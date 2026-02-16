"""
Metrics Manager

Coordinates all individual metric modules.
Automatically discovers and loads all available metrics.
"""

import numpy as np
from typing import List, Dict
from pathlib import Path

from metrics import (
    SharpnessMetric,
    BrightnessMetric,
    ContrastMetric,
    ColorVibrancyMetric,
    MotionMetric,
    CompositionMetric,
    PersonDetectionMetric
)


class MetricsManager:
    """
    Manages all metric calculations.
    
    Automatically loads all available metrics and provides
    a unified interface for calculating them.
    """
    
    def __init__(self):
        """Initialize all metric calculators"""
        # Initialize all metrics
        self.metrics = {
            'sharpness': SharpnessMetric(),
            'brightness': BrightnessMetric(),
            'contrast': ContrastMetric(),
            'color_vibrancy': ColorVibrancyMetric(),
            'motion': MotionMetric(),
            'composition': CompositionMetric(),
            'person_detection': PersonDetectionMetric(),
        }
    
    def get_available_metrics(self) -> List[str]:
        """
        Get list of all available metric names.
        
        Returns:
            List of metric names
        """
        return list(self.metrics.keys())
    
    def get_metric_info(self) -> Dict[str, str]:
        """
        Get information about all metrics.
        
        Returns:
            Dictionary mapping metric names to descriptions
        """
        return {
            name: metric.get_description()
            for name, metric in self.metrics.items()
        }
    
    def calculate_sharpness(self, frame: np.ndarray) -> float:
        """Calculate sharpness metric"""
        return self.metrics['sharpness'].calculate(frame)
    
    def calculate_brightness(self, frame: np.ndarray) -> float:
        """Calculate brightness metric"""
        return self.metrics['brightness'].calculate(frame)
    
    def calculate_contrast(self, frame: np.ndarray) -> float:
        """Calculate contrast metric"""
        return self.metrics['contrast'].calculate(frame)
    
    def calculate_color_vibrancy(self, frame: np.ndarray) -> float:
        """Calculate color vibrancy metric"""
        return self.metrics['color_vibrancy'].calculate(frame)
    
    def calculate_motion(self, frame: np.ndarray, prev_frame: np.ndarray) -> float:
        """Calculate motion metric (requires previous frame)"""
        return self.metrics['motion'].calculate(frame, prev_frame=prev_frame)
    
    def calculate_composition(self, frame: np.ndarray) -> float:
        """Calculate composition metric"""
        return self.metrics['composition'].calculate(frame)
    
    def calculate_person_detection(self, frame: np.ndarray) -> tuple:
        """
        Calculate person detection metrics.
        
        Returns:
            Tuple of (person_score, center_focus_score)
        """
        return self.metrics['person_detection'].calculate(frame)
    
    def calculate_all_for_frame(self, frame: np.ndarray, 
                               prev_frame: np.ndarray = None) -> Dict[str, float]:
        """
        Calculate all metrics for a single frame.
        
        Args:
            frame: Current frame
            prev_frame: Previous frame (optional, needed for motion)
            
        Returns:
            Dictionary of metric_name -> score
        """
        results = {}
        
        # Calculate single-frame metrics
        results['sharpness'] = self.calculate_sharpness(frame)
        results['brightness'] = self.calculate_brightness(frame)
        results['contrast'] = self.calculate_contrast(frame)
        results['color_vibrancy'] = self.calculate_color_vibrancy(frame)
        results['composition'] = self.calculate_composition(frame)
        
        # Calculate motion (requires previous frame)
        if prev_frame is not None:
            results['motion'] = self.calculate_motion(frame, prev_frame)
        else:
            results['motion'] = 0.0
        
        # Calculate person detection (returns two scores)
        person_score, center_focus = self.calculate_person_detection(frame)
        results['person_score'] = person_score
        results['center_focus_score'] = center_focus
        
        return results
    
    def print_available_metrics(self):
        """Print information about all available metrics"""
        print("\n" + "="*60)
        print("Available Metrics")
        print("="*60)
        
        for name, metric in self.metrics.items():
            print(f"\n{name}:")
            print(f"  {metric.get_description()}")
        
        print("\n" + "="*60)


# Example of how to add a new metric:
# 
# 1. Create new file: metrics/my_new_metric.py
# 2. Import in metrics/__init__.py
# 3. Add to MetricsManager.__init__():
#    self.metrics['my_metric'] = MyNewMetric()
# 4. Add convenience method (optional):
#    def calculate_my_metric(self, frame):
#        return self.metrics['my_metric'].calculate(frame)
# 5. Update calculate_all_for_frame() to include it
