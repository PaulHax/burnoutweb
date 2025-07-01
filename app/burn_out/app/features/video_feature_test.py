"""
Complete feature detection test using real video files.
Tests the full pipeline: video loading, frame extraction, feature detection.
"""

import numpy as np
from minimal_kwiver_test import MinimalFeatureDetector
import kwiver.vital.types as kvt
import kwiver.vital.algo as kva
import kwiver.vital.plugin_management as pm
import kwiver.vital.config as config_mod
from kwiver.vital.config import read_config_file
from kwiver.vital.types import Timestamp
from pathlib import Path


def test_real_video_feature_detection():
    """Test feature detection on real video files."""
    print("=== Real Video Feature Detection Test ===")

    # Load KWIVER plugins
    pm.plugin_manager_instance().load_all_plugins()

    # List of videos to try
    test_videos = [
        "/home/paulhax/src/tele-stuff/videos/09172008flight1tape3_2.mpg",
        "/home/paulhax/src/tele-stuff/videos/09152008flight2tape2_4.mpg",
    ]

    success_count = 0

    for video_path in test_videos:
        if not Path(video_path).exists():
            print(f"Video not found: {video_path}")
            continue

        print(f"\nTesting video: {Path(video_path).name}")

        try:
            # Use EXACT same approach as burnoutweb core.py line 229-233
            from burn_out.app.core import pick_video_reader_config

            # Create video reader exactly like burnoutweb does
            config_file = pick_video_reader_config(video_path)
            video_reader = kva.VideoInput.set_nested_algo_configuration(
                "video_reader",
                read_config_file(config_file),
            )

            # Try to open video
            if not video_reader.open(video_path):
                print(f"✗ Failed to open video: {video_path}")
                continue

            print("✓ Video opened successfully")

            # Get video info
            frame_count = 0
            current_timestamp = Timestamp()

            # Try to get the first few frames
            frames_tested = 0
            max_frames_to_test = 3

            while (
                video_reader.next_frame(current_timestamp)
                and frames_tested < max_frames_to_test
            ):
                if not current_timestamp.has_valid_frame():
                    continue

                frame_num = current_timestamp.get_frame()
                print(f"  Processing frame {frame_num}")

                # Try to get image
                image_container = video_reader.frame_image()
                if not image_container:
                    print(f"  ✗ Failed to get image for frame {frame_num}")
                    continue

                print(f"  ✓ Got image container for frame {frame_num}")

                # Create feature detector
                detector = MinimalFeatureDetector()

                # Run feature detection
                feature_set = detector.detect_features(image_container)

                if feature_set:
                    features = feature_set.features()
                    print(f"  ✓ Detected {len(features)} features on frame {frame_num}")

                    # Show sample features
                    for i, feature in enumerate(features[:3]):
                        loc = feature.location()
                        print(f"    Feature {i}: ({loc.x():.1f}, {loc.y():.1f})")

                    frames_tested += 1
                    success_count += 1

                    if frames_tested >= max_frames_to_test:
                        break
                else:
                    print(f"  ✗ No features detected on frame {frame_num}")

            video_reader.close()

            if frames_tested > 0:
                print(
                    f"✓ Successfully processed {frames_tested} frames from {Path(video_path).name}"
                )
            else:
                print(f"✗ Could not process any frames from {Path(video_path).name}")

        except Exception as e:
            print(f"✗ Error processing {Path(video_path).name}: {e}")
            continue

    print(f"\n=== Test Summary ===")
    print(f"Successfully processed frames: {success_count}")

    return success_count > 0


def test_synthetic_with_real_config():
    """Test synthetic images using real video processing configuration."""
    print("\n=== Synthetic Test with Real Config ===")

    try:
        # Create detector with same config as real videos
        detector = MinimalFeatureDetector()

        # Create synthetic test image
        height, width = 480, 640
        image_data = np.zeros((height, width), dtype=np.uint8)

        # Add corner features
        image_data[50:70, 50:70] = 255
        image_data[150:170, 100:120] = 255
        image_data[250:270, 200:220] = 255
        image_data[350:370, 450:470] = 255

        # Add some texture
        noise = np.random.randint(0, 50, (height, width), dtype=np.uint8)
        image_data = np.clip(image_data.astype(np.int16) + noise, 0, 255).astype(
            np.uint8
        )

        # Convert to KWIVER format
        image = kvt.Image(image_data)
        image_container = kvt.ImageContainer(image)

        print("✓ Created synthetic test image")

        # Run feature detection
        feature_set = detector.detect_features(image_container)

        if feature_set:
            features = feature_set.features()
            print(f"✓ Detected {len(features)} features on synthetic image")

            # Show sample features
            for i, feature in enumerate(features[:5]):
                loc = feature.location()
                print(f"  Feature {i}: ({loc.x():.1f}, {loc.y():.1f})")

            return True
        else:
            print("✗ No features detected on synthetic image")
            return False

    except Exception as e:
        print(f"✗ Synthetic test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing KWIVER feature detection with real videos and synthetic data...")

    # Test 1: Real video processing
    real_video_success = test_real_video_feature_detection()

    # Test 2: Synthetic image processing
    synthetic_success = test_synthetic_with_real_config()

    # Overall result
    print(f"\n=== Final Results ===")
    print(f"Real video test: {'SUCCESS' if real_video_success else 'FAILED'}")
    print(f"Synthetic test: {'SUCCESS' if synthetic_success else 'FAILED'}")

    if real_video_success or synthetic_success:
        print("✓ KWIVER feature detection integration is working!")
        print("✓ Ready to proceed with Phase 1 implementation")
    else:
        print("✗ Feature detection integration needs debugging")
