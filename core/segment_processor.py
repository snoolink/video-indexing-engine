"""
Segment Processor Module

Processes video segments and aggregates metrics from individual frames.
Uses the MetricsManager to calculate all metrics.
"""

import numpy as np
from typing import List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_models import ScoreMetrics
from core.metrics_manager import MetricsManager


class SegmentProcessor:
    """
    Processes video segments and calculates aggregate metrics.
    
    Takes a list of frames and returns a ScoreMetrics object with
    all metrics calculated and averaged over the segment.
    """
    
    def __init__(self):
        """Initialize the segment processor with metrics manager"""
        self.metrics_manager = MetricsManager()
    
    def process_segment(self, frames: List[np.ndarray]) -> ScoreMetrics:
        """
        Calculate all metrics for a list of frames representing a segment.
        
        Samples frames at different intervals for different metrics to
        optimize performance while maintaining accuracy.
        
        Args:
            frames: List of video frames (BGR format) representing a segment
            
        Returns:
            ScoreMetrics object with all calculated and averaged metrics
        """
        metrics = ScoreMetrics()
        
        # Storage for individual frame scores
        sharpness_scores = []
        brightness_scores = []
        contrast_scores = []
        color_scores = []
        motion_scores = []
        composition_scores = []
        person_scores = []
        center_focus_scores = []
        
        prev_frame = None
        
        for i, frame in enumerate(frames):
            # Sample every 3rd frame for basic metrics (performance optimization)
            if i % 3 == 0:
                sharpness_scores.append(
                    self.metrics_manager.calculate_sharpness(frame)
                )
                brightness_scores.append(
                    self.metrics_manager.calculate_brightness(frame)
                )
                contrast_scores.append(
                    self.metrics_manager.calculate_contrast(frame)
                )
                color_scores.append(
                    self.metrics_manager.calculate_color_vibrancy(frame)
                )
                composition_scores.append(
                    self.metrics_manager.calculate_composition(frame)
                )
                
                # Person detection every 6th frame (more expensive operation)
                if i % 6 == 0:
                    person_score, center_score = \
                        self.metrics_manager.calculate_person_detection(frame)
                    person_scores.append(person_score)
                    center_focus_scores.append(center_score)
                
                # Motion requires previous frame
                if prev_frame is not None:
                    motion_scores.append(
                        self.metrics_manager.calculate_motion(frame, prev_frame)
                    )
                
                prev_frame = frame.copy()
        
        # Aggregate scores by averaging
        metrics.sharpness = np.mean(sharpness_scores) if sharpness_scores else 0.0
        metrics.brightness = np.mean(brightness_scores) if brightness_scores else 0.0
        metrics.contrast = np.mean(contrast_scores) if contrast_scores else 0.0
        metrics.color_vibrancy = np.mean(color_scores) if color_scores else 0.0
        metrics.motion_score = np.mean(motion_scores) if motion_scores else 0.0
        metrics.composition_score = np.mean(composition_scores) if composition_scores else 0.0
        metrics.person_score = np.mean(person_scores) if person_scores else 0.5
        metrics.center_focus_score = np.mean(center_focus_scores) if center_focus_scores else 0.5
        
        return metrics
    
    def get_sampling_info(self) -> dict:
        """
        Get information about frame sampling strategy.
        
        Returns:
            Dictionary with sampling details for each metric type
        """
        return {
            'basic_metrics': {
                'metrics': ['sharpness', 'brightness', 'contrast', 
                           'color_vibrancy', 'composition'],
                'sampling': 'every 3rd frame',
                'reason': 'balance between accuracy and performance'
            },
            'person_detection': {
                'metrics': ['person_score', 'center_focus_score'],
                'sampling': 'every 6th frame',
                'reason': 'expensive operation, less temporal variation'
            },
            'motion_detection': {
                'metrics': ['motion_score'],
                'sampling': 'every 3rd frame',
                'reason': 'requires consecutive frames, moderate cost'
            }
        }
    
    def get_available_metrics(self) -> List[str]:
        """Get list of all available metrics"""
        return self.metrics_manager.get_available_metrics()
