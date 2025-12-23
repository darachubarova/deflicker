"""FastAPI server for mask stabilization."""

import os
import uuid
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import asyncio

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import cv2

from .segmentation import VideoSegmenter
from .stabilization import MaskStabilizer
from .metrics import compare_stability, calculate_mask_statistics
from .utils import (
    extract_frames,
    get_video_info,
    save_mask_image,
    create_comparison_image,
    encode_image_base64,
    overlay_mask_on_frame
)


# Initialize FastAPI app
app = FastAPI(
    title="Mask Stabilization API",
    description="API for video segmentation and mask stabilization",
    version="1.0.0"
)

# Configure CORS for GitHub Spark
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage directories
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "results" / "uploads"
RESULTS_DIR = BASE_DIR / "results" / "outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# In-memory job storage
jobs: Dict[str, Dict] = {}

# Global segmenter instance
segmenter = None


def get_segmenter():
    """Get or create the global segmenter instance."""
    global segmenter
    if segmenter is None:
        segmenter = VideoSegmenter()
    return segmenter


# Pydantic models
class SegmentRequest(BaseModel):
    job_id: str
    target_class: Optional[str] = None


class StabilizeRequest(BaseModel):
    job_id: str
    method: str  # 'moving_average', 'median_filter', 'exponential_smoothing'
    window_size: Optional[int] = 5
    alpha: Optional[float] = 0.3


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    message: str


# Helper functions
def save_job_state(job_id: str):
    """Save job state to disk."""
    job_dir = RESULTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    state_file = job_dir / "state.json"
    with open(state_file, 'w') as f:
        # Create serializable version of job data
        job_data = jobs[job_id].copy()
        # Remove non-serializable items
        job_data.pop('frames', None)
        job_data.pop('masks_before', None)
        job_data.pop('masks_after', None)
        job_data.pop('binary_masks', None)
        json.dump(job_data, f, indent=2)


def load_job_state(job_id: str) -> bool:
    """Load job state from disk."""
    job_dir = RESULTS_DIR / job_id
    state_file = job_dir / "state.json"
    
    if not state_file.exists():
        return False
    
    with open(state_file, 'r') as f:
        jobs[job_id] = json.load(f)
    
    return True


def process_segmentation(job_id: str, target_class: Optional[int]):
    """Background task to process segmentation."""
    try:
        job = jobs[job_id]
        job['status'] = 'segmenting'
        job['progress'] = 0.1
        job['message'] = 'Extracting frames...'
        
        # Extract frames
        video_path = job['video_path']
        frames = extract_frames(video_path)
        job['frames'] = frames
        job['num_frames'] = len(frames)
        
        job['progress'] = 0.3
        job['message'] = f'Segmenting {len(frames)} frames...'
        
        # Segment video
        seg = get_segmenter()
        binary_masks, prob_maps = seg.segment_video(frames, target_class=target_class)
        
        job['masks_before'] = prob_maps
        job['binary_masks'] = binary_masks
        
        # Save masks to disk
        job_dir = RESULTS_DIR / job_id
        masks_dir = job_dir / "masks_before"
        masks_dir.mkdir(parents=True, exist_ok=True)
        
        for i, mask in enumerate(prob_maps):
            mask_path = masks_dir / f"mask_{i:04d}.png"
            save_mask_image(mask, str(mask_path))
        
        job['progress'] = 1.0
        job['status'] = 'segmented'
        job['message'] = 'Segmentation complete'
        
        save_job_state(job_id)
        
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['message'] = str(e)


def process_stabilization(job_id: str, method: str, params: dict):
    """Background task to process stabilization."""
    try:
        job = jobs[job_id]
        job['status'] = 'stabilizing'
        job['progress'] = 0.1
        job['message'] = f'Applying {method}...'
        
        # Get masks
        masks_before = job['masks_before']
        
        # Apply stabilization
        masks_after = MaskStabilizer.apply_method(masks_before, method, **params)
        job['masks_after'] = masks_after
        
        job['progress'] = 0.5
        job['message'] = 'Calculating metrics...'
        
        # Calculate metrics
        metrics = compare_stability(masks_before, masks_after)
        job['metrics'] = metrics
        
        # Save stabilized masks
        job_dir = RESULTS_DIR / job_id
        masks_dir = job_dir / "masks_after"
        masks_dir.mkdir(parents=True, exist_ok=True)
        
        for i, mask in enumerate(masks_after):
            mask_path = masks_dir / f"mask_{i:04d}.png"
            save_mask_image(mask, str(mask_path))
        
        # Save comparison images
        comp_dir = job_dir / "comparisons"
        comp_dir.mkdir(parents=True, exist_ok=True)
        
        frames = job['frames']
        for i in range(min(len(frames), len(masks_before), len(masks_after))):
            comp_img = create_comparison_image(
                frames[i],
                masks_before[i],
                masks_after[i]
            )
            comp_path = comp_dir / f"comparison_{i:04d}.png"
            cv2.imwrite(str(comp_path), comp_img)
        
        job['progress'] = 1.0
        job['status'] = 'completed'
        job['message'] = 'Stabilization complete'
        job['stabilization_method'] = method
        job['stabilization_params'] = params
        
        save_job_state(job_id)
        
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['message'] = str(e)


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mask Stabilization API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/upload",
            "segment": "POST /api/segment",
            "stabilize": "POST /api/stabilize",
            "results": "GET /api/results/{job_id}",
            "metrics": "GET /api/metrics/{job_id}",
            "frames": "GET /api/frames/{job_id}/{frame_type}/{frame_num}"
        }
    }


@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file.
    
    Returns:
        job_id for tracking the processing
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    video_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    with open(video_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Get video info
    try:
        video_info = get_video_info(str(video_path))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid video file: {str(e)}")
    
    # Create job
    jobs[job_id] = {
        'job_id': job_id,
        'status': 'uploaded',
        'progress': 0.0,
        'message': 'Video uploaded successfully',
        'video_path': str(video_path),
        'video_info': video_info,
        'filename': file.filename
    }
    
    save_job_state(job_id)
    
    return {
        'job_id': job_id,
        'status': 'uploaded',
        'video_info': video_info
    }


@app.post("/api/segment")
async def segment_video(request: SegmentRequest, background_tasks: BackgroundTasks):
    """
    Start video segmentation.
    """
    job_id = request.job_id
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job['status'] not in ['uploaded', 'segmented']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot segment video in status: {job['status']}"
        )
    
    # Get target class ID if specified
    target_class = None
    if request.target_class:
        target_class = VideoSegmenter.get_class_id(request.target_class)
        if target_class is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown class: {request.target_class}"
            )
    
    # Start background task
    background_tasks.add_task(process_segmentation, job_id, target_class)
    
    return {
        'job_id': job_id,
        'status': 'queued',
        'message': 'Segmentation started'
    }


@app.post("/api/stabilize")
async def stabilize_masks(request: StabilizeRequest, background_tasks: BackgroundTasks):
    """
    Apply mask stabilization.
    """
    job_id = request.job_id
    
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job['status'] not in ['segmented', 'completed']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot stabilize in status: {job['status']}"
        )
    
    # Validate method and parameters
    valid_methods = ['moving_average', 'median_filter', 'exponential_smoothing', 'bilateral_temporal']
    if request.method not in valid_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid method. Must be one of: {valid_methods}"
        )
    
    # Prepare parameters
    params = {}
    if request.method in ['moving_average', 'median_filter']:
        params['window_size'] = request.window_size or 5
    elif request.method == 'exponential_smoothing':
        params['alpha'] = request.alpha or 0.3
    elif request.method == 'bilateral_temporal':
        params['window_size'] = request.window_size or 5
    
    # Start background task
    background_tasks.add_task(process_stabilization, job_id, request.method, params)
    
    return {
        'job_id': job_id,
        'status': 'queued',
        'message': 'Stabilization started'
    }


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """
    Get job status.
    """
    if job_id not in jobs:
        # Try to load from disk
        if not load_job_state(job_id):
            raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    return {
        'job_id': job_id,
        'status': job['status'],
        'progress': job.get('progress', 0.0),
        'message': job.get('message', '')
    }


@app.get("/api/results/{job_id}")
async def get_results(job_id: str):
    """
    Get job results summary.
    """
    if job_id not in jobs:
        if not load_job_state(job_id):
            raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # Create response without large arrays
    response = {
        'job_id': job_id,
        'status': job['status'],
        'video_info': job.get('video_info', {}),
        'num_frames': job.get('num_frames', 0),
        'filename': job.get('filename', ''),
    }
    
    if 'stabilization_method' in job:
        response['stabilization'] = {
            'method': job['stabilization_method'],
            'params': job['stabilization_params']
        }
    
    return response


@app.get("/api/metrics/{job_id}")
async def get_metrics(job_id: str):
    """
    Get stability metrics.
    """
    if job_id not in jobs:
        if not load_job_state(job_id):
            raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if 'metrics' not in job:
        raise HTTPException(
            status_code=400,
            detail="Metrics not available. Run stabilization first."
        )
    
    return job['metrics']


@app.get("/api/frames/{job_id}/{frame_type}/{frame_num}")
async def get_frame(job_id: str, frame_type: str, frame_num: int):
    """
    Get a specific frame image.
    
    frame_type: 'original', 'mask_before', 'mask_after', 'comparison'
    """
    job_dir = RESULTS_DIR / job_id
    
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    if frame_type == 'mask_before':
        img_path = job_dir / "masks_before" / f"mask_{frame_num:04d}.png"
    elif frame_type == 'mask_after':
        img_path = job_dir / "masks_after" / f"mask_{frame_num:04d}.png"
    elif frame_type == 'comparison':
        img_path = job_dir / "comparisons" / f"comparison_{frame_num:04d}.png"
    else:
        raise HTTPException(status_code=400, detail="Invalid frame_type")
    
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Frame not found")
    
    return FileResponse(img_path)


@app.get("/api/classes")
async def get_classes():
    """
    Get available segmentation classes.
    """
    return VideoSegmenter.get_available_classes()


@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its data.
    """
    # Remove from memory
    if job_id in jobs:
        del jobs[job_id]
    
    # Remove from disk
    job_dir = RESULTS_DIR / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
    
    # Remove uploaded video
    for file in UPLOAD_DIR.glob(f"{job_id}_*"):
        file.unlink()
    
    return {'message': 'Job deleted successfully'}

# Serve frontend
from fastapi.staticfiles import StaticFiles
from pathlib import Path

frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
