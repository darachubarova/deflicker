"""Mask stabilization methods to reduce flickering."""

import numpy as np
from typing import List
from scipy.ndimage import median_filter as scipy_median


class MaskStabilizer:
    """
    Implements various temporal smoothing methods for mask stabilization.
    """
    
    @staticmethod
    def moving_average(
        masks: List[np.ndarray],
        window_size: int = 5
    ) -> List[np.ndarray]:
        """
        Apply moving average smoothing to masks.
        
        Args:
            masks: List of probability maps (float arrays)
            window_size: Size of the temporal window (must be odd)
            
        Returns:
            List of smoothed masks
        """
        if window_size % 2 == 0:
            raise ValueError("window_size must be odd")
        
        num_frames = len(masks)
        smoothed_masks = []
        half_window = window_size // 2
        
        for i in range(num_frames):
            # Determine window bounds
            start = max(0, i - half_window)
            end = min(num_frames, i + half_window + 1)
            
            # Get masks in window
            window_masks = masks[start:end]
            
            # Compute average
            avg_mask = np.mean(window_masks, axis=0).astype(np.float32)
            smoothed_masks.append(avg_mask)
        
        return smoothed_masks
    
    @staticmethod
    def median_filter(
        masks: List[np.ndarray],
        window_size: int = 5
    ) -> List[np.ndarray]:
        """
        Apply median filter smoothing to masks.
        
        Args:
            masks: List of probability maps (float arrays)
            window_size: Size of the temporal window (must be odd)
            
        Returns:
            List of smoothed masks
        """
        if window_size % 2 == 0:
            raise ValueError("window_size must be odd")
        
        num_frames = len(masks)
        smoothed_masks = []
        half_window = window_size // 2
        
        for i in range(num_frames):
            # Determine window bounds
            start = max(0, i - half_window)
            end = min(num_frames, i + half_window + 1)
            
            # Get masks in window
            window_masks = masks[start:end]
            
            # Compute median along temporal axis
            median_mask = np.median(window_masks, axis=0).astype(np.float32)
            smoothed_masks.append(median_mask)
        
        return smoothed_masks
    
    @staticmethod
    def exponential_smoothing(
        masks: List[np.ndarray],
        alpha: float = 0.3
    ) -> List[np.ndarray]:
        """
        Apply exponential smoothing to masks.
        
        Formula: smoothed[t] = alpha * original[t] + (1-alpha) * smoothed[t-1]
        
        Args:
            masks: List of probability maps (float arrays)
            alpha: Smoothing parameter (0 < alpha < 1)
                  - Higher alpha: more weight on current frame (less smoothing)
                  - Lower alpha: more weight on history (more smoothing)
            
        Returns:
            List of smoothed masks
        """
        if not 0 < alpha < 1:
            raise ValueError("alpha must be between 0 and 1")
        
        smoothed_masks = []
        
        # Initialize with first frame
        smoothed = masks[0].copy()
        smoothed_masks.append(smoothed)
        
        # Apply exponential smoothing
        for i in range(1, len(masks)):
            smoothed = alpha * masks[i] + (1 - alpha) * smoothed
            smoothed_masks.append(smoothed.astype(np.float32))
        
        return smoothed_masks
    
    @staticmethod
    def bilateral_temporal_filter(
        masks: List[np.ndarray],
        window_size: int = 5,
        sigma_temporal: float = 1.0,
        sigma_intensity: float = 0.1
    ) -> List[np.ndarray]:
        """
        Apply bilateral filter in temporal domain.
        
        Combines temporal proximity with intensity similarity.
        
        Args:
            masks: List of probability maps
            window_size: Size of temporal window
            sigma_temporal: Standard deviation for temporal Gaussian
            sigma_intensity: Standard deviation for intensity Gaussian
            
        Returns:
            List of smoothed masks
        """
        if window_size % 2 == 0:
            raise ValueError("window_size must be odd")
        
        num_frames = len(masks)
        smoothed_masks = []
        half_window = window_size // 2
        
        for i in range(num_frames):
            # Determine window bounds
            start = max(0, i - half_window)
            end = min(num_frames, i + half_window + 1)
            
            # Current frame
            current_mask = masks[i]
            
            # Compute weights
            weights = []
            window_masks = []
            
            for j in range(start, end):
                # Temporal distance
                temporal_dist = abs(j - i)
                temporal_weight = np.exp(-temporal_dist**2 / (2 * sigma_temporal**2))
                
                # Intensity distance
                intensity_dist = np.abs(masks[j] - current_mask)
                intensity_weight = np.exp(-intensity_dist**2 / (2 * sigma_intensity**2))
                
                # Combined weight
                weight = temporal_weight * intensity_weight
                weights.append(weight)
                window_masks.append(masks[j])
            
            # Normalize weights
            weights = np.array(weights)
            weights_sum = np.sum(weights, axis=0, keepdims=True)
            weights_sum = np.maximum(weights_sum, 1e-8)  # Avoid division by zero
            
            # Weighted average
            smoothed = np.sum(
                weights[:, None, None] * np.array(window_masks),
                axis=0
            ) / weights_sum[0]
            
            smoothed_masks.append(smoothed.astype(np.float32))
        
        return smoothed_masks
    
    @staticmethod
    def apply_method(
        masks: List[np.ndarray],
        method: str,
        **params
    ) -> List[np.ndarray]:
        """
        Apply a stabilization method by name.
        
        Args:
            masks: List of probability maps
            method: Method name ('moving_average', 'median_filter', 
                   'exponential_smoothing', 'bilateral_temporal')
            **params: Method-specific parameters
            
        Returns:
            List of smoothed masks
        """
        method_map = {
            'moving_average': MaskStabilizer.moving_average,
            'median_filter': MaskStabilizer.median_filter,
            'exponential_smoothing': MaskStabilizer.exponential_smoothing,
            'bilateral_temporal': MaskStabilizer.bilateral_temporal_filter,
        }
        
        if method not in method_map:
            raise ValueError(f"Unknown method: {method}")
        
        return method_map[method](masks, **params)
    
    @staticmethod
    def convert_to_binary(
        probability_maps: List[np.ndarray],
        threshold: float = 0.5
    ) -> List[np.ndarray]:
        """
        Convert probability maps to binary masks.
        
        Args:
            probability_maps: List of probability maps (float arrays)
            threshold: Threshold for binarization
            
        Returns:
            List of binary masks
        """
        return [(pm > threshold).astype(np.uint8) for pm in probability_maps]
