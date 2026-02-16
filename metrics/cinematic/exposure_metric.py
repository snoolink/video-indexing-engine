"""
Exposure Quality Analysis Metric

Analyzes exposure quality and dynamic range.
Detects over/under/well exposed footage.
"""

import cv2
import numpy as np
from typing import Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from metrics.base_metric import BaseMetric


class ExposureMetric(BaseMetric):
    """
    Analyze exposure quality and dynamic range.
    
    Classifications:
    - properly_exposed (optimal)
    - underexposed (too dark)
    - overexposed (too bright)
    
    Range: 0.0 (poor exposure) to 1.0 (perfect exposure)
    """
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, frame: np.ndarray, **kwargs) -> Dict:
        """
        Calculate exposure quality.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Dictionary with exposure metrics
        """
        # Convert to LAB
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        
        # Calculate histogram
        hist = cv2.calcHist([l_channel], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()
        
        # Exposure metrics
        l_mean = np.mean(l_channel)
        l_std = np.std(l_channel)
        l_min = np.min(l_channel)
        l_max = np.max(l_channel)
        
        # Check for clipped highlights (>250)
        clipped_highlights_pct = np.sum(l_channel > 250) / l_channel.size * 100
        
        # Check for crushed blacks (<5)
        crushed_blacks_pct = np.sum(l_channel < 5) / l_channel.size * 100
        
        # Dynamic range utilization
        dynamic_range = l_max - l_min
        dynamic_range_score = min(dynamic_range / 255 * 100, 100)
        
        # Histogram distribution quality
        quarters = [np.sum(hist[i*64:(i+1)*64]) for i in range(4)]
        mean_quarter = np.mean(quarters)
        distribution_balance = 1.0 - (np.std(quarters) / mean_quarter) \
                              if mean_quarter > 0 else 0
        distribution_score = distribution_balance * 100
        
        # Classify exposure
        if 90 < l_mean < 165:  # Well exposed
            exposure_class = 'properly_exposed'
            exposure_score = 100 - abs(l_mean - 127.5) / 127.5 * 20
        elif l_mean < 90:  # Underexposed
            exposure_class = 'underexposed'
            exposure_score = max(0, l_mean / 90 * 70)
        else:  # Overexposed
            exposure_class = 'overexposed'
            exposure_score = max(0, (255 - l_mean) / 90 * 70)
        
        # Penalty for clipping
        exposure_score -= (clipped_highlights_pct * 2) + (crushed_blacks_pct * 2)
        exposure_score = max(0, min(100, exposure_score))
        
        # Normalize to 0-1
        exposure_quality = exposure_score / 100.0
        
        # Check if well exposed
        is_well_exposed = (
            90 < l_mean < 165 and 
            clipped_highlights_pct < 5 and 
            crushed_blacks_pct < 5
        )
        
        return {
            'exposure_class': exposure_class,
            'exposure_quality': exposure_quality,
            'brightness': l_mean,
            'contrast': l_std,
            'dynamic_range': dynamic_range,
            'dynamic_range_score': dynamic_range_score / 100.0,
            'clipped_highlights_pct': clipped_highlights_pct,
            'crushed_blacks_pct': crushed_blacks_pct,
            'histogram_balance': distribution_score / 100.0,
            'is_well_exposed': is_well_exposed
        }
    
    def get_description(self) -> str:
        return "Analyzes exposure quality and dynamic range"
