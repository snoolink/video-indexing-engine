"""
Brightness Metric

Measures lighting quality in LAB color space.
Optimal range is 40-80% brightness.
"""

import cv2
import numpy as np
from .base_metric import BaseMetric


class BrightnessMetric(BaseMetric):
    """
    Calculate average brightness in LAB color space.
    
    Analyzes the L (lightness) channel to determine
    if the frame is properly exposed.
    
    Range: 0.0 (poorly lit) to 1.0 (optimal lighting)
    """
    
    def __init__(self):
        super().__init__()
        self.optimal_min = 0.3  # Below this is too dark
        self.optimal_max = 0.8  # Above this is too bright
    
    def calculate(self, frame: np.ndarray, **kwargs) -> float:
        """
        Calculate brightness score for a frame.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Brightness score (0.0 to 1.0)
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        # Extract L (lightness) channel
        l_channel = lab[:, :, 0]
        
        # Calculate average brightness (0-255 → 0-1)
        avg_brightness = np.mean(l_channel) / 255.0
        
        # Score based on optimal range
        if avg_brightness < self.optimal_min:
            # Too dark - penalize
            score = avg_brightness / self.optimal_min
        elif avg_brightness > self.optimal_max:
            # Too bright - penalize
            score = (1.0 - avg_brightness) / (1.0 - self.optimal_max)
        else:
            # Optimal range
            score = 1.0
        
        return max(0.0, min(1.0, score))
    
    def get_description(self) -> str:
        return "Measures lighting quality, optimal in the 30-80% brightness range"
