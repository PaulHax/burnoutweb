#!/usr/bin/env python3
"""
Test Feature Storage System Implementation
Validates Phase 2a storage system against TeleSculptor compatibility.
"""

import sys
import tempfile
import shutil
sys.path.append('/home/paulhax/src/tele-stuff/burnoutweb/app')

def test_storage_initialization():
    """Test storage system initialization."""
    print("=== Testing Storage Initialization ===")
    
    try:
        from burn_out.app.features.feature_storage import FeatureDataManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test basic initialization
            manager = FeatureDataManager(tmpdir)
            
            # Check directory structure
            assert manager.features_dir.exists(), "features/ directory should be created"
            assert manager.base_path.exists(), "base directory should exist"
            
            # Check file paths
            assert manager.features_dir.name == "features", "features directory naming"
            assert manager.tracks_file.name == "tracks.txt", "tracks file naming"
            assert manager.landmarks_file.name == "landmarks.ply", "landmarks file naming"
            
            print("✓ Storage directories created correctly")
            print(f"✓ Features directory: {manager.features_dir}")
            print(f"✓ Tracks file: {manager.tracks_file}")
            
            return True
            
    except Exception as e:
        print(f"✗ Storage initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frame_feature_storage():
    """Test individual frame feature storage."""
    print("\n=== Testing Frame Feature Storage ===")
    
    try:
        from burn_out.app.features.feature_storage import FeatureDataManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FeatureDataManager(tmpdir)
            
            # Create test feature data (like service output)
            frame_id = 42
            video_basename = "test_video"
            feature_data = {
                'frame_number': frame_id,
                'feature_count': 3,
                'features': [
                    {'x': 100.5, 'y': 200.3, 'magnitude': 0.8, 'scale': 31.0, 'angle': 1.57, 'color': [255, 128, 64]},
                    {'x': 150.2, 'y': 180.7, 'magnitude': 0.9, 'scale': 25.0, 'angle': 0.78, 'color': [128, 255, 32]},
                    {'x': 300.1, 'y': 400.9, 'magnitude': 0.7, 'scale': 40.0, 'angle': 2.35, 'color': [64, 128, 255]}
                ]
            }
            
            # Test saving
            success = manager.save_frame_features(frame_id, feature_data, video_basename)
            assert success, "Feature saving should succeed"
            print(f"✓ Saved features for frame {frame_id}")
            
            # Test loading
            loaded_data = manager.load_frame_features(frame_id, video_basename)
            assert loaded_data is not None, "Should load saved features"
            assert loaded_data['frame_number'] == frame_id, "Frame ID should match"
            assert loaded_data['feature_count'] == 3, "Feature count should match"
            assert len(loaded_data['features']) == 3, "Features list should match"
            
            print(f"✓ Loaded features for frame {frame_id}")
            print(f"✓ Feature count: {loaded_data['feature_count']}")
            
            # Test TeleSculptor naming convention
            expected_filename = f"{video_basename}-{frame_id:05d}.json"
            expected_path = manager.features_dir / expected_filename
            assert expected_path.exists(), f"Feature file should exist at {expected_path}"
            print(f"✓ TeleSculptor naming convention: {expected_filename}")
            
            return True
            
    except Exception as e:
        print(f"✗ Frame feature storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detection_results_storage():
    """Test complete detection results storage."""
    print("\n=== Testing Detection Results Storage ===")
    
    try:
        from burn_out.app.features.feature_storage import FeatureDataManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FeatureDataManager(tmpdir)
            
            # Create mock detection results (like service output)
            detection_results = {
                'success': True,
                'video_path': '/path/to/test_video.mp4',
                'frame_features': {
                    1: {'frame_number': 1, 'feature_count': 250, 'features': []},
                    2: {'frame_number': 2, 'feature_count': 255, 'features': []},
                    3: {'frame_number': 3, 'feature_count': 248, 'features': []}
                },
                'summary': {
                    'total_frames_processed': 3,
                    'total_features_detected': 753,
                    'average_features_per_frame': 251.0
                }
            }
            
            # Test saving complete results
            success = manager.save_detection_results(detection_results)
            assert success, "Detection results saving should succeed"
            print("✓ Saved complete detection results")
            
            # Test loading complete results
            video_basename = "test_video"
            loaded_results = manager.load_detection_results(video_basename)
            assert loaded_results is not None, "Should load detection results"
            assert loaded_results['success'], "Loaded results should be successful"
            assert loaded_results['loaded_frames'] == 3, "Should load 3 frames"
            
            summary = loaded_results['summary']
            assert summary['total_frames_processed'] == 3, "Summary should match"
            assert summary['total_features_detected'] == 753, "Feature count should match"
            
            print(f"✓ Loaded detection results: {loaded_results['loaded_frames']} frames")
            print(f"✓ Total features: {summary['total_features_detected']}")
            
            return True
            
    except Exception as e:
        print(f"✗ Detection results storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tracks_storage():
    """Test feature tracks storage in TeleSculptor format."""
    print("\n=== Testing Feature Tracks Storage ===")
    
    try:
        from burn_out.app.features.feature_storage import FeatureDataManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FeatureDataManager(tmpdir)
            
            # Create test track data
            feature_tracks = [
                {
                    'id': 1001,
                    'observations': [
                        {'frame_id': 1, 'x': 100.5, 'y': 200.3, 'magnitude': 0.8, 'scale': 31.0, 'angle': 1.57, 'red': 255, 'green': 128, 'blue': 64, 'has_descriptor': 1},
                        {'frame_id': 2, 'x': 102.1, 'y': 201.8, 'magnitude': 0.82, 'scale': 30.5, 'angle': 1.60, 'red': 255, 'green': 130, 'blue': 66, 'has_descriptor': 1}
                    ]
                },
                {
                    'id': 1002,
                    'observations': [
                        {'frame_id': 1, 'x': 300.0, 'y': 150.0, 'magnitude': 0.9, 'scale': 25.0, 'angle': 0.78, 'red': 128, 'green': 255, 'blue': 32, 'has_descriptor': 1}
                    ]
                }
            ]
            
            # Test saving tracks
            success = manager.save_tracks(feature_tracks)
            assert success, "Track saving should succeed"
            print("✓ Saved feature tracks")
            
            # Verify tracks file exists
            assert manager.tracks_file.exists(), "tracks.txt should exist"
            
            # Test loading tracks
            loaded_tracks = manager.load_tracks()
            assert len(loaded_tracks) == 2, "Should load 2 tracks"
            
            # Verify track data
            track_1001 = next((t for t in loaded_tracks if t['id'] == 1001), None)
            assert track_1001 is not None, "Track 1001 should exist"
            assert len(track_1001['observations']) == 2, "Track 1001 should have 2 observations"
            
            track_1002 = next((t for t in loaded_tracks if t['id'] == 1002), None)
            assert track_1002 is not None, "Track 1002 should exist"
            assert len(track_1002['observations']) == 1, "Track 1002 should have 1 observation"
            
            print(f"✓ Loaded {len(loaded_tracks)} feature tracks")
            
            # Verify TeleSculptor format by reading file
            with open(manager.tracks_file, 'r') as f:
                lines = f.readlines()
                data_lines = [line for line in lines if not line.startswith('#') and line.strip()]
                assert len(data_lines) == 3, "Should have 3 data lines (2+1 observations)"
                
                # Check format of first data line
                parts = data_lines[0].split()
                assert len(parts) >= 11, "Each line should have at least 11 fields"
                assert parts[0] == "1001", "First track ID should be 1001"
                
            print("✓ TeleSculptor format validation passed")
            
            return True
            
    except Exception as e:
        print(f"✗ Feature tracks storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_info_and_validation():
    """Test storage information and compatibility validation."""
    print("\n=== Testing Storage Info and Validation ===")
    
    try:
        from burn_out.app.features.feature_storage import FeatureDataManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = FeatureDataManager(tmpdir)
            
            # Test storage info
            info = manager.get_storage_info()
            assert 'base_path' in info, "Should have base_path info"
            assert 'features_dir_exists' in info, "Should have directory existence info"
            assert info['features_dir_exists'], "Features directory should exist"
            
            print(f"✓ Storage info: {info['total_feature_files']} feature files")
            print(f"✓ KWIVER I/O available: {info['kwiver_io_available']}")
            
            # Test TeleSculptor compatibility validation
            validation = manager.validate_telesculptor_compatibility()
            assert 'compatible' in validation, "Should have compatibility status"
            assert 'issues' in validation, "Should have issues list"
            assert 'recommendations' in validation, "Should have recommendations list"
            
            print(f"✓ TeleSculptor compatibility: {validation['compatible']}")
            if validation['issues']:
                print(f"  Issues: {validation['issues']}")
            if validation['recommendations']:
                print(f"  Recommendations: {validation['recommendations']}")
            
            return True
            
    except Exception as e:
        print(f"✗ Storage info and validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_convenience_functions():
    """Test convenience functions."""
    print("\n=== Testing Convenience Functions ===")
    
    try:
        from burn_out.app.features.feature_storage import (
            create_feature_manager, save_detection_results, load_detection_results
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test manager creation
            manager = create_feature_manager(tmpdir)
            assert manager.base_path.exists(), "Manager should be created"
            print("✓ create_feature_manager() works")
            
            # Test convenience save/load
            detection_results = {
                'success': True,
                'video_path': '/path/to/convenience_test.mp4',
                'frame_features': {1: {'frame_number': 1, 'feature_count': 100, 'features': []}},
                'summary': {'total_frames_processed': 1, 'total_features_detected': 100}
            }
            
            success = save_detection_results(detection_results, tmpdir)
            assert success, "Convenience save should work"
            print("✓ save_detection_results() works")
            
            loaded = load_detection_results("convenience_test", tmpdir)
            assert loaded is not None, "Convenience load should work"
            assert loaded['success'], "Loaded data should be successful"
            print("✓ load_detection_results() works")
            
            return True
            
    except Exception as e:
        print(f"✗ Convenience functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all storage system tests."""
    print("🗄️  PHASE 2A: FEATURE STORAGE SYSTEM TESTING")
    print("=" * 50)
    
    tests = [
        test_storage_initialization,
        test_frame_feature_storage,
        test_detection_results_storage,
        test_tracks_storage,
        test_storage_info_and_validation,
        test_convenience_functions,
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
        print("✅ PHASE 2A FEATURE STORAGE: READY FOR PHASE 3A")
        return True
    else:
        print("❌ PHASE 2A FEATURE STORAGE: NEEDS FIXES")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)