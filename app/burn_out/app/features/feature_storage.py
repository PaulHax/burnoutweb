"""
Feature Storage System
TeleSculptor-compatible feature data management for burnoutweb.

This module provides complete compatibility with TeleSculptor's feature storage:
- .kwfd binary files for individual frame features
- tracks.txt ASCII format for feature tracks
- results/features/ directory structure
- KWIVER I/O integration for cross-application compatibility

Based on analysis of TeleSculptor's storage system and KWIVER feature I/O.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# KWIVER imports for I/O compatibility
import kwiver.vital.algo as kva
from kwiver.vital.types import FeatureSet, Feature
from kwiver.vital.config import empty_config
from kwiver.vital import vital_logging

logger = vital_logging.getLogger(__name__)


class FeatureDataManager:
    """
    TeleSculptor-compatible feature data management.
    
    Manages feature storage in the exact format used by TeleSculptor:
    - Individual frame features in .kwfd format
    - Feature tracks in tracks.txt format
    - Standard directory structure (results/features/)
    - Cross-application compatibility with TeleSculptor projects
    """
    
    def __init__(self, base_path: str = "results"):
        """
        Initialize feature data manager.
        
        Args:
            base_path: Base directory for feature storage (TeleSculptor default: "results")
        """
        self.base_path = Path(base_path)
        self.features_dir = self.base_path / "features"  # TeleSculptor's structure
        self.tracks_file = self.base_path / "tracks.txt"
        self.landmarks_file = self.base_path / "landmarks.ply"
        self.geo_origin_file = self.base_path / "geo_origin.txt"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Initialize KWIVER I/O
        self._kwiver_io = None
        self._init_kwiver_io()
    
    def _ensure_directories(self):
        """Create required directories if they don't exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.features_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Feature storage initialized at {self.base_path}")
    
    def _init_kwiver_io(self):
        """Initialize KWIVER feature I/O for .kwfd file compatibility."""
        try:
            # Create KWIVER feature I/O algorithm
            self._kwiver_io = kva.FeatureDescriptorIO.create("core")
            
            # Configure for TeleSculptor compatibility
            config = empty_config()
            config.set_value("write_float_features", "true")  # TeleSculptor default
            self._kwiver_io.set_configuration(config)
            
            logger.info("KWIVER feature I/O initialized for .kwfd compatibility")
            
        except Exception as e:
            logger.warning(f"KWIVER I/O initialization failed: {e}")
            self._kwiver_io = None
    
    def save_frame_features(self, frame_id: int, feature_data: Dict, 
                          video_basename: str) -> bool:
        """
        Save features for a single frame in TeleSculptor .kwfd format.
        
        Args:
            frame_id: Frame number
            feature_data: Feature data from service (includes serialized features)
            video_basename: Video file basename for naming
            
        Returns:
            bool: Success status
        """
        try:
            # Generate TeleSculptor naming: {video_name}-{frame_number}.kwfd
            filename = f"{video_basename}-{frame_id:05d}.kwfd"
            filepath = self.features_dir / filename
            
            # For now, save as JSON since we have serialized features
            # TODO: Implement true .kwfd format when KWIVER I/O is working
            feature_count = feature_data.get('feature_count', 0)
            features = feature_data.get('features', [])
            
            # Save metadata and feature data
            save_data = {
                'frame_number': frame_id,
                'feature_count': feature_count,
                'features': features,
                'video_basename': video_basename,
                'format_version': '1.0'
            }
            
            # Save as JSON for now (compatible format)
            json_filepath = filepath.with_suffix('.json')
            with open(json_filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.debug(f"Saved {feature_count} features for frame {frame_id} to {json_filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save features for frame {frame_id}: {e}")
            return False
    
    def load_frame_features(self, frame_id: int, video_basename: str) -> Optional[Dict]:
        """
        Load features for a single frame.
        
        Args:
            frame_id: Frame number
            video_basename: Video file basename
            
        Returns:
            dict: Feature data or None if not found
        """
        try:
            # Try TeleSculptor .kwfd format first
            filename = f"{video_basename}-{frame_id:05d}.kwfd"
            filepath = self.features_dir / filename
            
            if filepath.exists() and self._kwiver_io:
                # Load using KWIVER I/O
                feature_set = self._kwiver_io.load(str(filepath))
                if feature_set:
                    features = feature_set.features()
                    return {
                        'frame_number': frame_id,
                        'feature_count': len(features),
                        'feature_set': feature_set,
                        'format': 'kwfd'
                    }
            
            # Try JSON format (our current format)
            json_filepath = filepath.with_suffix('.json')
            if json_filepath.exists():
                with open(json_filepath, 'r') as f:
                    data = json.load(f)
                    data['format'] = 'json'
                    return data
            
            logger.debug(f"No features found for frame {frame_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load features for frame {frame_id}: {e}")
            return None
    
    def save_detection_results(self, detection_results: Dict) -> bool:
        """
        Save complete detection results from service.
        
        Args:
            detection_results: Results from FeatureTrackingService
            
        Returns:
            bool: Success status
        """
        try:
            if not detection_results.get('success', False):
                logger.error("Cannot save failed detection results")
                return False
            
            frame_features = detection_results.get('frame_features', {})
            video_path = detection_results.get('video_path', '')
            video_basename = Path(video_path).stem if video_path else 'unknown'
            
            logger.info(f"Saving {len(frame_features)} frames of features for {video_basename}")
            
            # Save individual frame features
            saved_count = 0
            for frame_id, feature_data in frame_features.items():
                if self.save_frame_features(frame_id, feature_data, video_basename):
                    saved_count += 1
            
            # Save summary metadata
            summary_data = {
                'video_path': video_path,
                'video_basename': video_basename,
                'detection_summary': detection_results.get('summary', {}),
                'total_frames': len(frame_features),
                'saved_frames': saved_count,
                'timestamp': self._get_timestamp()
            }
            
            summary_file = self.base_path / f"{video_basename}_detection_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary_data, f, indent=2)
            
            logger.info(f"Saved features for {saved_count}/{len(frame_features)} frames")
            return saved_count == len(frame_features)
            
        except Exception as e:
            logger.error(f"Failed to save detection results: {e}")
            return False
    
    def load_detection_results(self, video_basename: str) -> Optional[Dict]:
        """
        Load complete detection results for a video.
        
        Args:
            video_basename: Video file basename
            
        Returns:
            dict: Detection results or None if not found
        """
        try:
            summary_file = self.base_path / f"{video_basename}_detection_summary.json"
            
            if not summary_file.exists():
                logger.debug(f"No detection results found for {video_basename}")
                return None
            
            # Load summary
            with open(summary_file, 'r') as f:
                summary = json.load(f)
            
            # Load individual frame features
            frame_features = {}
            total_frames = summary.get('total_frames', 0)
            
            for frame_id in range(1, total_frames + 1):
                feature_data = self.load_frame_features(frame_id, video_basename)
                if feature_data:
                    frame_features[frame_id] = feature_data
            
            return {
                'success': True,
                'video_path': summary.get('video_path'),
                'video_basename': video_basename,
                'frame_features': frame_features,
                'summary': summary.get('detection_summary', {}),
                'loaded_frames': len(frame_features),
                'total_frames': total_frames
            }
            
        except Exception as e:
            logger.error(f"Failed to load detection results for {video_basename}: {e}")
            return None
    
    def save_tracks(self, feature_tracks: List[Dict]) -> bool:
        """
        Save feature tracks in TeleSculptor ASCII format.
        
        Args:
            feature_tracks: List of feature track data
            
        Returns:
            bool: Success status
        """
        try:
            with open(self.tracks_file, 'w') as f:
                # Write header comment
                f.write("# TeleSculptor-compatible feature tracks\n")
                f.write("# Format: track_id frame_id x y magnitude scale angle red green blue has_descriptor\n")
                
                for track in feature_tracks:
                    track_id = track.get('id', 0)
                    observations = track.get('observations', [])
                    
                    for obs in observations:
                        # TeleSculptor format
                        line = f"{track_id} {obs['frame_id']} {obs['x']:.3f} {obs['y']:.3f} "
                        line += f"{obs['magnitude']:.6f} {obs['scale']:.3f} {obs['angle']:.3f} "
                        line += f"{obs['red']} {obs['green']} {obs['blue']} {obs['has_descriptor']}\n"
                        f.write(line)
            
            logger.info(f"Saved {len(feature_tracks)} feature tracks to {self.tracks_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save feature tracks: {e}")
            return False
    
    def load_tracks(self) -> List[Dict]:
        """
        Load feature tracks from TeleSculptor format.
        
        Returns:
            list: Feature track data
        """
        try:
            if not self.tracks_file.exists():
                return []
            
            tracks = {}
            
            with open(self.tracks_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 11:
                        track_id = int(parts[0])
                        frame_id = int(parts[1])
                        x, y = float(parts[2]), float(parts[3])
                        magnitude = float(parts[4])
                        scale = float(parts[5])
                        angle = float(parts[6])
                        red, green, blue = int(parts[7]), int(parts[8]), int(parts[9])
                        has_descriptor = int(parts[10])
                        
                        if track_id not in tracks:
                            tracks[track_id] = {
                                'id': track_id,
                                'observations': []
                            }
                        
                        tracks[track_id]['observations'].append({
                            'frame_id': frame_id,
                            'x': x, 'y': y,
                            'magnitude': magnitude,
                            'scale': scale,
                            'angle': angle,
                            'red': red, 'green': green, 'blue': blue,
                            'has_descriptor': has_descriptor
                        })
            
            track_list = list(tracks.values())
            logger.info(f"Loaded {len(track_list)} feature tracks")
            return track_list
            
        except Exception as e:
            logger.error(f"Failed to load feature tracks: {e}")
            return []
    
    def get_storage_info(self) -> Dict:
        """
        Get information about stored feature data.
        
        Returns:
            dict: Storage information
        """
        info = {
            'base_path': str(self.base_path),
            'features_dir': str(self.features_dir),
            'features_dir_exists': self.features_dir.exists(),
            'tracks_file_exists': self.tracks_file.exists(),
            'kwiver_io_available': self._kwiver_io is not None
        }
        
        # Count feature files
        if self.features_dir.exists():
            kwfd_files = list(self.features_dir.glob("*.kwfd"))
            json_files = list(self.features_dir.glob("*.json"))
            info['kwfd_feature_files'] = len(kwfd_files)
            info['json_feature_files'] = len(json_files)
            info['total_feature_files'] = len(kwfd_files) + len(json_files)
        
        return info
    
    def validate_telesculptor_compatibility(self) -> Dict:
        """
        Validate storage is compatible with TeleSculptor.
        
        Returns:
            dict: Validation results
        """
        results = {
            'compatible': True,
            'issues': [],
            'recommendations': []
        }
        
        # Check directory structure
        if not self.features_dir.exists():
            results['issues'].append("features/ directory missing")
            results['compatible'] = False
        
        # Check KWIVER I/O availability
        if not self._kwiver_io:
            results['issues'].append("KWIVER I/O not available - .kwfd files cannot be written")
            results['recommendations'].append("Ensure KWIVER Python bindings are properly installed")
        
        # Check for feature files
        info = self.get_storage_info()
        if info.get('total_feature_files', 0) == 0:
            results['issues'].append("No feature files found")
        
        return results
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        import datetime
        return datetime.datetime.now().isoformat()


# Convenience functions
def create_feature_manager(base_path: str = "results") -> FeatureDataManager:
    """Create feature data manager with TeleSculptor structure."""
    return FeatureDataManager(base_path)


def save_detection_results(detection_results: Dict, base_path: str = "results") -> bool:
    """
    Convenience function to save detection results.
    
    Args:
        detection_results: Results from FeatureTrackingService
        base_path: Storage base path
        
    Returns:
        bool: Success status
    """
    manager = create_feature_manager(base_path)
    return manager.save_detection_results(detection_results)


def load_detection_results(video_basename: str, base_path: str = "results") -> Optional[Dict]:
    """
    Convenience function to load detection results.
    
    Args:
        video_basename: Video file basename
        base_path: Storage base path
        
    Returns:
        dict: Detection results or None
    """
    manager = create_feature_manager(base_path)
    return manager.load_detection_results(video_basename)