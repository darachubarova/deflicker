"""Utility functions for video processing and image handling."""

import cv2
import numpy as np
import base64
from typing import List, Tuple
from pathlib import Path


def extract_frames(video_path: str) -> List[np.ndarray]:
    """
    Extract all frames from a video file.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        List of frames as numpy arrays (BGR format)
    """
    frames = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    
    cap.release()
    return frames


def get_video_info(video_path: str) -> dict:
    """
    Get video metadata.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary with video information
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    info = {
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    }
    
    cap.release()
    return info


def save_mask_image(mask: np.ndarray, path: str, colormap: int = cv2.COLORMAP_JET):
    """
    Save a mask as an image file with colormap.
    
    Args:
        mask: Mask array (either binary or probability map)
        path: Output file path
        colormap: OpenCV colormap to use
    """
    # Ensure mask is in [0, 255] range
    if mask.dtype == np.float32 or mask.dtype == np.float64:
        mask_uint8 = (mask * 255).astype(np.uint8)
    else:
        mask_uint8 = mask.astype(np.uint8)
    
    # Apply colormap for visualization
    colored_mask = cv2.applyColorMap(mask_uint8, colormap)
    
    cv2.imwrite(path, colored_mask)


def create_comparison_image(
    original: np.ndarray,
    mask_before: np.ndarray,
    mask_after: np.ndarray
) -> np.ndarray:
    """
    Create a side-by-side comparison image.
    
    Args:
        original: Original video frame
        mask_before: Mask before stabilization
        mask_after: Mask after stabilization
        
    Returns:
        Combined comparison image
    """
    # Resize images to same height if needed
    h, w = original.shape[:2]
    
    # Convert masks to colored versions
    if mask_before.dtype in [np.float32, np.float64]:
        mask_before_uint8 = (mask_before * 255).astype(np.uint8)
    else:
        mask_before_uint8 = mask_before.astype(np.uint8)
        
    if mask_after.dtype in [np.float32, np.float64]:
        mask_after_uint8 = (mask_after * 255).astype(np.uint8)
    else:
        mask_after_uint8 = mask_after.astype(np.uint8)
    
    colored_before = cv2.applyColorMap(mask_before_uint8, cv2.COLORMAP_JET)
    colored_after = cv2.applyColorMap(mask_after_uint8, cv2.COLORMAP_JET)
    
    # Resize masks to match original frame size
    colored_before = cv2.resize(colored_before, (w, h))
    colored_after = cv2.resize(colored_after, (w, h))
    
    # Add labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(original, 'Original', (10, 30), font, 1, (255, 255, 255), 2)
    cv2.putText(colored_before, 'Before Stabilization', (10, 30), font, 1, (255, 255, 255), 2)
    cv2.putText(colored_after, 'After Stabilization', (10, 30), font, 1, (255, 255, 255), 2)
    
    # Concatenate horizontally
    comparison = np.hstack([original, colored_before, colored_after])
    
    return comparison


def encode_image_base64(image: np.ndarray) -> str:
    """
    Encode an image as base64 string.
    
    Args:
        image: Image as numpy array
        
    Returns:
        Base64-encoded string
    """
    # Encode image to PNG format
    success, buffer = cv2.imencode('.png', image)
    if not success:
        raise ValueError("Failed to encode image")
    
    # Convert to base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return img_base64


def overlay_mask_on_frame(frame: np.ndarray, mask: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """
    Overlay a mask on a frame with transparency.
    
    Args:
        frame: Original frame
        mask: Mask to overlay (probability map or binary)
        alpha: Transparency level (0-1)
        
    Returns:
        Frame with overlay
    """
    # Ensure mask is in [0, 255] range
    if mask.dtype in [np.float32, np.float64]:
        mask_uint8 = (mask * 255).astype(np.uint8)
    else:
        mask_uint8 = mask.astype(np.uint8)
    
    # Apply colormap
    colored_mask = cv2.applyColorMap(mask_uint8, cv2.COLORMAP_JET)
    
    # Resize mask to match frame size if needed
    if colored_mask.shape[:2] != frame.shape[:2]:
        colored_mask = cv2.resize(colored_mask, (frame.shape[1], frame.shape[0]))
    
    # Blend
    overlay = cv2.addWeighted(frame, 1 - alpha, colored_mask, alpha, 0)
    
    return overlay


def create_triple_comparison_video(
    video_path: str,
    masks_before: List[np.ndarray],
    masks_after: List[np.ndarray],
    output_path: str
) -> str:
    """
    Create a video with three levels: original (top), mask before (middle), mask after (bottom).
    
    Args:
        video_path: Path to original video
        masks_before: List of masks before stabilization
        masks_after: List of masks after stabilization
        output_path: Path to save the output video
        
    Returns:
        Path to the created video
    """
    # Extract frames from original video
    frames = extract_frames(video_path)
    
    # Get video info
    video_info = get_video_info(video_path)
    fps = video_info['fps']
    
    # Determine dimensions
    frame_h, frame_w = frames[0].shape[:2]
    
    # Create video writer for vertical stacking
    # Output will be: frame_w x (frame_h * 3)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_w, frame_h * 3))
    
    if not out.isOpened():
        raise ValueError(f"Cannot create video writer at {output_path}")
    
    # Process each frame
    num_frames = min(len(frames), len(masks_before), len(masks_after))
    
    for i in range(num_frames):
        # Get original frame
        original = frames[i]
        
        # Convert masks to colored versions
        if masks_before[i].dtype in [np.float32, np.float64]:
            mask_before_uint8 = (masks_before[i] * 255).astype(np.uint8)
        else:
            mask_before_uint8 = masks_before[i].astype(np.uint8)
            
        if masks_after[i].dtype in [np.float32, np.float64]:
            mask_after_uint8 = (masks_after[i] * 255).astype(np.uint8)
        else:
            mask_after_uint8 = masks_after[i].astype(np.uint8)
        
        # Apply colormaps
        colored_before = cv2.applyColorMap(mask_before_uint8, cv2.COLORMAP_JET)
        colored_after = cv2.applyColorMap(mask_after_uint8, cv2.COLORMAP_JET)
        
        # Resize masks to match frame size
        colored_before = cv2.resize(colored_before, (frame_w, frame_h))
        colored_after = cv2.resize(colored_after, (frame_w, frame_h))
        
        # Add text labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        color = (255, 255, 255)
        thickness = 2
        
        cv2.putText(original, f'Original (Frame {i+1})', (10, 30), font, font_scale, color, thickness)
        cv2.putText(colored_before, f'Mask Before Stabilization (Frame {i+1})', (10, 30), font, font_scale, color, thickness)
        cv2.putText(colored_after, f'Mask After Stabilization (Frame {i+1})', (10, 30), font, font_scale, color, thickness)
        
        # Stack vertically
        combined = np.vstack([original, colored_before, colored_after])
        
        # Write frame
        out.write(combined)
    
    out.release()
    
    return output_path


def create_triple_comparison_video_sliced(
    frames: List[np.ndarray],
    masks_before: List[np.ndarray],
    masks_after: List[np.ndarray],
    output_path: str,
    fps: float = 30.0
) -> str:
    """
    Create a video with three levels from already extracted frames and masks.
    
    Args:
        frames: List of original video frames
        masks_before: List of masks before stabilization
        masks_after: List of masks after stabilization
        output_path: Path to save the output video
        fps: Frames per second for output video
        
    Returns:
        Path to the created video
    """
    if not frames or not masks_before or not masks_after:
        raise ValueError("Input frames and masks cannot be empty")
    
    # Determine dimensions
    frame_h, frame_w = frames[0].shape[:2]
    
    # Create video writer for vertical stacking
    # Output will be: frame_w x (frame_h * 3)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_w, frame_h * 3))
    
    if not out.isOpened():
        raise ValueError(f"Cannot create video writer at {output_path}")
    
    # Process each frame
    num_frames = min(len(frames), len(masks_before), len(masks_after))
    
    for i in range(num_frames):
        # Get original frame
        original = frames[i].copy()
        
        # Convert masks to colored versions
        if masks_before[i].dtype in [np.float32, np.float64]:
            mask_before_uint8 = (masks_before[i] * 255).astype(np.uint8)
        else:
            mask_before_uint8 = masks_before[i].astype(np.uint8)
            
        if masks_after[i].dtype in [np.float32, np.float64]:
            mask_after_uint8 = (masks_after[i] * 255).astype(np.uint8)
        else:
            mask_after_uint8 = masks_after[i].astype(np.uint8)
        
        # Apply colormaps
        colored_before = cv2.applyColorMap(mask_before_uint8, cv2.COLORMAP_JET)
        colored_after = cv2.applyColorMap(mask_after_uint8, cv2.COLORMAP_JET)
        
        # Resize masks to match frame size
        colored_before = cv2.resize(colored_before, (frame_w, frame_h))
        colored_after = cv2.resize(colored_after, (frame_w, frame_h))
        
        # Add text labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        color = (255, 255, 255)
        thickness = 2
        
        cv2.putText(original, f'Original (Frame {i+1})', (10, 30), font, font_scale, color, thickness)
        cv2.putText(colored_before, f'Mask Before Stabilization (Frame {i+1})', (10, 30), font, font_scale, color, thickness)
        cv2.putText(colored_after, f'Mask After Stabilization (Frame {i+1})', (10, 30), font, font_scale, color, thickness)
        
        # Stack vertically
        combined = np.vstack([original, colored_before, colored_after])
        
        # Write frame
        out.write(combined)
    
    out.release()
    
    return output_path
