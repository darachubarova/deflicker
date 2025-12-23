#!/usr/bin/env python
"""
Standalone example demonstrating mask stabilization algorithms.

This example uses synthetic data and doesn't require PyTorch or OpenCV.
It demonstrates the core stabilization algorithms and metrics calculation.
"""

import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.stabilization import MaskStabilizer
from src.metrics import compare_stability, calculate_mask_statistics


def generate_synthetic_masks(num_frames=50, size=(100, 100), noise_level=0.3):
    """
    Generate synthetic probability masks with artificial flickering.
    
    Simulates a moving object with random noise to create flickering effect.
    """
    masks = []
    
    for i in range(num_frames):
        # Create base mask (moving circle)
        mask = np.zeros(size, dtype=np.float32)
        
        # Circle parameters (moving horizontally)
        center_x = int(size[1] * 0.3 + (size[1] * 0.4) * (i / num_frames))
        center_y = size[0] // 2
        radius = 20
        
        # Create circle
        y, x = np.ogrid[:size[0], :size[1]]
        circle_mask = ((x - center_x)**2 + (y - center_y)**2) <= radius**2
        mask[circle_mask] = 1.0
        
        # Add Gaussian noise to simulate flickering
        noise = np.random.normal(0, noise_level, size).astype(np.float32)
        mask = np.clip(mask + noise, 0, 1)
        
        masks.append(mask)
    
    return masks


def print_metrics(metrics, method_name=""):
    """Print metrics in a readable format."""
    if method_name:
        print(f"\n{'='*60}")
        print(f"Method: {method_name}")
        print(f"{'='*60}")
    
    print(f"\nIoU Before Stabilization:")
    print(f"  Mean:   {metrics['iou_before']['mean']:.4f}")
    print(f"  Std:    {metrics['iou_before']['std']:.4f}")
    print(f"  Min:    {metrics['iou_before']['min']:.4f}")
    print(f"  Max:    {metrics['iou_before']['max']:.4f}")
    
    print(f"\nIoU After Stabilization:")
    print(f"  Mean:   {metrics['iou_after']['mean']:.4f}")
    print(f"  Std:    {metrics['iou_after']['std']:.4f}")
    print(f"  Min:    {metrics['iou_after']['min']:.4f}")
    print(f"  Max:    {metrics['iou_after']['max']:.4f}")
    
    print(f"\nImprovement:")
    print(f"  IoU improvement:        {metrics['improvement']['iou_improvement']:.4f}")
    print(f"  IoU improvement (%):    {metrics['improvement']['iou_improvement_percent']:.2f}%")
    print(f"  Instability reduction:  {metrics['improvement']['instability_reduction']:.4f}")
    print(f"  Instability reduction (%): {metrics['improvement']['instability_reduction_percent']:.2f}%")


def main():
    print("="*60)
    print("Mask Stabilization - Standalone Example")
    print("="*60)
    
    # Generate synthetic masks with flickering
    print("\nGenerating synthetic masks with artificial flickering...")
    masks_original = generate_synthetic_masks(
        num_frames=50,
        size=(100, 100),
        noise_level=0.3
    )
    print(f"✓ Generated {len(masks_original)} masks")
    
    # Calculate statistics for original masks
    print("\nOriginal Mask Statistics:")
    stats = calculate_mask_statistics(masks_original)
    print(f"  Frame count: {stats['num_frames']}")
    print(f"  Mean area: {stats['area']['mean']:.2f}%")
    print(f"  Temporal consistency (mean IoU): {stats['temporal_consistency']['mean']:.4f}")
    print(f"  Temporal consistency (std): {stats['temporal_consistency']['std']:.4f}")
    
    # Test all stabilization methods
    methods = [
        ('Moving Average (window=5)', 'moving_average', {'window_size': 5}),
        ('Median Filter (window=5)', 'median_filter', {'window_size': 5}),
        ('Exponential Smoothing (alpha=0.3)', 'exponential_smoothing', {'alpha': 0.3}),
    ]
    
    results = {}
    
    for method_name, method_id, params in methods:
        print(f"\n{'='*60}")
        print(f"Testing: {method_name}")
        print(f"{'='*60}")
        
        # Apply stabilization
        masks_stabilized = MaskStabilizer.apply_method(
            masks_original,
            method_id,
            **params
        )
        print(f"✓ Stabilization applied")
        
        # Calculate metrics
        metrics = compare_stability(masks_original, masks_stabilized)
        results[method_name] = metrics
        
        print_metrics(metrics)
    
    # Summary comparison
    print("\n" + "="*60)
    print("SUMMARY: Comparison of All Methods")
    print("="*60)
    
    print("\n{:<40} {:>10} {:>10}".format("Method", "Mean IoU", "Improvement"))
    print("-"*60)
    
    for method_name, metrics in results.items():
        mean_iou = metrics['iou_after']['mean']
        improvement = metrics['improvement']['iou_improvement_percent']
        print("{:<40} {:>10.4f} {:>9.2f}%".format(
            method_name, mean_iou, improvement
        ))
    
    # Find best method
    best_method = max(results.items(), 
                     key=lambda x: x[1]['improvement']['iou_improvement'])
    
    print("\n" + "="*60)
    print(f"Best Method: {best_method[0]}")
    print(f"IoU Improvement: {best_method[1]['improvement']['iou_improvement']:.4f}")
    print(f"Improvement: {best_method[1]['improvement']['iou_improvement_percent']:.2f}%")
    print("="*60)
    
    print("\n✓ Example completed successfully!")
    print("\nThis demonstrates that the stabilization algorithms work correctly.")
    print("For real video processing, install all dependencies and use the API server.")


if __name__ == '__main__':
    main()
