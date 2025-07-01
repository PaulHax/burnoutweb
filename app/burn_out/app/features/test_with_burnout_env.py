"""
Feature detection test using the exact same environment as burnoutweb.
This mimics how burn-out --data loads and processes videos.
"""

import sys
import os
from pathlib import Path

# Add the burnoutweb app to Python path (same as burn-out script does)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import exactly what burnoutweb uses
from burn_out.app.core import BurnOutApp, pick_video_reader_config
from minimal_kwiver_test import MinimalFeatureDetector

import kwiver.vital.algo as kva
from kwiver.vital.config import read_config_file
from kwiver.vital.types import Timestamp
from kwiver.vital import plugin_management

def test_video_feature_detection_burnout_style():
    """Test feature detection using the exact same setup as burnoutweb."""
    print("=== Testing Feature Detection with BurnOut Environment ===")
    
    # Initialize KWIVER exactly like burnoutweb does in core.py line 28-29
    vpm = plugin_management.plugin_manager_instance()
    vpm.load_all_plugins()
    print("✓ KWIVER plugins loaded (burnoutweb style)")
    
    # Test video path - same as your command line example
    video_path = "/home/paulhax/src/tele-stuff/videos/09172008flight1tape3_2.mpg"
    
    if not Path(video_path).exists():
        print(f"✗ Video not found: {video_path}")
        return False
    
    print(f"Testing video: {Path(video_path).name}")
    
    try:
        # Use EXACT same video loading as burnoutweb core.py open_file() method
        print("Creating video source using burnoutweb method...")
        
        # This is exactly core.py line 229-233
        video_source = kva.VideoInput.set_nested_algo_configuration(
            "video_reader",
            read_config_file(pick_video_reader_config(video_path)),
        )
        
        # Open video exactly like burnoutweb
        if not video_source.open(video_path):
            print(f"✗ Failed to open video using burnoutweb method")
            return False
        
        print("✓ Video opened successfully using burnoutweb method!")
        
        # Get video info like burnoutweb does
        num_frames = video_source.num_frames()
        frame_rate = video_source.frame_rate()
        print(f"  Video info: {num_frames} frames, {frame_rate} fps")
        
        # Create feature detector
        detector = MinimalFeatureDetector()
        
        # Test feature detection on first few frames
        current_timestamp = Timestamp()
        frames_processed = 0
        max_frames = 3
        
        print("Processing frames for feature detection...")
        
        while video_source.next_frame(current_timestamp) and frames_processed < max_frames:
            if not current_timestamp.has_valid_frame():
                continue
                
            frame_num = current_timestamp.get_frame()
            print(f"  Processing frame {frame_num}")
            
            # Get frame image (this is the key step that was failing before)
            image_container = video_source.frame_image()
            if not image_container:
                print(f"  ✗ No image container for frame {frame_num}")
                continue
                
            print(f"  ✓ Got image container for frame {frame_num}")
            
            # Run feature detection
            feature_set = detector.detect_features(image_container)
            
            if feature_set:
                features = feature_set.features()
                print(f"  ✓ Detected {len(features)} features on frame {frame_num}")
                
                # Show sample feature info (fix the location access)
                if len(features) > 0:
                    for i in range(min(3, len(features))):
                        feature = features[i]
                        # Check what type features actually are
                        print(f"    Feature {i} type: {type(feature)}")
                        print(f"    Feature {i} value: {feature}")
                        
                frames_processed += 1
            else:
                print(f"  ✗ No features detected on frame {frame_num}")
        
        video_source.close()
        print(f"✓ Successfully processed {frames_processed} frames")
        
        return frames_processed > 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing feature detection with burnoutweb environment...")
    print("This should work exactly like: burn-out --data ../videos/09172008flight1tape3_2.mpv")
    
    success = test_video_feature_detection_burnout_style()
    
    if success:
        print("\n✓ SUCCESS: Feature detection works with burnoutweb environment!")
        print("✓ Ready to integrate into burnoutweb pipeline")
    else:
        print("\n✗ FAILED: Need to debug further")