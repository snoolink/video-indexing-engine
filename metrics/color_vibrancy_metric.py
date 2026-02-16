"""
Color Vibrancy Metric

Measures color saturation in HSV space.
Fashion/lifestyle content benefits from vibrant colors.
"""

import cv2
import numpy as np
from .base_metric import BaseMetric

class ColorVibrancyMetric(BaseMetric):
    """
    Calculate color saturation in HSV color space.
    
    Analyzes the S (saturation) channel to determine
    how vibrant and colorful the image is.
    
    Range: 0.0 (grayscale/dull) to 1.0 (vibrant colors)
    """
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, frame: np.ndarray, **kwargs) -> float:
        """
        Calculate color vibrancy score for a frame.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Color vibrancy score (0.0 to 1.0)
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Extract S (saturation) channel
        saturation = hsv[:, :, 1]
        
        # Calculate average saturation (0-255 → 0-1)
        avg_saturation = np.mean(saturation) / 255.0
        
        return avg_saturation
    
    def get_description(self) -> str:
        return "Measures color saturation and vibrancy in HSV color space"


