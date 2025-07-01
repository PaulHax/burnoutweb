"""
Debug video loading to match burnoutweb exactly.
"""

import kwiver.vital.algo as kva
import kwiver.vital.config as config_mod
from kwiver.vital.types import Timestamp
from kwiver.vital import plugin_management
from minimal_kwiver_test import MinimalFeatureDetector

def test_video_with_explicit_config():
    """Test video loading with explicit FFmpeg configuration."""
    print("=== Debug Video Loading ===")
    
    # Load plugins
    pm = plugin_management.plugin_manager_instance()
    pm.load_all_plugins()
    
    video_path = "/home/paulhax/src/tele-stuff/videos/09172008flight1tape3_2.mpg"
    
    try:
        # Method 1: Try with explicit FFmpeg config
        print("Method 1: Explicit FFmpeg configuration")
        config = config_mod.empty_config()
        config.set_value("video_reader:type", "ffmpeg")
        config.set_value("video_reader:klv_enabled", "true")
        config.set_value("video_reader:unknown_stream_behavior", "ignore")
        config.set_value("video_reader:audio_enabled", "false")  # Disable audio
        
        video_reader = kva.VideoInput.set_nested_algo_configuration("video_reader", config)
        
        if video_reader.open(video_path):
            print("✓ Method 1 SUCCESS: Video opened with explicit config")
            
            # Test frame reading
            timestamp = Timestamp()
            if video_reader.next_frame(timestamp):
                print(f"✓ Got frame {timestamp.get_frame()}")
                
                image_container = video_reader.frame_image()
                if image_container:
                    print("✓ Got image container")
                    
                    # Test feature detection
                    detector = MinimalFeatureDetector()
                    features = detector.detect_features(image_container)
                    if features:
                        num_features = len(features.features())
                        print(f"✓ FEATURE DETECTION SUCCESS: {num_features} features detected!")
                        return True
            
            video_reader.close()
        else:
            print("✗ Method 1 failed")
            
        # Method 2: Try minimal config like burnoutweb
        print("\nMethod 2: Minimal config like burnoutweb")
        config2 = config_mod.empty_config()
        config2.set_value("video_reader:type", "ffmpeg")
        
        video_reader2 = kva.VideoInput.set_nested_algo_configuration("video_reader", config2)
        
        if video_reader2.open(video_path):
            print("✓ Method 2 SUCCESS: Video opened with minimal config")
            video_reader2.close()
        else:
            print("✗ Method 2 failed")
            
        # Method 3: Try direct FFmpeg reader without nesting
        print("\nMethod 3: Direct FFmpeg reader")
        direct_reader = kva.VideoInput.create("ffmpeg")
        
        if direct_reader.open(video_path):
            print("✓ Method 3 SUCCESS: Direct FFmpeg reader worked")
            direct_reader.close()
        else:
            print("✗ Method 3 failed")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
    return False


if __name__ == "__main__":
    success = test_video_with_explicit_config()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")