"""
Feature Detection Configuration Module

This module provides TeleSculptor-compatible configuration for feature detection
and tracking algorithms in burnoutweb.

Main Components:
- ORBDetectorConfig: ORB feature detector configuration
- FeatureTrackerConfig: Complete tracking pipeline configuration
- Presets: Fast, Quality, Performance, and TeleSculptor configurations
"""

from .orb_detector_config import (
    ORBDetectorConfig,
    create_orb_detector,
    create_orb_config,
    validate_orb_parameters,
)

from .feature_tracker_config import (
    FeatureTrackerConfig,
    FeatureMatcherConfig,
    LoopClosureConfig,
    create_telesculptor_config,
    create_burnoutweb_config,
    validate_tracker_config,
)

# Convenience exports for common usage patterns
__all__ = [
    # Main configuration classes
    'ORBDetectorConfig',
    'FeatureTrackerConfig',
    'FeatureMatcherConfig', 
    'LoopClosureConfig',
    
    # Convenience functions
    'create_orb_detector',
    'create_orb_config',
    'create_telesculptor_config',
    'create_burnoutweb_config',
    
    # Validation functions
    'validate_orb_parameters',
    'validate_tracker_config',
    
    # Quick access to presets
    'get_telesculptor_preset',
    'get_fast_preset',
    'get_quality_preset',
    'get_performance_preset',
]

def get_telesculptor_preset():
    """Get exact TeleSculptor configuration preset."""
    return FeatureTrackerConfig.get_telesculptor_preset()

def get_fast_preset():
    """Get performance-optimized configuration preset.""" 
    return FeatureTrackerConfig.get_fast_preset()

def get_quality_preset():
    """Get high-quality configuration preset."""
    return FeatureTrackerConfig.get_quality_preset()

def get_performance_preset():
    """Get real-time performance configuration preset."""
    return FeatureTrackerConfig.get_performance_preset()


# Version info
__version__ = "1.0.0"
__telesculptor_compatibility__ = "TeleSculptor 1.6+"
__kwiver_compatibility__ = "KWIVER 1.6+"