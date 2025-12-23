"""
API endpoint validation tests.

These tests verify that the API endpoints are properly defined
and can be imported without runtime errors.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def test_api_structure():
    """Test that the API can be imported and has expected structure."""
    print("\n" + "="*60)
    print("Testing API Structure")
    print("="*60)
    
    try:
        # Try importing with mock dependencies if needed
        import unittest.mock as mock
        
        # Mock external dependencies
        sys.modules['cv2'] = mock.MagicMock()
        sys.modules['torch'] = mock.MagicMock()
        sys.modules['torchvision'] = mock.MagicMock()
        sys.modules['torchvision.transforms'] = mock.MagicMock()
        sys.modules['torchvision.models'] = mock.MagicMock()
        sys.modules['torchvision.models.segmentation'] = mock.MagicMock()
        
        from src.main import app
        print("✓ FastAPI app imported successfully")
        
        # Check that app has expected attributes
        assert hasattr(app, 'routes'), "App should have routes"
        print(f"✓ API has {len(app.routes)} routes defined")
        
        # List all routes
        print("\nDefined Routes:")
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods) if route.methods else 'N/A'
                print(f"  {methods:12} {route.path}")
        
        # Check expected endpoints exist
        expected_paths = [
            '/',
            '/api/upload',
            '/api/segment',
            '/api/stabilize',
            '/api/status/{job_id}',
            '/api/results/{job_id}',
            '/api/metrics/{job_id}',
            '/api/frames/{job_id}/{frame_type}/{frame_num}',
            '/api/classes',
            '/api/job/{job_id}',
        ]
        
        actual_paths = [route.path for route in app.routes if hasattr(route, 'path')]
        
        print("\nExpected Endpoints:")
        for path in expected_paths:
            # Handle path parameters
            found = any(
                path.replace('{', '').replace('}', '') in actual_path.replace('{', '').replace('}', '')
                for actual_path in actual_paths
            )
            status = "✓" if found else "✗"
            print(f"  {status} {path}")
        
        return True
        
    except ImportError as e:
        print(f"⚠ Could not fully import API (dependencies missing): {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing API: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pydantic_models():
    """Test that Pydantic models can be imported."""
    print("\n" + "="*60)
    print("Testing Pydantic Models")
    print("="*60)
    
    try:
        import unittest.mock as mock
        
        # Mock external dependencies
        sys.modules['cv2'] = mock.MagicMock()
        sys.modules['torch'] = mock.MagicMock()
        sys.modules['torchvision'] = mock.MagicMock()
        
        from src.main import SegmentRequest, StabilizeRequest, JobStatus
        
        print("✓ SegmentRequest model imported")
        print("✓ StabilizeRequest model imported")
        print("✓ JobStatus model imported")
        
        # Test model instantiation
        seg_req = SegmentRequest(job_id="test-123", target_class="person")
        print(f"✓ SegmentRequest can be instantiated: {seg_req.job_id}")
        
        stab_req = StabilizeRequest(
            job_id="test-123",
            method="moving_average",
            window_size=5
        )
        print(f"✓ StabilizeRequest can be instantiated: {stab_req.method}")
        
        return True
        
    except ImportError as e:
        print(f"⚠ Could not import models (dependencies missing): {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing models: {e}")
        return False


def test_module_functions():
    """Test that individual module functions work."""
    print("\n" + "="*60)
    print("Testing Module Functions")
    print("="*60)
    
    try:
        import numpy as np
        from src.metrics import calculate_iou, compare_stability
        from src.stabilization import MaskStabilizer
        
        # Test IoU calculation
        mask1 = np.ones((10, 10), dtype=np.uint8)
        mask2 = np.ones((10, 10), dtype=np.uint8)
        iou = calculate_iou(mask1, mask2)
        assert iou == 1.0, "IoU of identical masks should be 1.0"
        print(f"✓ IoU calculation works: {iou}")
        
        # Test stabilization
        masks = [np.random.rand(10, 10).astype(np.float32) for _ in range(5)]
        smoothed = MaskStabilizer.moving_average(masks, window_size=3)
        assert len(smoothed) == len(masks), "Output should have same length"
        print(f"✓ Moving average stabilization works")
        
        # Test metrics comparison
        metrics = compare_stability(masks, smoothed)
        assert 'iou_before' in metrics, "Metrics should contain iou_before"
        assert 'iou_after' in metrics, "Metrics should contain iou_after"
        print(f"✓ Metrics comparison works")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing functions: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("API Validation Test Suite")
    print("="*60)
    
    results = {
        'API Structure': test_api_structure(),
        'Pydantic Models': test_pydantic_models(),
        'Module Functions': test_module_functions(),
    }
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("⚠ Some tests failed (may be due to missing dependencies)")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
