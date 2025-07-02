#!/usr/bin/env python3
"""
Test Configuration System Implementation
Validates Phase 1a implementation against TeleSculptor standards.
"""

import sys
import os
sys.path.append('/home/paulhax/src/tele-stuff/burnoutweb/app')

def test_kwiver_integration():
    """Test KWIVER imports and plugin loading."""
    print("=== Testing KWIVER Integration ===")
    
    try:
        from kwiver.vital import plugin_management
        from kwiver.vital.config import empty_config
        import kwiver.vital.algo as kva
        
        # Load plugins
        vpm = plugin_management.plugin_manager_instance()
        vpm.load_all_plugins()
        print("✓ KWIVER plugins loaded successfully")
        
        # Test ORB detector creation
        detector = kva.DetectFeatures.create("ocv_ORB")
        print(f"✓ ORB detector created: {type(detector).__name__}")
        
        return True
        
    except Exception as e:
        print(f"✗ KWIVER integration failed: {e}")
        return False

def test_orb_detector_config():
    """Test ORB detector configuration."""
    print("\n=== Testing ORB Detector Configuration ===")
    
    try:
        from burn_out.app.features.config.orb_detector_config import (
            ORBDetectorConfig, create_orb_detector, validate_orb_parameters
        )
        
        # Test default parameters
        params = ORBDetectorConfig.DEFAULT_PARAMS
        print(f"✓ Default parameters loaded: {len(params)} parameters")
        
        # Validate TeleSculptor exact values
        expected_values = {
            'n_features': 500,
            'scale_factor': 1.2,
            'n_levels': 8,
            'fast_threshold': 20,
            'edge_threshold': 31,
            'patch_size': 31,
            'first_level': 0,
            'score_type': 0,
            'wta_k': 2,
        }
        
        for key, expected in expected_values.items():
            actual = params[key]
            if actual == expected:
                print(f"✓ {key}: {actual} (matches TeleSculptor)")
            else:
                print(f"✗ {key}: {actual} (expected {expected})")
                return False
        
        # Test detector creation
        detector = create_orb_detector()
        print(f"✓ Detector created successfully: {type(detector).__name__}")
        
        # Test parameter validation
        valid, errors = validate_orb_parameters(params)
        if valid:
            print("✓ Parameter validation passed")
        else:
            print(f"✗ Parameter validation failed: {errors}")
            return False
        
        # Test presets
        fast_preset = ORBDetectorConfig.get_fast_preset()
        quality_preset = ORBDetectorConfig.get_quality_preset()
        performance_preset = ORBDetectorConfig.get_performance_preset()
        
        print(f"✓ Fast preset: {fast_preset['n_features']} features")
        print(f"✓ Quality preset: {quality_preset['n_features']} features")
        print(f"✓ Performance preset: {performance_preset['n_features']} features")
        
        return True
        
    except Exception as e:
        print(f"✗ ORB detector config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_feature_tracker_config():
    """Test feature tracker configuration."""
    print("\n=== Testing Feature Tracker Configuration ===")
    
    try:
        from burn_out.app.features.config.feature_tracker_config import (
            FeatureTrackerConfig, create_telesculptor_config, validate_tracker_config
        )
        
        # Test GUI configuration
        gui_config = FeatureTrackerConfig.create_gui_config()
        print(f"✓ GUI config created: max_frames={gui_config['max_frames']}")
        
        # Test tracker configuration
        tracker_config = FeatureTrackerConfig.create_tracker_config()
        print(f"✓ Tracker config created: type={tracker_config['type']}")
        
        # Test full configuration
        full_config = create_telesculptor_config()
        print(f"✓ Full TeleSculptor config created with {len(full_config)} sections")
        
        # Validate configuration
        valid, errors = validate_tracker_config(full_config)
        if valid:
            print("✓ Tracker configuration validation passed")
        else:
            print(f"✗ Tracker configuration validation failed: {errors}")
            return False
        
        # Test presets
        fast_config = FeatureTrackerConfig.get_fast_preset()
        quality_config = FeatureTrackerConfig.get_quality_preset()
        
        print(f"✓ Fast preset: {fast_config['gui']['max_frames']} max frames")
        print(f"✓ Quality preset: {quality_config['gui']['max_frames']} max frames")
        
        return True
        
    except Exception as e:
        print(f"✗ Feature tracker config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_module_imports():
    """Test configuration module imports."""
    print("\n=== Testing Configuration Module Imports ===")
    
    try:
        from burn_out.app.features.config import (
            ORBDetectorConfig,
            create_orb_detector,
            get_telesculptor_preset,
            get_fast_preset,
        )
        
        print("✓ Main configuration classes imported")
        
        # Test convenience functions
        detector = create_orb_detector()
        preset = get_telesculptor_preset()
        fast = get_fast_preset()
        
        print("✓ Convenience functions work")
        print(f"✓ TeleSculptor preset: {preset['detector']['n_features']} features")
        print(f"✓ Fast preset: {fast['detector']['n_features']} features")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration module import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase0_compatibility():
    """Test compatibility with Phase 0 validation approach."""
    print("\n=== Testing Phase 0 Compatibility ===")
    
    try:
        from burn_out.app.features.config import create_orb_detector
        from kwiver.vital.config import empty_config
        
        # Create detector using Phase 0 approach (manual config)
        import kwiver.vital.algo as kva
        manual_detector = kva.DetectFeatures.create("ocv_ORB")
        manual_config = empty_config()
        manual_config.set_value("n_features", "500")
        manual_config.set_value("scale_factor", "1.2")
        manual_config.set_value("n_levels", "8")
        manual_config.set_value("fast_threshold", "20")
        manual_detector.set_configuration(manual_config)
        
        # Create detector using our configuration system
        config_detector = create_orb_detector()
        
        # Both should have same type
        assert type(manual_detector).__name__ == type(config_detector).__name__
        print("✓ Configuration system produces same detector type as Phase 0")
        
        # Test that our approach is equivalent but cleaner
        telesculptor_detector = create_orb_detector(
            n_features=500,
            scale_factor=1.2,
            n_levels=8,
            fast_threshold=20
        )
        print("✓ Configuration system provides cleaner API than manual approach")
        
        return True
        
    except Exception as e:
        print(f"✗ Phase 0 compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all configuration system tests."""
    print("🔧 PHASE 1A: CONFIGURATION SYSTEM TESTING")
    print("=" * 50)
    
    tests = [
        test_kwiver_integration,
        test_orb_detector_config,
        test_feature_tracker_config,
        test_config_module_imports,
        test_phase0_compatibility,
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
        print("✅ PHASE 1A CONFIGURATION SYSTEM: READY FOR PHASE 1B")
        return True
    else:
        print("❌ PHASE 1A CONFIGURATION SYSTEM: NEEDS FIXES")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)