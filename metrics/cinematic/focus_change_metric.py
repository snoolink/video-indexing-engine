"""
Focus Change Detection Metric

Detects focus changes (rack focus) and shallow depth of field.
"""

import cv2
import numpy as np
from typing import Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from metrics.base_metric import BaseMetric


class FocusChangeMetric(BaseMetric):
    """
    Detect focus changes (rack focus) between frames.
    
    Also detects shallow depth of field (bokeh effect).
    
    Range: 0.0 (no change) to 1.0 (significant change)
    """
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, frame: np.ndarray, prev_frame: np.ndarray = None, **kwargs) -> Dict:
        """
        Calculate focus change metrics.
        
        Args:
            frame: Current video frame (BGR format)
            prev_frame: Previous video frame (optional, for change detection)
            
        Returns:
            Dictionary with focus change metrics
        """
        # Convert to grayscale
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate current sharpness
        laplacian2 = cv2.Laplacian(gray2, cv2.CV_64F)
        current_sharpness = np.var(laplacian2)
        
        # Detect shallow depth of field (bokeh)
        has_bokeh = self._detect_bokeh(gray2)
        
        # If no previous frame, return current state only
        if prev_frame is None:
            return {
                'has_focus_change': False,
                'focus_change_amount': 0.0,
                'current_sharpness': current_sharpness,
                'has_shallow_dof': has_bokeh,
                'dof_variance': 0.0
            }
        
        # Calculate focus change from previous frame
        gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        laplacian1 = cv2.Laplacian(gray1, cv2.CV_64F)
        prev_sharpness = np.var(laplacian1)
        
        # Calculate focus change
        focus_change = abs(current_sharpness - prev_sharpness)
        focus_change_percentage = (focus_change / (prev_sharpness + 1e-6)) * 100
        
        # Threshold for significant focus change (rack focus)
        has_focus_change = focus_change_percentage > 15
        
        return {
            'has_focus_change': has_focus_change,
            'focus_change_amount': focus_change_percentage,
            'current_sharpness': current_sharpness,
            'has_shallow_dof': has_bokeh,
            'dof_variance': self._calculate_dof_variance(gray2)
        }
    
    def _detect_bokeh(self, gray: np.ndarray) -> bool:
        """
        Detect shallow depth of field (bokeh effect).
        
        High variance in sharpness across regions indicates bokeh.
        """
        h, w = gray.shape
        
        # Divide into 9 regions (3x3 grid)
        regions = []
        for i in range(3):
            for j in range(3):
                region = gray[i*h//3:(i+1)*h//3, j*w//3:(j+1)*w//3]
                laplacian = cv2.Laplacian(region, cv2.CV_64F)
                sharpness = np.var(laplacian)
                regions.append(sharpness)
        
        # High variance in sharpness = shallow DOF
        sharpness_variance = np.var(regions)
        
        # Threshold for bokeh detection
        return sharpness_variance > 1000
    
    def _calculate_dof_variance(self, gray: np.ndarray) -> float:
        """Calculate depth of field variance metric"""
        h, w = gray.shape
        
        regions = [
            gray[0:h//3, 0:w//3],           # Top-left
            gray[h//3:2*h//3, w//3:2*w//3], # Center
            gray[2*h//3:h, 2*w//3:w]        # Bottom-right
        ]
        
        region_sharpness = [
            np.var(cv2.Laplacian(region, cv2.CV_64F)) 
            for region in regions
        ]
        
        return float(np.var(region_sharpness))
    
    def get_description(self) -> str:
        return "Detects focus changes (rack focus) and shallow depth of field"
