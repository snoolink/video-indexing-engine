#!/usr/bin/env python3
"""
Data Models Module

Defines all data structures used throughout the video indexing system.
Easy to extend with new metrics or fields.
"""

from dataclasses import dataclass, asdict
from typing import Dict
import numpy as np

@dataclass
class ScoreMetrics:
    """
    All available scoring metrics for a video segment.
    
    Each metric is scored from 0.0 (worst) to 1.0 (best).
    Add new metrics by simply adding new fields here.
    """
    sharpness: float = 0.0
    brightness: float = 0.0
    contrast: float = 0.0
    color_vibrancy: float = 0.0
    motion_score: float = 0.0
    composition_score: float = 0.0
    person_score: float = 0.0
    center_focus_score: float = 0.0
    
    # Example: Add new metrics here
    # face_score: float = 0.0
    # smile_score: float = 0.0
    # symmetry_score: float = 0.0
    
    # def to_dict(self) -> Dict:
    #     """Convert to dictionary for JSON serialization"""
    #     return asdict(self)
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
    # Convert all values to native Python types (handle numpy types)
        return {
        key: float(value) if isinstance(value, (np.floating, np.integer)) else value
        for key, value in asdict(self).items()
    }

    @classmethod
    def from_dict(cls, data: Dict):
        """Create ScoreMetrics from dictionary"""
        return cls(**data)
    
    def get_metric_names(self) -> list:
        """Get list of all available metric names"""
        return list(self.__dict__.keys())


@dataclass
class VideoSegment:
    """
    Stores information about a video segment (e.g., 1-second clip).
    
    Contains timing information and all calculated metrics.
    """
    video_file: str           # Name of the source video file
    start_time: float         # Start time in seconds
    end_time: float          # End time in seconds
    duration: float          # Duration in seconds
    metrics: ScoreMetrics    # All calculated metrics
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'video_file': self.video_file,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'metrics': self.metrics.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create VideoSegment from dictionary"""
        return cls(
            video_file=data['video_file'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            duration=data['duration'],
            metrics=ScoreMetrics.from_dict(data['metrics'])
        )
    
    def overlaps_with(self, other: 'VideoSegment') -> bool:
        """
        Check if this segment overlaps with another segment.
        
        Args:
            other: Another VideoSegment to check against
            
        Returns:
            True if segments overlap, False otherwise
        """
        # Must be from the same video
        if self.video_file != other.video_file:
            return False
        
        # Segments overlap if one starts before the other ends
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)


@dataclass
class VideoMetadata:
    """Metadata about an indexed video file"""
    segment_count: int       # Number of segments extracted
    file_path: str          # Full path to video file
    indexed: bool           # Whether indexing was successful
    error: str = None       # Error message if indexing failed
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {
            'segment_count': self.segment_count,
            'file_path': self.file_path,
            'indexed': self.indexed
        }
        if self.error:
            result['error'] = self.error
        return result


@dataclass  
class IndexMetadata:
    """Metadata about the entire video index"""
    created_at: str                # ISO format timestamp
    segment_duration: float        # Duration of each segment
    total_segments: int           # Total segments across all videos
    total_videos: int             # Total number of videos
    indexed_videos: int           # Successfully indexed videos
    available_metrics: list       # List of metric names
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'created_at': self.created_at,
            'segment_duration': self.segment_duration,
            'total_segments': self.total_segments,
            'total_videos': self.total_videos,
            'indexed_videos': self.indexed_videos,
            'available_metrics': self.available_metrics
        }
