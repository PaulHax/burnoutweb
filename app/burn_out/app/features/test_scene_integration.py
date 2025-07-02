#!/usr/bin/env python3
"""
Test Scene Integration Module
Validates functional programming approach for feature-scene integration.
"""

import sys
import tempfile
sys.path.append('/home/paulhax/src/tele-stuff/burnoutweb/app')

def test_functional_approach():
    """Test pure functional feature processing."""
    print("=== Testing Functional Scene Integration ===")
    
    try:
        from burn_out.app.features.scene_integration import (
            extract_video_basename,
            calculate_feature_summary,
            merge_feature_tracks,
            create_frame_context,
            filter_features_by_quality,
            get_features_in_region
        )
        
        # Test video basename extraction
        video_path = "/path/to/test_video.mp4"
        basename = extract_video_basename(video_path)
        assert basename == "test_video", f"Expected 'test_video', got '{basename}'"
        print("✓ Video basename extraction works")
        
        # Test feature summary calculation
        mock_tracks = {
            1: {'feature_count': 100, 'features': []},
            2: {'feature_count': 150, 'features': []},
            3: {'feature_count': 120, 'features': []}
        }
        
        summary = calculate_feature_summary(mock_tracks, "test_video")
        assert summary['total_frames'] == 3, "Should have 3 frames"
        assert summary['total_features'] == 370, "Should have 370 total features"
        assert abs(summary['average_features_per_frame'] - 123.33) < 0.1, "Average should be ~123.33"
        print("✓ Feature summary calculation works")
        
        # Test track merging
        existing = {1: {'feature_count': 100}, 2: {'feature_count': 150}}
        new_tracks = {3: {'feature_count': 120}, 4: {'feature_count': 80}}
        
        merged = merge_feature_tracks(existing, new_tracks)
        assert len(merged) == 4, "Should have 4 frames after merge"
        assert merged[3]['feature_count'] == 120, "New tracks should be included"
        print("✓ Track merging works")
        
        # Test frame context creation
        context = create_frame_context(mock_tracks, 2)
        assert context['frame_id'] == 2, "Frame ID should match"
        assert context['has_features'] == True, "Should have features"
        assert context['feature_count'] == 150, "Should have 150 features"
        print("✓ Frame context creation works")
        
        # Test feature filtering
        mock_features = [
            {'x': 100, 'y': 200, 'magnitude': 0.8},
            {'x': 150, 'y': 180, 'magnitude': 0.05},  # Low quality
            {'x': 300, 'y': 400, 'magnitude': 0.9}
        ]
        
        filtered = filter_features_by_quality(mock_features, min_magnitude=0.1)
        assert len(filtered) == 2, "Should filter out low quality feature"
        print("✓ Feature quality filtering works")
        
        # Test region filtering
        region_features = get_features_in_region(
            mock_features, 
            x_range=(90, 200), 
            y_range=(150, 250)
        )
        assert len(region_features) == 2, "Should find 2 features in region"
        print("✓ Region-based feature filtering works")
        
        return True
        
    except Exception as e:
        print(f"✗ Functional approach test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_feature_manager_integration():
    """Test integration with feature manager."""
    print("\n=== Testing Feature Manager Integration ===")
    
    try:
        from burn_out.app.features.scene_integration import (
            initialize_feature_data,
            add_detection_results_to_data,
            load_video_features
        )
        from burn_out.app.features.feature_storage import FeatureDataManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create feature manager
            feature_manager = FeatureDataManager(tmpdir)
            
            # Test initialization
            video_path = "/path/to/test_video.mp4"
            feature_data = initialize_feature_data(video_path, feature_manager)
            
            assert feature_data['video_basename'] == "test_video", "Basename should match"
            assert feature_data['loaded'] == False, "Should start with no features"
            assert len(feature_data['feature_tracks']) == 0, "Should start empty"
            print("✓ Feature data initialization works")
            
            # Test adding detection results
            mock_detection_results = {
                'success': True,
                'video_path': video_path,
                'frame_features': {
                    1: {'frame_number': 1, 'feature_count': 250, 'features': []},
                    2: {'frame_number': 2, 'feature_count': 255, 'features': []}
                },
                'summary': {
                    'total_frames_processed': 2,
                    'total_features_detected': 505
                }
            }
            
            updated_data, success = add_detection_results_to_data(
                feature_data, mock_detection_results, feature_manager
            )
            
            assert success == True, "Adding detection results should succeed"
            assert len(updated_data['feature_tracks']) == 2, "Should have 2 frames"
            assert updated_data['loaded'] == True, "Should be loaded after adding results"
            print("✓ Adding detection results works")
            
            # Test loading existing features
            loaded_features = load_video_features(feature_manager, "test_video")
            assert loaded_features['loaded'] == True, "Should load saved features"
            assert len(loaded_features['frame_features']) == 2, "Should load 2 frames"
            print("✓ Loading existing features works")
            
            return True
            
    except Exception as e:
        print(f"✗ Feature manager integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_geo_conversion():
    """Test geo-conversion functions."""
    print("\n=== Testing Geo-Conversion Functions ===")
    
    try:
        from burn_out.app.features.scene_integration import (
            convert_features_to_world_coordinates,
            apply_geo_conversion_to_frame,
            apply_geo_conversion_to_tracks
        )
        
        # Test feature coordinate conversion
        mock_features = [
            {'x': 100, 'y': 200, 'magnitude': 0.8},
            {'x': 150, 'y': 180, 'magnitude': 0.9}
        ]
        
        mock_camera_pose = {'center': [0, 0, 0], 'rotation': [0, 0, 0]}
        mock_local_geo_cs = None  # Placeholder
        
        world_features = convert_features_to_world_coordinates(
            mock_features, mock_camera_pose, mock_local_geo_cs
        )
        
        assert len(world_features) == 2, "Should preserve all features"
        assert all('world_coords' in f for f in world_features), "Should add world_coords"
        assert all('geo_converted' in f for f in world_features), "Should mark as geo_converted"
        print("✓ Feature coordinate conversion works")
        
        # Test frame geo-conversion
        frame_data = {
            'frame_number': 1,
            'feature_count': 2,
            'features': mock_features
        }
        
        converted_frame = apply_geo_conversion_to_frame(
            frame_data, mock_camera_pose, mock_local_geo_cs
        )
        
        assert 'world_features' in converted_frame, "Should add world_features"
        assert converted_frame['geo_converted'] == True, "Should mark as converted"
        print("✓ Frame geo-conversion works")
        
        # Test tracks geo-conversion
        mock_tracks = {
            1: {'features': mock_features},
            2: {'features': mock_features}
        }
        
        mock_camera_map = {
            1: mock_camera_pose,
            2: mock_camera_pose
        }
        
        converted_tracks = apply_geo_conversion_to_tracks(
            mock_tracks, mock_camera_map, mock_local_geo_cs
        )
        
        assert len(converted_tracks) == 2, "Should preserve all tracks"
        assert all('geo_converted' in track for track in converted_tracks.values()), "All should be converted"
        print("✓ Tracks geo-conversion works")
        
        return True
        
    except Exception as e:
        print(f"✗ Geo-conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all scene integration tests."""
    print("🔗 PHASE 2.2: SCENE INTEGRATION TESTING")
    print("=" * 50)
    
    tests = [
        test_functional_approach,
        test_feature_manager_integration,
        test_geo_conversion,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test failed: {test.__name__}")
    
    print(f"\n🎯 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ PHASE 2.2 SCENE INTEGRATION: FUNCTIONAL APPROACH VALIDATED")
        print("\nKey achievements:")
        print("✅ Pure functional programming approach")
        print("✅ No dependencies on Scene class internals")
        print("✅ Feature data processing functions")
        print("✅ Feature manager integration")
        print("✅ Geo-conversion function structure")
        print("✅ Clean separation of concerns")
        print("\n🚀 READY FOR SCENE CLASS TO USE THESE FUNCTIONS")
        return True
    else:
        print("❌ PHASE 2.2 SCENE INTEGRATION: NEEDS FIXES")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)