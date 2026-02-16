#!/usr/bin/env python3
"""
Video Reader Module

Handles all video file operations including reading, seeking, and extracting frames.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional


class VideoReader:
    """
    Handles reading video files and extracting frames.
    
    Provides methods for getting video metadata and reading specific segments.
    """
    
    def __init__(self, video_path: Path):
        """
        Initialize video reader for a specific video file.
        
        Args:
            video_path: Path to video file
        """
        self.video_path = video_path
        self._validate_video()
    
    def _validate_video(self):
        """Validate that video file exists and can be opened"""
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
        
        # Try to open video
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            cap.release()
            raise ValueError(f"Cannot open video file: {self.video_path}")
        cap.release()
    
    def get_metadata(self) -> dict:
        """
        Get video metadata (fps, duration, resolution, etc.).
        
        Returns:
            Dictionary with video metadata
        """
        cap = cv2.VideoCapture(str(self.video_path))
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'fps': fps,
            'total_frames': total_frames,
            'width': width,
            'height': height,
            'duration': duration,
            'filename': self.video_path.name,
            'path': str(self.video_path)
        }
    
    def read_segment(self, start_frame: int, num_frames: int) -> List[np.ndarray]:
        """
        Read a segment of frames from the video.
        
        Args:
            start_frame: Frame number to start from (0-indexed)
            num_frames: Number of frames to read
            
        Returns:
            List of frames (BGR format)
        """
        cap = cv2.VideoCapture(str(self.video_path))
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        frames = []
        for _ in range(num_frames):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        return frames
    
    def read_segment_by_time(self, start_time: float, duration: float) -> List[np.ndarray]:
        """
        Read a segment of frames by time (in seconds).
        
        Args:
            start_time: Start time in seconds
            duration: Duration in seconds
            
        Returns:
            List of frames (BGR format)
        """
        metadata = self.get_metadata()
        fps = metadata['fps']
        
        start_frame = int(start_time * fps)
        num_frames = int(duration * fps)
        
        return self.read_segment(start_frame, num_frames)
    
    def get_frame_at_time(self, time_seconds: float) -> Optional[np.ndarray]:
        """
        Get a single frame at a specific time.
        
        Args:
            time_seconds: Time in seconds
            
        Returns:
            Frame (BGR format) or None if failed
        """
        cap = cv2.VideoCapture(str(self.video_path))
        
        # Seek to time
        cap.set(cv2.CAP_PROP_POS_MSEC, time_seconds * 1000)
        
        ret, frame = cap.read()
        cap.release()
        
        return frame if ret else None
    
    def iterate_segments(self, segment_duration: float) -> Tuple[int, List[np.ndarray]]:
        """
        Generator that yields segments of the video.
        
        Args:
            segment_duration: Duration of each segment in seconds
            
        Yields:
            Tuple of (start_frame, frames_list)
        """
        metadata = self.get_metadata()
        fps = metadata['fps']
        total_frames = metadata['total_frames']
        frames_per_segment = int(fps * segment_duration)
        
        for start_frame in range(0, total_frames - frames_per_segment, frames_per_segment):
            frames = self.read_segment(start_frame, frames_per_segment)
            
            # Only yield if we got enough frames
            if len(frames) >= frames_per_segment // 2:
                yield start_frame, frames
    
    @staticmethod
    def get_supported_formats() -> set:
        """
        Get set of supported video file extensions.
        
        Returns:
            Set of file extensions (e.g., {'.mp4', '.mov', ...})
        """
        return {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.flv', '.wmv'}
    
    @staticmethod
    def find_videos(folder: Path) -> List[Path]:
        """
        Find all supported video files in a folder.
        
        Args:
            folder: Path to folder to search
            
        Returns:
            List of video file paths
        """
        supported = VideoReader.get_supported_formats()
        return [
            f for f in folder.iterdir()
            if f.suffix.lower() in supported
        ]


# Example usage:
# 
# reader = VideoReader(Path("video.mp4"))
# metadata = reader.get_metadata()
# print(f"Video: {metadata['duration']:.1f}s at {metadata['fps']:.1f} fps")
# 
# # Read first 30 frames
# frames = reader.read_segment(0, 30)
# 
# # Iterate through all 1-second segments
# for start_frame, frames in reader.iterate_segments(1.0):
#     print(f"Processing segment starting at frame {start_frame}")
#     # ... process frames ...
