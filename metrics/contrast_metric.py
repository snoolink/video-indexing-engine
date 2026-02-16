"""
Contrast Metric

Measures image contrast using standard deviation.
Higher contrast creates more visual interest.
"""

import cv2
import numpy as np
from .base_metric import BaseMetric


class ContrastMetric(BaseMetric):
    """
    Calculate image contrast using standard deviation.
    
    Higher standard deviation indicates more contrast
    and visual definition in the image.
    
    Range: 0.0 (flat/low contrast) to 1.0 (high contrast)
    """
    
    def __init__(self):
        super().__init__()
        self.typical_max = 60.0  # Typical maximum std dev for good contrast
    
    def calculate(self, frame: np.ndarray, **kwargs) -> float:
        """
        Calculate contrast score for a frame.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Contrast score (0.0 to 1.0)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate standard deviation (measure of contrast)
        std_dev = np.std(gray)
        
        # Normalize to 0-1 range
        # Typical values range from 0-80, we use 60 as good contrast
        score = min(std_dev / self.typical_max, 1.0)
        
        return score
    
    def get_description(self) -> str:
        return "Measures image contrast and visual definition using standard deviation"
