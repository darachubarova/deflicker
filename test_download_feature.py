#!/usr/bin/env python
"""Test script for the new download-video functionality."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import create_triple_comparison_video_sliced
import numpy as np
import cv2


def test_create_triple_comparison_video_sliced():
    """Test the create_triple_comparison_video_sliced function."""
    print("Testing create_triple_comparison_video_sliced...")
    
    # Create test data
    frame_height, frame_width = 480, 640
    num_frames = 10
    fps = 30.0
    
    # Generate synthetic frames
    frames = [
        np.random.randint(0, 255, (frame_height, frame_width, 3), dtype=np.uint8)
        for _ in range(num_frames)
    ]
    
    # Generate synthetic masks (0-1 float)
    masks_before = [
        np.random.rand(frame_height, frame_width).astype(np.float32)
        for _ in range(num_frames)
    ]
    
    masks_after = [
        np.random.rand(frame_height, frame_width).astype(np.float32)
        for _ in range(num_frames)
    ]
    
    # Create output directory
    output_dir = Path("results/test_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(output_dir / "test_comparison.mp4")
    
    try:
        # Call the function
        result = create_triple_comparison_video_sliced(
            frames=frames,
            masks_before=masks_before,
            masks_after=masks_after,
            output_path=output_path,
            fps=fps
        )
        
        # Verify output
        output_file = Path(result)
        if output_file.exists() and output_file.stat().st_size > 0:
            print(f"✅ Video created successfully: {output_path}")
            print(f"   File size: {output_file.stat().st_size} bytes")
            print(f"   Expected dimensions: {frame_width} x {frame_height * 3}")
            print(f"   Expected FPS: {fps}")
            return True
        else:
            print(f"❌ Video file not created or empty")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_models():
    """Test that the Pydantic models are correctly defined."""
    print("\nTesting API models...")
    
    try:
        from src.main import DownloadVideoRequest
        
        # Test with all parameters
        request1 = DownloadVideoRequest(
            job_id="test-job-id",
            frame_range_start=0,
            frame_range_end=100
        )
        print(f"✅ DownloadVideoRequest with all params: {request1.dict()}")
        
        # Test with only job_id
        request2 = DownloadVideoRequest(job_id="test-job-id-2")
        print(f"✅ DownloadVideoRequest with only job_id: {request2.dict()}")
        
        # Test optional parameters
        request3 = DownloadVideoRequest(
            job_id="test-job-id-3",
            frame_range_start=50
        )
        print(f"✅ DownloadVideoRequest with partial params: {request3.dict()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing new download-video functionality")
    print("=" * 60)
    
    results = []
    
    # Test 1: API models
    results.append(("API Models", test_api_models()))
    
    # Test 2: Video creation
    results.append(("Video Creation", test_create_triple_comparison_video_sliced()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
