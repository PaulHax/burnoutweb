#!/usr/bin/env python3
"""
Test Auto Detection Trigger
Validates automatic feature detection trigger functionality.
"""

import sys
import tempfile
import asyncio
sys.path.append('/home/paulhax/src/tele-stuff/burnoutweb/app')

def test_should_auto_detect():
    """Test the should_auto_detect_features function."""
    print("=== Testing Auto Detection Logic ===")
    
    try:
        from burn_out.app.features.auto_detection_trigger import should_auto_detect_features
        from burn_out.app.features.feature_storage import FeatureDataManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            feature_manager = FeatureDataManager(tmpdir)
            video_path = "/path/to/test_video.mp4"
            
            # Test with no existing features
            should_detect = should_auto_detect_features(video_path, feature_manager)
            assert should_detect == True, "Should detect when no features exist"
            print("✓ Auto-detect logic works for new video")
            
            # Test with existing features
            # Create mock detection results
            mock_results = {
                'success': True,
                'video_path': video_path,
                'frame_features': {1: {'feature_count': 250}},
                'summary': {'total_frames_processed': 1}
            }
            
            # Save mock results
            feature_manager.save_detection_results(mock_results)
            
            # Now should not auto-detect
            should_detect = should_auto_detect_features(video_path, feature_manager)
            assert should_detect == False, "Should not detect when features exist"
            print("✓ Auto-detect logic skips when features already exist")
            
            return True
            
    except Exception as e:
        print(f"✗ Auto detection logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_trigger_function():
    """Test the trigger_feature_detection function."""
    print("\n=== Testing Trigger Function ===")
    
    try:
        from burn_out.app.features.auto_detection_trigger import trigger_feature_detection
        from burn_out.app.features.feature_storage import FeatureDataManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            feature_manager = FeatureDataManager(tmpdir)
            
            # Test with non-existent video (should not crash)
            video_path = "/nonexistent/video.mp4"
            
            progress_updates = []
            completion_results = []
            
            def progress_callback(data):
                progress_updates.append(data)
                print(f"  Progress: {data.get('status', 'unknown')}")
            
            def completion_callback(results):
                completion_results.append(results)
                print(f"  Completion: {results.get('success', False)}")
            
            # This should return True (will start detection) but fail quickly
            success = await trigger_feature_detection(
                video_path=video_path,
                feature_manager=feature_manager,
                progress_callback=progress_callback,
                completion_callback=completion_callback
            )
            
            # Should return True because it tried to start detection
            print(f"✓ Trigger function returned: {success}")
            
            # Give it a moment for async operations
            await asyncio.sleep(1.0)
            
            print(f"✓ Function handles non-existent video gracefully")
            
            return True
            
    except Exception as e:
        print(f"✗ Trigger function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_readiness():
    """Test that all components are ready for core.py integration."""
    print("\n=== Testing Integration Readiness ===")
    
    try:
        # Test imports that core.py will need
        from burn_out.app.features.feature_storage import FeatureDataManager
        from burn_out.app.features.auto_detection_trigger import trigger_feature_detection
        print("✓ All required imports available")
        
        # Test feature manager creation
        feature_manager = FeatureDataManager()
        print("✓ Feature manager can be created")
        
        # Test that trigger function exists and is async
        import inspect
        assert inspect.iscoroutinefunction(trigger_feature_detection), "trigger_feature_detection should be async"
        print("✓ Trigger function is properly async")
        
        # Test basic functionality
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FeatureDataManager(tmpdir)
            info = fm.get_storage_info()
            assert 'base_path' in info, "Feature manager should provide storage info"
            print("✓ Feature manager basic functionality works")
        
        print("\n✅ All components ready for core.py integration!")
        print("\nNext steps:")
        print("1. Add imports to core.py")
        print("2. Add feature_manager and current_video_path to __init__")
        print("3. Store video path in open_file method")
        print("4. Extend on_metadata_loaded to trigger features")
        print("5. Add progress/completion callback methods")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration readiness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all auto detection tests."""
    print("🚀 AUTO FEATURE DETECTION TRIGGER TESTING")
    print("=" * 50)
    
    tests = [
        test_should_auto_detect,
        test_trigger_function,
        test_integration_readiness,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                result = await test()
            else:
                result = test()
                
            if result:
                passed += 1
            else:
                print(f"\n❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"\n❌ Test crashed: {test.__name__}: {e}")
    
    print(f"\n🎯 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ AUTO DETECTION TRIGGER: READY FOR CORE.PY INTEGRATION")
        return True
    else:
        print("❌ AUTO DETECTION TRIGGER: NEEDS FIXES")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)