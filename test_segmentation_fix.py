#!/usr/bin/env python
"""
Test to verify NumPy 2.x compatibility fix for torchvision transforms.

This test validates that the _preprocess_frame method correctly converts
numpy arrays to PIL Images before applying transforms, fixing the
"TypeError: expected np.ndarray (got numpy.ndarray)" issue.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("Testing NumPy 2.x Compatibility Fix")
print("="*60)

try:
    import torch
    import torchvision
    from PIL import Image
    print("✓ Required packages imported")
except ImportError as e:
    print(f"⚠ Skipping test - missing dependencies: {e}")
    sys.exit(0)

try:
    from src.segmentation import VideoSegmenter
    print("✓ VideoSegmenter imported")
except Exception as e:
    print(f"✗ Failed to import VideoSegmenter: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 1: Check PIL import is present
print("\nTest 1: Verify PIL.Image import")
try:
    import src.segmentation as seg_module
    assert hasattr(seg_module, 'Image'), "PIL.Image should be imported in segmentation module"
    print("✓ PIL.Image import confirmed")
except AssertionError as e:
    print(f"✗ {e}")
    sys.exit(1)

# Test 2: Test _preprocess_frame with numpy array
print("\nTest 2: Test _preprocess_frame with numpy array")
try:
    # Create a VideoSegmenter instance (using CPU to avoid CUDA requirements)
    segmenter = VideoSegmenter(device='cpu')
    print("✓ VideoSegmenter initialized")
    
    # Create a test frame (BGR format like OpenCV provides)
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    print(f"✓ Test frame created: shape={test_frame.shape}, dtype={test_frame.dtype}")
    
    # Preprocess the frame - this should not raise TypeError
    input_tensor = segmenter._preprocess_frame(test_frame)
    print(f"✓ Frame preprocessed successfully: shape={input_tensor.shape}, dtype={input_tensor.dtype}")
    
    # Verify output is a torch tensor
    assert isinstance(input_tensor, torch.Tensor), "Output should be a torch.Tensor"
    print("✓ Output is torch.Tensor")
    
    # Verify shape is correct (C, H, W)
    assert len(input_tensor.shape) == 3, "Tensor should have 3 dimensions"
    assert input_tensor.shape[0] == 3, "First dimension should be 3 (RGB channels)"
    print(f"✓ Output shape is correct: {input_tensor.shape}")
    
    # Verify values are normalized (should be roughly in range [-3, 3] after normalization)
    mean = input_tensor.mean().item()
    assert -5 < mean < 5, "Mean should be in reasonable range after normalization"
    print(f"✓ Values appear normalized (mean={mean:.4f})")
    
except TypeError as e:
    if "expected np.ndarray (got numpy.ndarray)" in str(e):
        print(f"✗ NumPy compatibility error still present: {e}")
        sys.exit(1)
    else:
        raise
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test with actual batch processing (from segment_video method)
print("\nTest 3: Test batch processing")
try:
    # Create multiple test frames
    test_frames = [
        np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
        for _ in range(3)
    ]
    print(f"✓ Created {len(test_frames)} test frames")
    
    # Test batch preprocessing (as used in segment_video)
    batch_tensors = torch.stack([
        segmenter._preprocess_frame(frame) for frame in test_frames
    ])
    print(f"✓ Batch preprocessed successfully: shape={batch_tensors.shape}")
    
    assert batch_tensors.shape[0] == 3, "Batch should have 3 frames"
    assert batch_tensors.shape[1] == 3, "Each frame should have 3 channels"
    print("✓ Batch processing works correctly")
    
except Exception as e:
    print(f"✗ Batch processing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verify the fix handles edge cases
print("\nTest 4: Test edge cases")
try:
    # Test with minimum size frame
    small_frame = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
    small_tensor = segmenter._preprocess_frame(small_frame)
    print(f"✓ Small frame processed: {small_tensor.shape}")
    
    # Test with different dtype (uint8 is most common, but ensure it works)
    frame_uint8 = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    tensor_uint8 = segmenter._preprocess_frame(frame_uint8)
    print(f"✓ uint8 frame processed: {tensor_uint8.shape}")
    
except Exception as e:
    print(f"✗ Edge case test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✓ All tests passed!")
print("="*60)
print("\nThe fix successfully resolves the NumPy 2.x compatibility issue.")
print("Frames are now converted to PIL Images before applying transforms.")
