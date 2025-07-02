"""
ORB Feature Detector Configuration
Port of TeleSculptor's ocv_ORB_detector_descriptor.conf to Python.

This configuration provides the exact same ORB parameters used by TeleSculptor
for consistent feature detection across both applications.

Based on validated Phase 0 results: 500 features per frame on real aerial video.
"""

from kwiver.vital.config import empty_config
import kwiver.vital.algo as kva


class ORBDetectorConfig:
    """ORB detector configuration matching TeleSculptor's parameters exactly."""
    
    # TeleSculptor's exact ORB parameters from ocv_ORB_detector_descriptor.conf
    # VALIDATED: These parameters successfully detected 500 features per frame
    DEFAULT_PARAMS = {
        # The maximum number of features to retain
        'n_features': 500,
        
        # Pyramid decimation ratio, greater than 1
        # scaleFactor==2 means classical pyramid, but degrades matching scores
        # Too close to 1 means more pyramid levels needed, affecting speed
        'scale_factor': 1.2,
        
        # The number of pyramid levels
        # Smallest level will have linear size = input_size/pow(scale_factor, n_levels)
        'n_levels': 8,
        
        # Threshold for FAST corner detector (undocumented but critical)
        'fast_threshold': 20,
        
        # Border where features are not detected (should match patch_size)
        'edge_threshold': 31,
        
        # Size of patch used by oriented BRIEF descriptor
        # On smaller pyramid layers, perceived image area covered will be larger
        'patch_size': 31,
        
        # First pyramid level (should be 0 in current implementation)
        'first_level': 0,
        
        # Feature scoring method:
        # 0 = HARRIS_SCORE (default) - Harris algorithm ranks features, more stable
        # 1 = FAST_SCORE - slightly less stable but faster to compute
        'score_type': 0,
        
        # Number of points that produce each element of oriented BRIEF descriptor
        # 2 = random point pair comparison (0/1 response)
        # 3 = 3 random points, output winner index (0,1,2) - needs NORM_HAMMING2
        # 4 = 4 random points (0,1,2,3) - also needs NORM_HAMMING2
        'wta_k': 2,
    }
    
    @classmethod
    def create_config(cls, **overrides):
        """
        Create KWIVER config for ORB detector with TeleSculptor parameters.
        
        Args:
            **overrides: Override any default parameters
            
        Returns:
            kwiver.vital.config.Config: Configured ORB detector config
        """
        config = empty_config()
        
        # Merge defaults with any overrides
        params = {**cls.DEFAULT_PARAMS, **overrides}
        
        # Set all ORB parameters as strings (KWIVER requirement)
        for key, value in params.items():
            config.set_value(key, str(value))
            
        return config
    
    @classmethod
    def create_detector(cls, **overrides):
        """
        Create and configure ORB detector with TeleSculptor parameters.
        
        Args:
            **overrides: Override any default parameters
            
        Returns:
            kwiver.vital.algo.DetectFeatures: Configured ORB detector
        """
        detector = kva.DetectFeatures.create("ocv_ORB")
        config = cls.create_config(**overrides)
        detector.set_configuration(config)
        
        return detector
    
    @classmethod
    def get_telesculptor_preset(cls):
        """Get the exact TeleSculptor ORB configuration."""
        return cls.DEFAULT_PARAMS.copy()
    
    @classmethod
    def get_fast_preset(cls):
        """Get a faster ORB configuration (fewer features, fewer levels)."""
        return {
            **cls.DEFAULT_PARAMS,
            'n_features': 250,
            'n_levels': 6,
            'fast_threshold': 25,  # Slightly higher threshold for speed
        }
    
    @classmethod 
    def get_quality_preset(cls):
        """Get a higher quality ORB configuration (more features, more levels)."""
        return {
            **cls.DEFAULT_PARAMS,
            'n_features': 1000,
            'n_levels': 10,
            'fast_threshold': 15,  # Lower threshold for more features
        }
    
    @classmethod
    def get_performance_preset(cls):
        """Get a performance-optimized configuration for real-time use."""
        return {
            **cls.DEFAULT_PARAMS,
            'n_features': 150,
            'n_levels': 4,
            'fast_threshold': 30,
            'scale_factor': 1.5,  # Larger scale factor = fewer levels needed
        }


def create_orb_detector(**overrides):
    """
    Convenience function to create ORB detector with TeleSculptor parameters.
    
    Usage:
        detector = create_orb_detector()  # TeleSculptor defaults
        detector = create_orb_detector(n_features=1000)  # Override features
        detector = create_orb_detector(**ORBDetectorConfig.get_fast_preset())
    
    Returns:
        kwiver.vital.algo.DetectFeatures: Configured ORB detector
    """
    return ORBDetectorConfig.create_detector(**overrides)


def create_orb_config(**overrides):
    """
    Convenience function to create ORB config with TeleSculptor parameters.
    
    Usage:
        config = create_orb_config()
        config = create_orb_config(scale_factor=1.5)
        config = create_orb_config(**ORBDetectorConfig.get_quality_preset())
    
    Returns:
        kwiver.vital.config.Config: Configured ORB config object
    """
    return ORBDetectorConfig.create_config(**overrides)


def validate_orb_parameters(params):
    """
    Validate ORB parameters are within acceptable ranges.
    
    Args:
        params (dict): ORB parameter dictionary
        
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # Validate feature count
    if params.get('n_features', 0) <= 0:
        errors.append("n_features must be positive")
    if params.get('n_features', 0) > 10000:
        errors.append("n_features should not exceed 10000 for performance")
    
    # Validate scale factor
    scale_factor = params.get('scale_factor', 1.2)
    if scale_factor <= 1.0:
        errors.append("scale_factor must be greater than 1.0")
    if scale_factor >= 3.0:
        errors.append("scale_factor >= 3.0 may degrade feature matching")
    
    # Validate pyramid levels
    n_levels = params.get('n_levels', 8)
    if n_levels < 1:
        errors.append("n_levels must be at least 1")
    if n_levels > 15:
        errors.append("n_levels > 15 may cause excessive computation")
    
    # Validate thresholds
    if params.get('fast_threshold', 20) <= 0:
        errors.append("fast_threshold must be positive")
    if params.get('edge_threshold', 31) <= 0:
        errors.append("edge_threshold must be positive")
    
    # Validate patch size
    patch_size = params.get('patch_size', 31)
    if patch_size < 15 or patch_size > 63:
        errors.append("patch_size should be between 15 and 63")
    
    # Validate score type
    score_type = params.get('score_type', 0)
    if score_type not in [0, 1]:
        errors.append("score_type must be 0 (HARRIS) or 1 (FAST)")
    
    # Validate WTA_K
    wta_k = params.get('wta_k', 2)
    if wta_k not in [2, 3, 4]:
        errors.append("wta_k must be 2, 3, or 4")
    
    return len(errors) == 0, errors