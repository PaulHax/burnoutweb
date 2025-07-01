"""
Minimal KWIVER feature detection test.

This module provides the simplest possible test to validate that:
1. KWIVER Python bindings work in burnoutweb environment
2. We can create feature detectors
3. We can detect features on video frames
4. Basic data flow works

Based on TeleSculptor's ORB feature detection approach.
"""

import logging
from typing import Optional, List, Tuple

# Test KWIVER imports
try:
    import kwiver.vital.algo as kvital_algo
    import kwiver.vital.types as kvital_types
    import kwiver.vital.plugin_management as pm
    import kwiver.vital.config as config_mod
    from kwiver.vital.config import Config
    from kwiver.vital.types import Image, ImageContainer, Feature, FeatureSet
    
    # Load KWIVER plugins - CRITICAL for algorithm availability
    pm.plugin_manager_instance().load_all_plugins()
    
    KWIVER_AVAILABLE = True
    print("✓ KWIVER Python bindings imported successfully")
    print("✓ KWIVER plugins loaded successfully")
    
    # Show available detectors
    available_detectors = kvital_algo.DetectFeatures.registered_names()
    print(f"✓ Available detectors: {available_detectors}")
    
except ImportError as e:
    KWIVER_AVAILABLE = False
    print(f"✗ KWIVER import failed: {e}")


class MinimalFeatureDetector:
    """
    Minimal KWIVER-based feature detector for validation testing.
    
    Uses ORB detector with TeleSculptor's parameters:
    - n_features: 500
    - scale_factor: 1.2  
    - n_levels: 8
    - fast_threshold: 20
    """
    
    def __init__(self):
        self.detector = None
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize ORB feature detector with TeleSculptor parameters."""
        if not KWIVER_AVAILABLE:
            raise RuntimeError("KWIVER not available")
            
        try:
            # Create ORB detector algorithm
            self.detector = kvital_algo.DetectFeatures.create("ocv_ORB")
            
            # Configure with TeleSculptor's ORB parameters
            cfg = config_mod.empty_config()
            cfg.set_value("n_features", "500")
            cfg.set_value("scale_factor", "1.2")
            cfg.set_value("n_levels", "8")
            cfg.set_value("edge_threshold", "31")
            cfg.set_value("fast_threshold", "20")
            cfg.set_value("patch_size", "31")
            
            self.detector.set_configuration(cfg)
            print("✓ ORB detector initialized with TeleSculptor parameters")
            
        except Exception as e:
            print(f"✗ Failed to initialize ORB detector: {e}")
            raise
    
    def detect_features(self, image_container) -> Optional['FeatureSet']:
        """
        Detect features in a single frame.
        
        Args:
            image_container: KWIVER ImageContainer with frame data
            
        Returns:
            FeatureSet containing detected features, or None if detection failed
        """
        if not self.detector:
            print("✗ Detector not initialized")
            return None
            
        try:
            # Run feature detection
            feature_set = self.detector.detect(image_container)
            
            num_features = len(feature_set.features()) if feature_set else 0
            print(f"✓ Detected {num_features} features")
            
            return feature_set
            
        except Exception as e:
            print(f"✗ Feature detection failed: {e}")
            return None
    
    def test_detection_on_frame(self, video_path: str) -> bool:
        """
        Test feature detection on a video frame using KWIVER VideoInput.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if test successful, False otherwise
        """
        try:
            # Import KWIVER video input components
            from kwiver.vital.algo import VideoInput
            from kwiver.vital.config import read_config_file
            from kwiver.vital.types import Timestamp
            from pathlib import Path
            
            print(f"Testing feature detection on video: {video_path}")
            
            # Use burnoutweb's video config if available
            config_path = Path(__file__).parent.parent / "assets" / "config" / "gui_image_video_reader.conf"
            if not config_path.exists():
                print(f"Config file not found: {config_path}")
                # Create basic video reader config
                cfg = config_mod.empty_config()
                cfg.set_value("video_reader:type", "ffmpeg")
                video_reader = kvital_algo.VideoInput.create("ffmpeg")
                video_reader.set_configuration(cfg)
            else:
                print(f"Using config: {config_path}")
                config = read_config_file(str(config_path))
                video_reader = VideoInput.set_nested_algo_configuration("video_reader", config)
            
            # Open video
            if not video_reader.open(video_path):
                print(f"✗ Failed to open video: {video_path}")
                return False
            
            print("✓ Video opened successfully")
            
            # Get first frame
            current_timestamp = Timestamp()
            if not video_reader.next_frame(current_timestamp):
                print("✗ Failed to get first frame")
                return False
                
            print(f"✓ Got frame {current_timestamp.get_frame()}")
            
            # Get frame image (this is the key for feature detection)
            image_container = video_reader.frame_image()
            if not image_container:
                print("✗ Failed to get frame image")
                return False
                
            print("✓ Got frame image container")
            
            # Run feature detection on this frame
            feature_set = self.detect_features(image_container)
            if feature_set:
                features = feature_set.features()
                print(f"✓ Feature detection successful: {len(features)} features detected")
                
                # Print first few feature locations for validation
                for i, feature in enumerate(features[:5]):
                    loc = feature.location()
                    print(f"  Feature {i}: ({loc.x():.1f}, {loc.y():.1f})")
                
                video_reader.close()
                return True
            else:
                print("✗ Feature detection returned no results")
                video_reader.close()
                return False
                
        except Exception as e:
            print(f"✗ Frame detection test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def run_minimal_test():
    """Run minimal KWIVER feature detection validation test."""
    print("=== Minimal KWIVER Feature Detection Test ===")
    
    # Test 1: KWIVER imports
    if not KWIVER_AVAILABLE:
        print("ABORT: KWIVER not available")
        return False
    
    # Test 2: Detector initialization
    try:
        detector = MinimalFeatureDetector()
        print("✓ Feature detector created successfully")
    except Exception as e:
        print(f"✗ Detector creation failed: {e}")
        return False
    
    # Test 3: Video frame detection
    # Look for test video file or skip if not available
    import os
    test_video = None
    
    # Check for common test video locations
    possible_videos = [
        "/home/paulhax/src/tele-stuff/test_video.mp4",
        "/home/paulhax/Downloads/test_video.mp4",
        "/tmp/test_video.mp4"
    ]
    
    for video_path in possible_videos:
        if os.path.exists(video_path):
            test_video = video_path
            break
    
    if test_video:
        print(f"Using test video: {test_video}")
        success = detector.test_detection_on_frame(test_video)
    else:
        print("No test video found. Skipping video frame test.")
        print("To test with video, create a test video at one of these locations:")
        for path in possible_videos:
            print(f"  {path}")
        success = True  # Don't fail test if no video available
    
    print("=== Test Complete ===")
    return success


if __name__ == "__main__":
    run_minimal_test()