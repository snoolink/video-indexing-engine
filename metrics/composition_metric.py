"""
Composition Metric

Measures composition quality using edge distribution.
Good composition has edges distributed across the frame.
"""

import cv2
import numpy as np
from .base_metric import BaseMetric


class CompositionMetric(BaseMetric):
    """
    Calculate composition quality using edge detection.
    
    Divides frame into 9 sections (rule of thirds) and
    measures edge distribution across sections.
    
    Range: 0.0 (poor composition) to 1.0 (good composition)
    """
    
    def __init__(self):
        super().__init__()
        self.canny_low = 50
        self.canny_high = 150
    
    def calculate(self, frame: np.ndarray, **kwargs) -> float:
        """
        Calculate composition score for a frame.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Composition score (0.0 to 1.0)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, self.canny_low, self.canny_high)
        
        # Divide frame into 9 sections (rule of thirds)
        h, w = edges.shape
        sections = []
        
        for i in range(3):
            for j in range(3):
                # Extract section
                section = edges[
                    i * h // 3 : (i + 1) * h // 3,
                    j * w // 3 : (j + 1) * w // 3
                ]
                # Count edges in section
                sections.append(np.sum(section))
        
        # Calculate distribution
        # Good composition has relatively even edge distribution
        if np.mean(sections) == 0:
            return 0.0
        
        edge_distribution = np.std(sections) / (np.mean(sections) + 1)
        
        # Lower std relative to mean = better distribution
        # Normalize and invert (lower is better)
        score = 1.0 - min(edge_distribution / 2.0, 1.0)
        
        return max(0.0, score)
    
    def get_description(self) -> str:
        return "Measures composition quality using edge distribution across rule of thirds grid"
