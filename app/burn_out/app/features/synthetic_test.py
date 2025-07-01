"""
Synthetic test to validate KWIVER feature detection with generated images.
Creates simple test images to verify the complete pipeline works.
"""

import numpy as np
from minimal_kwiver_test import MinimalFeatureDetector
import kwiver.vital.types as kvt


def create_test_image(width=640, height=480, add_features=True):
    """
    Create a synthetic test image with corner features.
    
    Args:
        width: Image width
        height: Image height  
        add_features: Whether to add corner features
        
    Returns:
        KWIVER ImageContainer with test image
    """
    # Create grayscale test image
    image_data = np.zeros((height, width), dtype=np.uint8)
    
    if add_features:
        # Add some corner features
        # Top-left corners
        image_data[50:70, 50:70] = 255
        image_data[150:170, 100:120] = 255
        image_data[250:270, 200:220] = 255
        
        # Bottom-right corners  
        image_data[350:370, 450:470] = 255
        image_data[300:320, 500:520] = 255
        
        # Add some noise for more realistic features
        noise = np.random.randint(0, 50, (height, width), dtype=np.uint8)
        image_data = np.clip(image_data.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Convert to KWIVER Image using numpy array constructor
    image = kvt.Image(image_data)  # Direct numpy array constructor
    image_container = kvt.ImageContainer(image)
    
    return image_container


def test_synthetic_feature_detection():
    """Run synthetic feature detection test."""
    print("=== Synthetic Feature Detection Test ===")
    
    try:
        # Create detector
        detector = MinimalFeatureDetector()
        
        # Create test image
        print("Creating synthetic test image...")
        image_container = create_test_image()
        print("✓ Test image created")
        
        # Run feature detection
        print("Running feature detection...")
        feature_set = detector.detect_features(image_container)
        
        if feature_set:
            features = feature_set.features()
            print(f"✓ Feature detection successful: {len(features)} features detected")
            
            # Print first few feature locations
            for i, feature in enumerate(features[:10]):
                loc = feature.location()
                print(f"  Feature {i}: ({loc.x():.1f}, {loc.y():.1f})")
                
            return True
        else:
            print("✗ Feature detection returned no results")
            return False
            
    except Exception as e:
        print(f"✗ Synthetic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_synthetic_feature_detection()
    print(f"\nSynthetic test: {'SUCCESS' if success else 'FAILED'}")