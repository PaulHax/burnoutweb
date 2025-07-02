"""
Core.py Integration Patch
Shows exactly how to integrate auto feature detection into core.py

INSTRUCTIONS FOR INTEGRATION:
1. Add the imports at the top of core.py
2. Add the feature manager initialization in __init__
3. Add current_video_path tracking in open_file
4. Extend the on_metadata_loaded method
5. Add the _trigger_auto_features helper method
"""

# ================================
# 1. ADD THESE IMPORTS TO TOP OF core.py
# ================================
"""
Add these imports after the existing imports in core.py:

from .features.feature_storage import FeatureDataManager
from .features.auto_detection_trigger import trigger_feature_detection
import asyncio
"""

# ================================
# 2. ADD TO BurnOutApp.__init__ METHOD
# ================================
"""
Add these lines in the __init__ method after self.scene = Scene(self.server):

        # Feature detection setup
        self.feature_manager = FeatureDataManager()
        self.current_video_path = None
        logger.info("Feature detection system initialized")
"""

# ================================
# 3. MODIFY open_file METHOD
# ================================
"""
In the open_file method, add this line after the file_to_load check:

    def open_file(self, file_to_load=None):
        if file_to_load is None:
            return
        
        # Store video path for feature detection
        self.current_video_path = file_to_load
        
        logger.debug("open file")
        # ... rest of existing code remains the same ...
"""

# ================================
# 4. MODIFY on_metadata_loaded METHOD
# ================================
"""
Replace the existing on_metadata_loaded method with:

    def on_metadata_loaded(self, metadata):
        self.scene.set_metadata(metadata)
        
        # Trigger automatic feature detection
        if self.current_video_path:
            asyncio.create_task(self._trigger_auto_features())
        else:
            logger.warning("No video path available for auto feature detection")
"""

# ================================
# 5. ADD NEW HELPER METHOD
# ================================
"""
Add this new method to the BurnOutApp class:

    async def _trigger_auto_features(self):
        '''Trigger automatic feature detection after metadata loading.'''
        try:
            success = await trigger_feature_detection(
                video_path=self.current_video_path,
                feature_manager=self.feature_manager,
                progress_callback=self._on_feature_progress,
                completion_callback=self._on_feature_completion
            )
            
            if success:
                logger.info("Automatic feature detection started")
            else:
                logger.info("Feature detection not needed (features already exist)")
                
        except Exception as e:
            logger.error(f"Error triggering automatic feature detection: {e}")
    
    def _on_feature_progress(self, progress_data):
        '''Handle feature detection progress updates.'''
        status = progress_data.get('status', 'unknown')
        message = progress_data.get('message', '')
        
        if status == 'frame_processed':
            frame_num = progress_data.get('frame_number', 0)
            features_count = progress_data.get('features_count', 0)
            progress_pct = progress_data.get('progress', 0) * 100
            logger.debug(f"Feature detection: Frame {frame_num}, {features_count} features ({progress_pct:.1f}%)")
        else:
            logger.info(f"Feature detection {status}: {message}")
    
    def _on_feature_completion(self, results):
        '''Handle feature detection completion.'''
        if results.get('success', False):
            summary = results.get('summary', {})
            frames = summary.get('total_frames_processed', 0)
            features = summary.get('total_features_detected', 0)
            avg_features = summary.get('average_features_per_frame', 0)
            
            logger.info(f"Feature detection completed: {frames} frames, {features} total features, {avg_features:.1f} avg per frame")
            
            # TODO: Integrate with scene and visualization
            # self.scene could be notified of new features here
            
        else:
            error = results.get('error', 'Unknown error')
            logger.error(f"Feature detection failed: {error}")
"""

# ================================
# COMPLETE INTEGRATION EXAMPLE
# ================================

def show_complete_integration_example():
    """
    This shows what the key parts of core.py would look like after integration.
    This is for reference - don't copy this entire function.
    """
    
    class BurnOutApp:
        def __init__(self, server=None):
            # ... existing initialization ...
            
            # Feature detection setup (NEW)
            self.feature_manager = FeatureDataManager()
            self.current_video_path = None
            logger.info("Feature detection system initialized")
        
        def open_file(self, file_to_load=None):
            if file_to_load is None:
                return
            
            # Store video path for feature detection (NEW)
            self.current_video_path = file_to_load
            
            logger.debug("open file")
            logger.debug(f" => {file_to_load=}")
            # ... rest of existing code unchanged ...
        
        def on_metadata_loaded(self, metadata):
            self.scene.set_metadata(metadata)
            
            # Trigger automatic feature detection (NEW)
            if self.current_video_path:
                asyncio.create_task(self._trigger_auto_features())
            else:
                logger.warning("No video path available for auto feature detection")
        
        async def _trigger_auto_features(self):
            """NEW METHOD - Trigger automatic feature detection."""
            try:
                success = await trigger_feature_detection(
                    video_path=self.current_video_path,
                    feature_manager=self.feature_manager,
                    progress_callback=self._on_feature_progress,
                    completion_callback=self._on_feature_completion
                )
                
                if success:
                    logger.info("Automatic feature detection started")
                else:
                    logger.info("Feature detection not needed (features already exist)")
                    
            except Exception as e:
                logger.error(f"Error triggering automatic feature detection: {e}")
        
        def _on_feature_progress(self, progress_data):
            """NEW METHOD - Handle feature detection progress."""
            status = progress_data.get('status', 'unknown')
            message = progress_data.get('message', '')
            
            if status == 'frame_processed':
                frame_num = progress_data.get('frame_number', 0)
                features_count = progress_data.get('features_count', 0)
                progress_pct = progress_data.get('progress', 0) * 100
                logger.debug(f"Features: Frame {frame_num}, {features_count} features ({progress_pct:.1f}%)")
            else:
                logger.info(f"Feature detection {status}: {message}")
        
        def _on_feature_completion(self, results):
            """NEW METHOD - Handle feature detection completion."""
            if results.get('success', False):
                summary = results.get('summary', {})
                frames = summary.get('total_frames_processed', 0)
                features = summary.get('total_features_detected', 0)
                avg_features = summary.get('average_features_per_frame', 0)
                
                logger.info(f"Feature detection completed: {frames} frames, {features} total features, {avg_features:.1f} avg per frame")
                
                # Future: Integrate with scene and visualization
                # Could call scene integration functions here
                
            else:
                error = results.get('error', 'Unknown error')
                logger.error(f"Feature detection failed: {error}")


# ================================
# TESTING THE INTEGRATION
# ================================

def test_integration():
    """
    After making the changes to core.py, test with:
    
    1. Start burnoutweb: burn-out --data /path/to/video.mp4
    2. Check logs for: "Feature detection system initialized"
    3. When video loads, check for: "Automatic feature detection started"
    4. Monitor progress: "Features: Frame X, Y features (Z%)"
    5. Check completion: "Feature detection completed: X frames, Y total features"
    """
    pass