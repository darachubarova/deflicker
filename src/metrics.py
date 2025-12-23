"""Metrics for evaluating mask stability."""

import numpy as np
from typing import List, Dict, Tuple


def calculate_iou(mask1: np.ndarray, mask2: np.ndarray) -> float:
    """
    Calculate Intersection over Union (IoU) between two masks.
    
    Args:
        mask1: First mask (binary or probability map)
        mask2: Second mask (binary or probability map)
        
    Returns:
        IoU score (0 to 1)
    """
    # Ensure masks are binary
    if mask1.dtype in [np.float32, np.float64]:
        mask1_bin = (mask1 > 0.5).astype(np.uint8)
    else:
        mask1_bin = (mask1 > 0).astype(np.uint8)
    
    if mask2.dtype in [np.float32, np.float64]:
        mask2_bin = (mask2 > 0.5).astype(np.uint8)
    else:
        mask2_bin = (mask2 > 0).astype(np.uint8)
    
    # Calculate intersection and union
    intersection = np.logical_and(mask1_bin, mask2_bin).sum()
    union = np.logical_or(mask1_bin, mask2_bin).sum()
    
    # Avoid division by zero
    if union == 0:
        return 1.0 if intersection == 0 else 0.0
    
    return float(intersection / union)


def calculate_dice(mask1: np.ndarray, mask2: np.ndarray) -> float:
    """
    Calculate Dice coefficient between two masks.
    
    Args:
        mask1: First mask
        mask2: Second mask
        
    Returns:
        Dice score (0 to 1)
    """
    # Ensure masks are binary
    if mask1.dtype in [np.float32, np.float64]:
        mask1_bin = (mask1 > 0.5).astype(np.uint8)
    else:
        mask1_bin = (mask1 > 0).astype(np.uint8)
    
    if mask2.dtype in [np.float32, np.float64]:
        mask2_bin = (mask2 > 0.5).astype(np.uint8)
    else:
        mask2_bin = (mask2 > 0).astype(np.uint8)
    
    intersection = np.logical_and(mask1_bin, mask2_bin).sum()
    
    # Avoid division by zero
    total = mask1_bin.sum() + mask2_bin.sum()
    if total == 0:
        return 1.0 if intersection == 0 else 0.0
    
    return float(2 * intersection / total)


def calculate_instability(masks: List[np.ndarray]) -> List[float]:
    """
    Calculate instability scores between consecutive frames.
    
    Instability = 1 - IoU (higher means more flickering)
    
    Args:
        masks: List of masks
        
    Returns:
        List of instability scores (one per frame transition)
    """
    instability_scores = []
    
    for i in range(len(masks) - 1):
        iou = calculate_iou(masks[i], masks[i + 1])
        instability = 1.0 - iou
        instability_scores.append(instability)
    
    return instability_scores


def calculate_temporal_consistency(masks: List[np.ndarray]) -> List[float]:
    """
    Calculate temporal consistency (IoU) between consecutive frames.
    
    Args:
        masks: List of masks
        
    Returns:
        List of IoU scores between consecutive frames
    """
    consistency_scores = []
    
    for i in range(len(masks) - 1):
        iou = calculate_iou(masks[i], masks[i + 1])
        consistency_scores.append(iou)
    
    return consistency_scores


def compare_stability(
    masks_before: List[np.ndarray],
    masks_after: List[np.ndarray]
) -> Dict[str, any]:
    """
    Compare stability metrics before and after stabilization.
    
    Args:
        masks_before: Masks before stabilization
        masks_after: Masks after stabilization
        
    Returns:
        Dictionary with comparison metrics
    """
    # Calculate instability for both
    instability_before = calculate_instability(masks_before)
    instability_after = calculate_instability(masks_after)
    
    # Calculate IoU for both
    iou_before = calculate_temporal_consistency(masks_before)
    iou_after = calculate_temporal_consistency(masks_after)
    
    # Compute statistics
    results = {
        'instability_before': {
            'mean': float(np.mean(instability_before)),
            'median': float(np.median(instability_before)),
            'std': float(np.std(instability_before)),
            'min': float(np.min(instability_before)),
            'max': float(np.max(instability_before)),
            'scores': [float(x) for x in instability_before]
        },
        'instability_after': {
            'mean': float(np.mean(instability_after)),
            'median': float(np.median(instability_after)),
            'std': float(np.std(instability_after)),
            'min': float(np.min(instability_after)),
            'max': float(np.max(instability_after)),
            'scores': [float(x) for x in instability_after]
        },
        'iou_before': {
            'mean': float(np.mean(iou_before)),
            'median': float(np.median(iou_before)),
            'std': float(np.std(iou_before)),
            'min': float(np.min(iou_before)),
            'max': float(np.max(iou_before)),
            'scores': [float(x) for x in iou_before]
        },
        'iou_after': {
            'mean': float(np.mean(iou_after)),
            'median': float(np.median(iou_after)),
            'std': float(np.std(iou_after)),
            'min': float(np.min(iou_after)),
            'max': float(np.max(iou_after)),
            'scores': [float(x) for x in iou_after]
        },
        'improvement': {
            'instability_reduction': float(
                np.mean(instability_before) - np.mean(instability_after)
            ),
            'instability_reduction_percent': float(
                100 * (np.mean(instability_before) - np.mean(instability_after)) / 
                (np.mean(instability_before) + 1e-8)
            ),
            'iou_improvement': float(
                np.mean(iou_after) - np.mean(iou_before)
            ),
            'iou_improvement_percent': float(
                100 * (np.mean(iou_after) - np.mean(iou_before)) / 
                (np.mean(iou_before) + 1e-8)
            )
        }
    }
    
    return results


def calculate_mask_statistics(masks: List[np.ndarray]) -> Dict[str, any]:
    """
    Calculate various statistics for a sequence of masks.
    
    Args:
        masks: List of masks
        
    Returns:
        Dictionary with mask statistics
    """
    # Calculate area (percentage of frame that is foreground)
    areas = []
    for mask in masks:
        if mask.dtype in [np.float32, np.float64]:
            mask_bin = (mask > 0.5).astype(np.uint8)
        else:
            mask_bin = (mask > 0).astype(np.uint8)
        area_percent = 100 * mask_bin.sum() / mask_bin.size
        areas.append(area_percent)
    
    # Calculate temporal consistency
    consistency = calculate_temporal_consistency(masks)
    
    return {
        'num_frames': len(masks),
        'area': {
            'mean': float(np.mean(areas)),
            'std': float(np.std(areas)),
            'min': float(np.min(areas)),
            'max': float(np.max(areas)),
        },
        'temporal_consistency': {
            'mean': float(np.mean(consistency)),
            'std': float(np.std(consistency)),
            'min': float(np.min(consistency)),
            'max': float(np.max(consistency)),
        }
    }
