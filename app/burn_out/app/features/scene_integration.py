"""
Feature Scene Integration Module
Pure functional programming approach for feature processing.

This module provides pure functions for feature data processing that any caller
can use. It has no knowledge of Scene class or any other specific classes.
All functions are pure - they take inputs and return outputs without side effects.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path

from kwiver.vital import vital_logging

logger = vital_logging.getLogger(__name__)


def extract_video_basename(video_path: str) -> str:
    """
    Extract basename from video path for feature file naming.

    Args:
        video_path: Full path to video file

    Returns:
        str: Video basename
    """
    return Path(video_path).stem


def load_video_features(feature_manager, video_basename: str) -> Dict:
    """
    Load all available features for a video.

    Args:
        feature_manager: Feature storage manager instance
        video_basename: Video file basename

    Returns:
        dict: Feature data with 'frame_features' key or empty dict
    """
    try:
        detection_results = feature_manager.load_detection_results(video_basename)
        if detection_results:
            return {
                "frame_features": detection_results.get("frame_features", {}),
                "summary": detection_results.get("summary", {}),
                "video_basename": video_basename,
                "loaded": True,
            }
        return {
            "frame_features": {},
            "summary": {},
            "video_basename": video_basename,
            "loaded": False,
        }

    except Exception as e:
        logger.error(f"Failed to load features for {video_basename}: {e}")
        return {
            "frame_features": {},
            "summary": {},
            "video_basename": video_basename,
            "loaded": False,
            "error": str(e),
        }


def save_detection_results(feature_manager, detection_results: Dict) -> bool:
    """
    Save detection results using feature manager.

    Args:
        feature_manager: Feature storage manager instance
        detection_results: Results from feature detection service

    Returns:
        bool: Success status
    """
    try:
        return feature_manager.save_detection_results(detection_results)
    except Exception as e:
        logger.error(f"Failed to save detection results: {e}")
        return False


def get_frame_features(feature_tracks: Dict, frame_id: int) -> Optional[Dict]:
    """
    Get features for a specific frame.

    Args:
        feature_tracks: All feature track data (frame_id -> feature_data)
        frame_id: Frame number

    Returns:
        dict: Feature data for frame or None
    """
    return feature_tracks.get(frame_id)


def calculate_feature_summary(feature_tracks: Dict, video_basename: str = "") -> Dict:
    """
    Calculate summary statistics for feature data.

    Args:
        feature_tracks: All feature track data
        video_basename: Video basename (optional)

    Returns:
        dict: Summary statistics
    """
    if not feature_tracks:
        return {
            "total_frames": 0,
            "total_features": 0,
            "average_features_per_frame": 0,
            "video_basename": video_basename,
        }

    total_features = sum(
        data.get("feature_count", 0) for data in feature_tracks.values()
    )

    return {
        "total_frames": len(feature_tracks),
        "total_features": total_features,
        "average_features_per_frame": total_features / len(feature_tracks),
        "video_basename": video_basename,
    }


def merge_feature_tracks(existing_tracks: Dict, new_tracks: Dict) -> Dict:
    """
    Merge new feature tracks with existing tracks.

    Args:
        existing_tracks: Current feature track data
        new_tracks: New feature track data to merge

    Returns:
        dict: Merged feature tracks
    """
    merged = existing_tracks.copy()
    merged.update(new_tracks)
    return merged


def convert_features_to_world_coordinates(
    features: List[Dict], camera_pose: Optional[Dict], local_geo_cs
) -> List[Dict]:
    """
    Convert 2D image features to 3D world coordinates using camera pose.

    Args:
        features: List of 2D feature dictionaries
        camera_pose: Camera pose information (can be None)
        local_geo_cs: Local geographic coordinate system

    Returns:
        list: Features with world coordinates added
    """
    if not features or not camera_pose:
        # Return features without world coordinates
        return [
            {**feature, "world_coords": None, "has_world_coords": False}
            for feature in features
        ]

    world_features = []

    for feature in features:
        try:
            # TODO: Implement actual triangulation logic using camera_pose
            # For now, create placeholder world coordinates structure
            world_feature = {
                **feature,  # Keep original 2D data
                "world_coords": None,  # Placeholder for 3D triangulation
                "has_world_coords": False,
                "geo_converted": True,
            }
            world_features.append(world_feature)

        except Exception as e:
            logger.warning(f"Failed to convert feature to world coordinates: {e}")
            world_features.append(
                {
                    **feature,
                    "world_coords": None,
                    "has_world_coords": False,
                    "geo_converted": False,
                }
            )

    return world_features


def apply_geo_conversion_to_frame(
    frame_features: Dict, camera_pose: Optional[Dict], local_geo_cs
) -> Dict:
    """
    Apply geo-conversion to features for a single frame.

    Args:
        frame_features: Feature data for one frame
        camera_pose: Camera pose for this frame
        local_geo_cs: Local geographic coordinate system

    Returns:
        dict: Frame features with world coordinates added
    """
    if not frame_features:
        return frame_features

    features = frame_features.get("features", [])
    world_features = convert_features_to_world_coordinates(
        features, camera_pose, local_geo_cs
    )

    return {
        **frame_features,
        "world_features": world_features,
        "has_world_coords": bool(camera_pose),
        "geo_converted": True,
    }


def apply_geo_conversion_to_tracks(
    feature_tracks: Dict, camera_map: Dict, local_geo_cs
) -> Dict:
    """
    Apply geo-conversion to all feature tracks.

    Args:
        feature_tracks: Feature track data (frame_id -> feature_data)
        camera_map: Camera pose data indexed by frame
        local_geo_cs: Local geographic coordinate system

    Returns:
        dict: Feature tracks with world coordinates added
    """
    converted_tracks = {}

    for frame_id, feature_data in feature_tracks.items():
        camera_pose = camera_map.get(frame_id)
        converted_tracks[frame_id] = apply_geo_conversion_to_frame(
            feature_data, camera_pose, local_geo_cs
        )

    return converted_tracks


def filter_features_by_quality(
    features: List[Dict], min_magnitude: float = 0.1
) -> List[Dict]:
    """
    Filter features by quality threshold.

    Args:
        features: List of feature dictionaries
        min_magnitude: Minimum feature magnitude threshold

    Returns:
        list: Filtered features
    """
    return [
        feature for feature in features if feature.get("magnitude", 0) >= min_magnitude
    ]


def get_features_in_region(
    features: List[Dict], x_range: Tuple[float, float], y_range: Tuple[float, float]
) -> List[Dict]:
    """
    Get features within a specific image region.

    Args:
        features: List of feature dictionaries
        x_range: (min_x, max_x) range
        y_range: (min_y, max_y) range

    Returns:
        list: Features in the specified region
    """
    min_x, max_x = x_range
    min_y, max_y = y_range

    return [
        feature
        for feature in features
        if (
            min_x <= feature.get("x", 0) <= max_x
            and min_y <= feature.get("y", 0) <= max_y
        )
    ]


def create_frame_context(feature_tracks: Dict, frame_id: int) -> Dict:
    """
    Create context information for a specific frame.

    Args:
        feature_tracks: All feature track data
        frame_id: Current frame number

    Returns:
        dict: Frame context with feature information
    """
    frame_features = get_frame_features(feature_tracks, frame_id)

    return {
        "frame_id": frame_id,
        "has_features": frame_features is not None,
        "feature_count": frame_features.get("feature_count", 0)
        if frame_features
        else 0,
        "features": frame_features.get("features", []) if frame_features else [],
        "world_features": frame_features.get("world_features", [])
        if frame_features
        else [],
    }


def initialize_feature_data(video_path: str, feature_manager) -> Dict:
    """
    Initialize feature data for a video.

    Args:
        video_path: Path to video file
        feature_manager: Feature storage manager instance

    Returns:
        dict: Initialized feature data structure
    """
    video_basename = extract_video_basename(video_path)
    video_features = load_video_features(feature_manager, video_basename)

    return {
        "video_path": video_path,
        "video_basename": video_basename,
        "feature_tracks": video_features.get("frame_features", {}),
        "summary": calculate_feature_summary(
            video_features.get("frame_features", {}), video_basename
        ),
        "loaded": video_features.get("loaded", False),
        "geo_converted": False,
    }


def add_detection_results_to_data(
    feature_data: Dict, detection_results: Dict, feature_manager
) -> Tuple[Dict, bool]:
    """
    Add new detection results to existing feature data.

    Args:
        feature_data: Current feature data structure
        detection_results: New detection results
        feature_manager: Feature storage manager instance

    Returns:
        tuple: (updated_feature_data, success_status)
    """
    # Save the detection results
    save_success = save_detection_results(feature_manager, detection_results)

    if not save_success:
        return feature_data, False

    # Extract new tracks
    new_tracks = detection_results.get("frame_features", {})

    # Merge with existing tracks
    existing_tracks = feature_data.get("feature_tracks", {})
    merged_tracks = merge_feature_tracks(existing_tracks, new_tracks)

    # Update feature data
    updated_data = {
        **feature_data,
        "feature_tracks": merged_tracks,
        "summary": calculate_feature_summary(
            merged_tracks, feature_data.get("video_basename", "")
        ),
        "loaded": True,
    }

    return updated_data, True


def apply_geo_conversion_to_data(
    feature_data: Dict, camera_map: Dict, local_geo_cs
) -> Dict:
    """
    Apply geo-conversion to all feature data.

    Args:
        feature_data: Feature data structure
        camera_map: Camera poses indexed by frame
        local_geo_cs: Local geographic coordinate system

    Returns:
        dict: Feature data with geo-conversion applied
    """
    feature_tracks = feature_data.get("feature_tracks", {})
    converted_tracks = apply_geo_conversion_to_tracks(
        feature_tracks, camera_map, local_geo_cs
    )

    return {**feature_data, "feature_tracks": converted_tracks, "geo_converted": True}
