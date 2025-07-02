"""
Feature Tracker Configuration
Port of TeleSculptor's core_feature_tracker.conf structure to Python.

This configuration mirrors TeleSculptor's complete feature tracking pipeline:
detector → descriptor → matcher → loop_closer → feature_io

Based on TeleSculptor's gui_track_features.conf and core_feature_tracker.conf.
"""

from .orb_detector_config import ORBDetectorConfig
from kwiver.vital.config import empty_config


class FeatureTrackerConfig:
    """Feature tracker configuration matching TeleSculptor's pipeline exactly."""
    
    # TeleSculptor's gui_track_features.conf defaults
    DEFAULT_GUI_CONFIG = {
        # Image converter type (bypass = no conversion)
        'image_converter_type': 'bypass',
        
        # Descriptor configuration
        'descriptor_type': 'ocv_ORB',
        'descriptor_binary': True,
        
        # Maximum frames for GUI processing (TeleSculptor default)
        # Tracker will choose frames distributed over the video
        'max_frames': 500,
    }
    
    # TeleSculptor's core_feature_tracker.conf structure
    DEFAULT_TRACKER_CONFIG = {
        # Feature tracker algorithm type
        'type': 'core',
        
        # Feature detection configuration
        'detector_type': 'core_nonmax',  # Non-maximum suppression detector
        'detector_backend': 'ocv_ORB',   # ORB as the backend detector
        
        # Descriptor extraction configuration  
        'descriptor_type': 'ocv_ORB',    # Use ORB descriptors
        
        # Feature matching configuration
        'matcher_type': 'core_fmatrix_guided',  # F-matrix guided matching
        
        # Loop closure configuration
        'loop_closer_type': 'keyframe',  # Keyframe-based loop closure
        
        # Feature I/O configuration
        'feature_io_type': 'core',       # Core feature I/O algorithm
        
        # Output directory for feature files (TeleSculptor standard)
        'features_dir': 'results/features',
    }
    
    @classmethod
    def create_gui_config(cls, **overrides):
        """
        Create GUI-level configuration (gui_track_features.conf equivalent).
        
        Args:
            **overrides: Override any default parameters
            
        Returns:
            dict: GUI configuration dictionary
        """
        return {**cls.DEFAULT_GUI_CONFIG, **overrides}
    
    @classmethod
    def create_tracker_config(cls, **overrides):
        """
        Create tracker-level configuration (core_feature_tracker.conf equivalent).
        
        Args:
            **overrides: Override any default parameters
            
        Returns:
            dict: Tracker configuration dictionary
        """
        config = {**cls.DEFAULT_TRACKER_CONFIG, **overrides}
        
        # Add detector configuration based on descriptor type
        descriptor_type = config.get('descriptor_type', 'ocv_ORB')
        if descriptor_type == 'ocv_ORB':
            config['detector_config'] = ORBDetectorConfig.get_telesculptor_preset()
        
        return config
    
    @classmethod
    def create_full_config(cls, **overrides):
        """
        Create complete configuration combining GUI and tracker levels.
        
        Args:
            **overrides: Override any parameters at any level
            
        Returns:
            dict: Complete feature tracking configuration
        """
        # Split overrides by component
        gui_overrides = {}
        tracker_overrides = {}
        detector_overrides = {}
        
        for key, value in overrides.items():
            if key in cls.DEFAULT_GUI_CONFIG:
                gui_overrides[key] = value
            elif key in cls.DEFAULT_TRACKER_CONFIG:
                tracker_overrides[key] = value
            elif key in ORBDetectorConfig.DEFAULT_PARAMS:
                detector_overrides[key] = value
        
        # Create hierarchical configuration
        full_config = {
            'gui': cls.create_gui_config(**gui_overrides),
            'tracker': cls.create_tracker_config(**tracker_overrides),
            'detector': ORBDetectorConfig.get_telesculptor_preset()
        }
        
        # Apply detector overrides
        if detector_overrides:
            full_config['detector'].update(detector_overrides)
        
        return full_config
    
    @classmethod
    def get_telesculptor_preset(cls):
        """Get the exact TeleSculptor feature tracking configuration."""
        return cls.create_full_config()
    
    @classmethod
    def get_fast_preset(cls):
        """Get a performance-optimized configuration."""
        return cls.create_full_config(
            max_frames=250,                    # Fewer frames for speed
            **ORBDetectorConfig.get_fast_preset()  # Fast detector settings
        )
    
    @classmethod
    def get_quality_preset(cls):
        """Get a high-quality configuration."""
        return cls.create_full_config(
            max_frames=1000,                   # More frames for quality
            **ORBDetectorConfig.get_quality_preset()  # Quality detector settings
        )
    
    @classmethod
    def get_performance_preset(cls):
        """Get a real-time performance configuration."""
        return cls.create_full_config(
            max_frames=100,                    # Minimal frames for real-time
            **ORBDetectorConfig.get_performance_preset()  # Performance detector
        )


class FeatureMatcherConfig:
    """Configuration for TeleSculptor's F-matrix guided feature matcher."""
    
    # Based on core_fmatrix_guided_feature_matcher.conf
    DEFAULT_PARAMS = {
        # F-matrix estimation algorithm
        'fmatrix_estimator_type': 'core_lms',  # Least median of squares
        
        # Feature matcher for initial correspondence
        'feature_matcher_type': 'core_homography_guided',
        
        # Inlier selection threshold
        'inlier_threshold': 1.0,
        
        # Minimum number of inliers required
        'min_inliers': 20,
        
        # Maximum iterations for RANSAC
        'max_iterations': 1000,
    }
    
    @classmethod
    def create_config(cls, **overrides):
        """Create F-matrix guided matcher configuration."""
        return {**cls.DEFAULT_PARAMS, **overrides}


class LoopClosureConfig:
    """Configuration for TeleSculptor's keyframe-based loop closure."""
    
    # Based on loop_closer_keyframe.conf  
    DEFAULT_PARAMS = {
        # Loop closure algorithm type
        'type': 'keyframe',
        
        # Keyframe selection parameters
        'keyframe_selection': 'distributed',  # Distributed keyframe selection
        'min_keyframe_separation': 10,        # Minimum frames between keyframes
        'max_keyframes': 100,                 # Maximum number of keyframes
        
        # Loop detection parameters
        'loop_detection_threshold': 0.7,     # Similarity threshold for loops
        'min_loop_separation': 30,           # Minimum frames for valid loop
        
        # Bundle adjustment after loop closure
        'bundle_adjustment': True,           # Enable bundle adjustment
        'ba_iterations': 50,                # BA iteration limit
    }
    
    @classmethod
    def create_config(cls, **overrides):
        """Create keyframe loop closure configuration."""
        return {**cls.DEFAULT_PARAMS, **overrides}


def create_telesculptor_config(**overrides):
    """
    Convenience function to create complete TeleSculptor-compatible configuration.
    
    Usage:
        config = create_telesculptor_config()  # Exact TeleSculptor defaults
        config = create_telesculptor_config(max_frames=1000, n_features=1000)
    
    Returns:
        dict: Complete feature tracking configuration
    """
    return FeatureTrackerConfig.create_full_config(**overrides)


def create_burnoutweb_config(**overrides):
    """
    Create burnoutweb-optimized configuration for web performance.
    
    Balances quality with performance for web-based usage.
    
    Returns:
        dict: Burnoutweb-optimized configuration
    """
    burnoutweb_defaults = {
        'max_frames': 300,        # Moderate frame count for web
        'n_features': 400,        # Balanced feature count
        'n_levels': 6,           # Fewer pyramid levels for speed
        'fast_threshold': 25,    # Slightly higher threshold
    }
    
    return FeatureTrackerConfig.create_full_config(**burnoutweb_defaults, **overrides)


def validate_tracker_config(config):
    """
    Validate complete tracker configuration for consistency.
    
    Args:
        config (dict): Complete tracker configuration
        
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # Validate GUI configuration
    gui_config = config.get('gui', {})
    max_frames = gui_config.get('max_frames', 500)
    if max_frames <= 0:
        errors.append("max_frames must be positive")
    if max_frames > 5000:
        errors.append("max_frames > 5000 may cause memory issues")
    
    # Validate descriptor type consistency
    gui_desc_type = gui_config.get('descriptor_type', 'ocv_ORB')
    tracker_desc_type = config.get('tracker', {}).get('descriptor_type', 'ocv_ORB')
    if gui_desc_type != tracker_desc_type:
        errors.append("Descriptor type mismatch between GUI and tracker configs")
    
    # Validate detector parameters if present
    detector_config = config.get('detector', {})
    if detector_config:
        from .orb_detector_config import validate_orb_parameters
        detector_valid, detector_errors = validate_orb_parameters(detector_config)
        if not detector_valid:
            errors.extend([f"Detector: {err}" for err in detector_errors])
    
    # Validate features directory
    features_dir = config.get('tracker', {}).get('features_dir', '')
    if not features_dir:
        errors.append("features_dir must be specified")
    
    return len(errors) == 0, errors