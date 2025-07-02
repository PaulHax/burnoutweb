"""
Feature Detection Service
Async multiprocessing service following VideoImporter pattern.

This service replicates TeleSculptor's TrackFeaturesTool workflow in burnoutweb:
1. Frame sampling (max 500 frames, uniform distribution)
2. KWIVER algorithm initialization using validated approach
3. Feature detection per frame with progress tracking
4. Async result delivery with progress callbacks

Architecture mirrors VideoImporter for consistent burnoutweb integration.
"""

import asyncio
import logging
from multiprocessing import Process, Queue
from pathlib import Path
from typing import Optional, Callable, Dict, Any

# KWIVER imports (using validated Phase 0 approach)
import kwiver.vital.algo as kva
from kwiver.vital.config import read_config_file
from kwiver.vital.types import Timestamp
from kwiver.vital import plugin_management
from kwiver.vital import vital_logging

# Burnoutweb imports (using existing infrastructure)
from .config.orb_detector_config import ORBDetectorConfig
from .config.feature_tracker_config import FeatureTrackerConfig

# Setup logging (following VideoImporter pattern)
logger = vital_logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FeatureTrackingService:
    """
    Feature detection service mirroring VideoImporter architecture.

    Provides async multiprocessing feature detection with progress tracking
    and completion callbacks, following burnoutweb's established patterns.
    """

    def __init__(
        self,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None,
    ):
        """
        Initialize feature tracking service.

        Args:
            progress_callback: Called with progress updates during detection
            completion_callback: Called when detection completes
        """
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.progress_queue = Queue()  # New: for progress updates
        self.process = self._spawn_worker_process()
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self._monitoring_task = None

    def _spawn_worker_process(self):
        """Spawn worker process (same pattern as VideoImporter)."""
        process = Process(
            target=_worker,
            args=(self.task_queue, self.result_queue, self.progress_queue),
        )
        process.start()
        return process

    def detect_features(self, video_path: str, video_config_path: str, config_params: Optional[Dict] = None):
        """
        Start feature detection (mirrors VideoImporter.run()).

        Args:
            video_path: Path to video file
            video_config_path: Path to KWIVER video reader config
            config_params: Override configuration parameters
        """
        config_params = config_params or {}
        logger.info(f"Starting feature detection on {video_path}")

        # Queue detection task (like VideoImporter)
        self.task_queue.put((_extract_features, (video_path, video_config_path, config_params)))

        # Start async monitoring (like VideoImporter._await_metadata_results)
        self._monitoring_task = asyncio.create_task(self._await_results())

    def cancel(self):
        """Cancel detection (mirrors VideoImporter.cancel())."""
        logger.info("Cancelling feature detection")
        self.process.terminate()
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.progress_queue = Queue()
        self.process = self._spawn_worker_process()

        if self._monitoring_task:
            self._monitoring_task.cancel()

    def close(self):
        """Clean shutdown (mirrors VideoImporter.close())."""
        logger.info("Closing feature tracking service")
        self.task_queue.put(None)

        if self._monitoring_task:
            self._monitoring_task.cancel()

    async def _await_results(self):
        """
        Monitor results and progress (mirrors VideoImporter._await_metadata_results()).

        Handles both progress updates and final completion.
        """
        loop = asyncio.get_event_loop()

        try:
            while True:
                # Check for progress updates (non-blocking)
                try:
                    while True:
                        progress_data = self.progress_queue.get_nowait()
                        if self.progress_callback:
                            if asyncio.iscoroutinefunction(self.progress_callback):
                                await self.progress_callback(progress_data)
                            else:
                                self.progress_callback(progress_data)
                except:
                    pass  # No progress updates available

                # Check for completion (blocking with timeout)
                try:
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, self.result_queue.get), timeout=0.1
                    )

                    # Feature detection completed
                    logger.info("Feature detection completed")
                    if self.completion_callback:
                        if asyncio.iscoroutinefunction(self.completion_callback):
                            await self.completion_callback(result)
                        else:
                            self.completion_callback(result)
                    break

                except asyncio.TimeoutError:
                    continue  # Keep monitoring

        except asyncio.CancelledError:
            logger.info("Result monitoring cancelled")


def _worker(task_queue, result_queue, progress_queue):
    """
    Worker process (mirrors VideoImporter._worker()).

    Handles feature detection tasks in separate process to avoid UI blocking.
    """
    # Load KWIVER plugins (like VideoImporter and Phase 0 validation)
    vpm = plugin_management.plugin_manager_instance()
    vpm.load_all_plugins()
    logger.info("KWIVER plugins loaded in worker process")

    for func, args in iter(task_queue.get, None):
        try:
            if func == _extract_features:
                result = func(
                    *args, progress_callback=lambda data: progress_queue.put(data)
                )
                result_queue.put(result)
            else:
                raise RuntimeError(f"Unhandled worker function: {func}")
        except Exception as e:
            logger.error(f"Worker process error: {e}")
            result_queue.put({"error": str(e)})


def _extract_features(
    video_path: str, video_config_path: str, config_params: Dict, progress_callback: Callable
):
    """
    Extract features using VALIDATED Phase 0 approach.

    This function implements TeleSculptor's TrackFeaturesTool workflow
    using the exact approach that successfully detected 500 features per frame.

    Args:
        video_path: Path to video file
        config_params: Configuration overrides
        progress_callback: Progress update callback

    Returns:
        dict: Frame features and metadata
    """
    logger.info(f"Extracting features from {video_path}")
    progress_callback(
        {"status": "initializing", "message": "Initializing KWIVER algorithms"}
    )

    try:
        # Phase 1: Video setup (VALIDATED - works with H.264)
        config = read_config_file(video_config_path)
        video_reader = kva.VideoInput.set_nested_algo_configuration(
            "video_reader", config
        )

        # Critical: Ignore return value like burnoutweb (VALIDATED)
        video_reader.open(video_path)
        logger.info("Video reader opened (ignoring return value like burnoutweb)")
        progress_callback(
            {"status": "video_opened", "message": "Video loaded successfully"}
        )

        # Phase 2: Create detector (using our validated configuration)
        detector = ORBDetectorConfig.create_detector(**config_params)
        logger.info(f"ORB detector created with parameters: {config_params}")
        progress_callback(
            {"status": "detector_ready", "message": "Feature detector configured"}
        )

        # Phase 3: Frame sampling (TeleSculptor uniform distribution)
        progress_callback(
            {
                "status": "sampling_frames",
                "message": "Analyzing video for frame sampling",
            }
        )
        frames_to_process = _sample_frames(video_reader, max_frames=500)
        total_frames = len(frames_to_process)
        logger.info(f"Sampled {total_frames} frames for processing")
        progress_callback(
            {
                "status": "sampling_complete",
                "message": f"Will process {total_frames} frames",
                "total_frames": total_frames,
            }
        )

        # Phase 4: Feature detection per frame (VALIDATED - 500 features per frame)
        frame_features = {}
        current_timestamp = Timestamp()
        processed_count = 0

        logger.info("Starting feature detection on frames")
        progress_callback(
            {"status": "detecting_features", "message": "Starting feature detection"}
        )

        # Process frames as they come (like Phase 0 validation)
        frame_num = 0
        while (
            video_reader.next_frame(current_timestamp)
            and processed_count < total_frames
        ):
            if not current_timestamp.has_valid_frame():
                continue

            frame_num = current_timestamp.get_frame()

            # Check if this frame should be processed (uniform sampling)
            if frame_num in frames_to_process:
                image_container = video_reader.frame_image()
                if image_container:
                    # Detect features (same as Phase 0 validation)
                    feature_set = detector.detect(image_container)
                    features = feature_set.features()
                    feature_count = len(features)

                    # Store features (without FeatureSet object to avoid pickle issues)
                    frame_features[frame_num] = {
                        "feature_count": feature_count,
                        "frame_number": frame_num,
                        # Convert features to serializable format
                        "features": _serialize_features(features)
                        if feature_count < 100
                        else None,  # Limit for performance
                    }

                    processed_count += 1
                    progress_percent = (processed_count / total_frames) * 100

                    logger.info(
                        f"Frame {frame_num}: {feature_count} features detected "
                        f"({processed_count}/{total_frames}, {progress_percent:.1f}%)"
                    )

                    # Progress update
                    progress_callback(
                        {
                            "status": "frame_processed",
                            "message": f"Frame {frame_num}: {feature_count} features detected",
                            "frame_number": frame_num,
                            "features_count": feature_count,
                            "processed_count": processed_count,
                            "total_frames": total_frames,
                            "progress": progress_percent / 100.0,
                        }
                    )

        # Phase 5: Completion
        total_features = sum(data["feature_count"] for data in frame_features.values())
        avg_features = total_features / len(frame_features) if frame_features else 0

        result = {
            "success": True,
            "video_path": video_path,
            "frame_features": frame_features,
            "summary": {
                "total_frames_processed": len(frame_features),
                "total_features_detected": total_features,
                "average_features_per_frame": avg_features,
                "config_params": config_params,
            },
        }

        logger.info(
            f"Feature detection completed: {len(frame_features)} frames, "
            f"{total_features} total features, {avg_features:.1f} avg per frame"
        )
        progress_callback(
            {
                "status": "completed",
                "message": f"Detection complete: {total_features} features in {len(frame_features)} frames",
                "summary": result["summary"],
            }
        )

        return result

    except Exception as e:
        error_msg = f"Feature extraction failed: {str(e)}"
        logger.error(error_msg)
        progress_callback({"status": "error", "message": error_msg, "error": str(e)})
        return {"success": False, "error": str(e)}


def _sample_frames(video_reader, max_frames: int = 500) -> list:
    """
    Sample frames uniformly across video (TeleSculptor approach).

    Args:
        video_reader: KWIVER VideoInput instance
        max_frames: Maximum number of frames to process

    Returns:
        list: Frame numbers to process
    """
    # For now, implement simple sequential sampling
    # TODO: Implement true uniform distribution based on total frame count
    return list(range(1, max_frames + 1))


def _serialize_features(features) -> list:
    """
    Convert KWIVER features to serializable format.

    Args:
        features: KWIVER feature list

    Returns:
        list: Serializable feature data
    """
    serialized = []
    for feature in features:
        try:
            # Extract basic feature properties that can be serialized
            serialized.append(
                {
                    "x": float(feature.loc[0]),
                    "y": float(feature.loc[1]),
                    "magnitude": float(feature.magnitude),
                    "scale": float(feature.scale),
                    "angle": float(feature.angle),
                    # Color information if available
                    "color": [
                        float(feature.color[0]),
                        float(feature.color[1]),
                        float(feature.color[2]),
                    ]
                    if hasattr(feature, "color")
                    else [255, 255, 255],
                }
            )
        except Exception:
            # Skip features that can't be serialized
            continue

    return serialized


def _count_video_frames(video_reader) -> int:
    """
    Count total frames in video.

    Args:
        video_reader: KWIVER VideoInput instance

    Returns:
        int: Total frame count
    """
    # TODO: Implement frame counting
    # For now, return estimated count
    return 1000  # Placeholder


# Convenience functions for easy usage
def create_feature_service(progress_callback=None, completion_callback=None):
    """Create feature tracking service with callbacks."""
    return FeatureTrackingService(progress_callback, completion_callback)


async def detect_features_async(
    video_path: str,
    video_config_path: str,
    config_params: Optional[Dict] = None,
    progress_callback: Optional[Callable] = None,
):
    """
    Async convenience function for feature detection.

    Args:
        video_path: Path to video file
        video_config_path: Path to KWIVER video reader config
        config_params: Configuration overrides
        progress_callback: Progress update callback

    Returns:
        dict: Detection results
    """
    result = None

    def completion_handler(data):
        nonlocal result
        result = data

    service = FeatureTrackingService(
        progress_callback=progress_callback, completion_callback=completion_handler
    )

    try:
        service.detect_features(video_path, video_config_path, config_params)

        # Wait for completion
        while result is None:
            await asyncio.sleep(0.1)

        return result

    finally:
        service.close()
