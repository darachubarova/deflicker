#!/usr/bin/env python
"""Quick test script to verify the system is set up correctly."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing module imports...")

try:
    from src import __version__
    print(f"✓ src package imported (version {__version__})")
except Exception as e:
    print(f"✗ Failed to import src: {e}")
    sys.exit(1)

try:
    from src.utils import extract_frames, save_mask_image, encode_image_base64
    print("✓ utils module imported")
except Exception as e:
    print(f"✗ Failed to import utils: {e}")
    sys.exit(1)

try:
    from src.metrics import calculate_iou, compare_stability
    print("✓ metrics module imported")
except Exception as e:
    print(f"✗ Failed to import metrics: {e}")
    sys.exit(1)

try:
    from src.stabilization import MaskStabilizer
    print("✓ stabilization module imported")
except Exception as e:
    print(f"✗ Failed to import stabilization: {e}")
    sys.exit(1)

try:
    # This will try to import torch which may not be installed yet
    from src.segmentation import VideoSegmenter
    print("✓ segmentation module imported")
except ImportError as e:
    print(f"⚠ segmentation module needs PyTorch (expected): {e}")
except Exception as e:
    print(f"✗ Failed to import segmentation: {e}")

try:
    # This will try to import FastAPI which may not be installed yet
    from src.main import app
    print("✓ main (FastAPI app) imported")
except ImportError as e:
    print(f"⚠ main module needs FastAPI (expected): {e}")
except Exception as e:
    print(f"✗ Failed to import main: {e}")

print("\n" + "="*60)
print("Module structure test completed!")
print("="*60)

# Test basic functionality
print("\nTesting basic functionality...")

import numpy as np
from src.metrics import calculate_iou

# Create test masks
mask1 = np.zeros((100, 100), dtype=np.uint8)
mask1[25:75, 25:75] = 1

mask2 = np.zeros((100, 100), dtype=np.uint8)
mask2[30:80, 30:80] = 1

iou = calculate_iou(mask1, mask2)
print(f"✓ IoU calculation works: {iou:.4f}")

# Test stabilization methods
from src.stabilization import MaskStabilizer

prob_maps = [np.random.rand(50, 50).astype(np.float32) for _ in range(10)]

smoothed_ma = MaskStabilizer.moving_average(prob_maps, window_size=3)
print(f"✓ Moving average works: {len(smoothed_ma)} frames")

smoothed_median = MaskStabilizer.median_filter(prob_maps, window_size=3)
print(f"✓ Median filter works: {len(smoothed_median)} frames")

smoothed_exp = MaskStabilizer.exponential_smoothing(prob_maps, alpha=0.3)
print(f"✓ Exponential smoothing works: {len(smoothed_exp)} frames")

print("\n" + "="*60)
print("All basic functionality tests passed!")
print("="*60)
print("\nNote: To run the full system, install dependencies:")
print("  pip install -r requirements.txt")
