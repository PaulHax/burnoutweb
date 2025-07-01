"""
Test feature detection by ignoring video_reader.open() return value,
just like burnoutweb does in video_importer.py.
"""

import kwiver.vital.algo as kva
from kwiver.vital.config import read_config_file
from kwiver.vital.types import Timestamp
from kwiver.vital import plugin_management
from minimal_kwiver_test import MinimalFeatureDetector

def test_video_like_burnoutweb():
    """Test video loading exactly like burnoutweb - ignore open() return value."""
    print("=== Testing Like BurnoutWeb (Ignore open() result) ===")
    
    # Load plugins like burnoutweb
    pm = plugin_management.plugin_manager_instance()
    pm.load_all_plugins()
    
    video_path = "/home/paulhax/src/tele-stuff/videos/09172008flight1tape3_2.mpg"
    
    try:
        # Use EXACT same approach as burnoutweb video_importer.py
        from burn_out.app.core import pick_video_reader_config
        
        config_file = pick_video_reader_config(video_path)
        config = read_config_file(config_file)
        
        # Create video reader exactly like video_importer.py line 102-103
        video_reader = kva.VideoInput.set_nested_algo_configuration("video_reader", config)
        
        # DON'T CHECK the return value - just like burnoutweb!
        video_reader.open(video_path)
        print("✓ Called video_reader.open() (ignoring return value like burnoutweb)")
        
        # Now try to process frames - this is the real test
        current_timestamp = Timestamp()
        frame_count = 0
        
        print("Attempting to read frames...")
        
        while video_reader.next_frame(current_timestamp) and frame_count < 3:
            if not current_timestamp.has_valid_frame():
                continue
                
            frame_num = current_timestamp.get_frame()
            print(f"✓ SUCCESS: Got frame {frame_num}")
            
            # Try to get the image
            image_container = video_reader.frame_image()
            if image_container:
                print(f"✓ SUCCESS: Got image container for frame {frame_num}")
                
                # Test feature detection
                detector = MinimalFeatureDetector()
                feature_set = detector.detect_features(image_container)
                
                if feature_set:
                    features = feature_set.features()
                    print(f"✓ FEATURE DETECTION SUCCESS: {len(features)} features on frame {frame_num}")
                    
                    # Show first few features
                    for i in range(min(3, len(features))):
                        # Get feature info safely
                        feature = features[i]
                        print(f"    Feature {i}: {feature}")
                    
                    frame_count += 1
                else:
                    print(f"✗ No features detected on frame {frame_num}")
            else:
                print(f"✗ No image container for frame {frame_num}")
        
        video_reader.close()
        
        if frame_count > 0:
            print(f"\n🎉 SUCCESS: Processed {frame_count} frames with feature detection!")
            print("✓ The video DOES work - warnings were not fatal!")
            return True
        else:
            print("\n✗ Could not process any frames")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing video loading by ignoring open() return value...")
    print("This matches how burnoutweb actually works in video_importer.py")
    
    success = test_video_like_burnoutweb()
    
    if success:
        print("\n🎉 BREAKTHROUGH: Video processing works!")
        print("✓ H.264 warnings are just warnings, not errors")
        print("✓ Ready to integrate feature detection into burnoutweb!")
    else:
        print("\n✗ Still having issues - need more investigation")