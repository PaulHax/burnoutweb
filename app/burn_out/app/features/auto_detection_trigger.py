"""
Auto Feature Detection Trigger
Simple module to trigger feature detection after metadata loading completes.

This module provides a way to automatically start feature detection
following the VideoImporter callback pattern used in core.py.
"""

import asyncio
from typing import Optional, Callable
from pathlib import Path

from kwiver.vital import vital_logging
from .track_features_service import FeatureTrackingService
from .feature_storage import FeatureDataManager
from .config import ORBDetectorConfig

logger = vital_logging.getLogger(__name__)


def should_auto_detect_features(video_path: str, feature_manager: FeatureDataManager) -> bool:
    """Check if we should automatically detect features for this video."""
    try:
        video_basename = Path(video_path).stem
        detection_results = feature_manager.load_detection_results(video_basename)
        
        if detection_results and detection_results.get('success', False):
            frame_count = len(detection_results.get('frame_features', {}))
            if frame_count > 0:
                logger.info(f"Found existing features for {video_basename}: {frame_count} frames")
                return False
        
        logger.info(f"No existing features found for {video_basename}")
        return True
        
    except Exception as e:
        logger.warning(f"Error checking existing features: {e}")
        return False


async def trigger_feature_detection(
    video_path: str,
    video_config_path: str,
    feature_manager: FeatureDataManager,
    progress_callback: Optional[Callable] = None,
    completion_callback: Optional[Callable] = None
) -> bool:
    """
    Trigger automatic feature detection for a video.
    
    Args:
        video_path: Path to video file
        video_config_path: Path to KWIVER video reader config
        feature_manager: Feature storage manager
        progress_callback: Optional progress callback
        completion_callback: Optional completion callback
        
    Returns:
        bool: True if detection was started
    """
    try:
        # Check if we should auto-detect
        if not should_auto_detect_features(video_path, feature_manager):
            return False
        
        logger.info(f"Starting automatic feature detection for {video_path}")
        
        # Use fast preset for automatic detection (good balance of speed/quality)
        config_params = ORBDetectorConfig.get_fast_preset()
        
        # Wrap progress callback to add auto-detection context
        def auto_progress_callback(data):
            auto_data = {
                **data,
                'auto_detection': True,
                'source': 'metadata_complete_trigger'
            }
            
            if progress_callback:
                if asyncio.iscoroutinefunction(progress_callback):
                    asyncio.create_task(progress_callback(auto_data))
                else:
                    progress_callback(auto_data)
        
        # Wrap completion callback
        def auto_completion_callback(results):
            if results.get('success', False):
                summary = results.get('summary', {})
                frames = summary.get('total_frames_processed', 0)
                features = summary.get('total_features_detected', 0)
                logger.info(f"Auto feature detection completed: {frames} frames, {features} features")
            else:
                error = results.get('error', 'Unknown error')
                logger.error(f"Auto feature detection failed: {error}")
            
            if completion_callback:
                if asyncio.iscoroutinefunction(completion_callback):
                    asyncio.create_task(completion_callback(results))
                else:
                    completion_callback(results)
        
        # Create and start feature detection service
        service = FeatureTrackingService(
            progress_callback=auto_progress_callback,
            completion_callback=auto_completion_callback
        )
        
        service.detect_features(video_path, video_config_path, config_params)
        return True
        
    except Exception as e:
        logger.error(f"Failed to trigger feature detection: {e}")
        return False