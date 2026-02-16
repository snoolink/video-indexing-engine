"""
Sharpness Metric

Measures image sharpness using Laplacian variance.
Higher values indicate sharper, more focused images.
"""

import cv2
import numpy as np
from .base_metric import BaseMetric


class SharpnessMetric(BaseMetric):
    """
    Calculate image sharpness using Laplacian variance.
    
    Uses the variance of the Laplacian operator to measure
    the amount of edges/details in the image.
    
    Range: 0.0 (blurry) to 1.0 (sharp)
    """
    
    def __init__(self):
        super().__init__()
        self.typical_max = 1000.0  # Typical maximum Laplacian variance
    
    def calculate(self, frame: np.ndarray, **kwargs) -> float:
        """
        Calculate sharpness score for a frame.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Sharpness score (0.0 to 1.0)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        # Normalize to 0-1 range
        # Typical values range from 0-2000, we use 1000 as max
        score = min(variance / self.typical_max, 1.0)
        
        return score
    
    def get_description(self) -> str:
        return "Measures image sharpness and focus quality using Laplacian variance"
