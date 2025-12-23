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
