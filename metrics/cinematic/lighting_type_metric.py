"""
Lighting Type Classification Metric

Classifies lighting type and quality.
Detects golden hour, blue hour, high key, low key, natural, backlit, etc.
"""

import cv2
import numpy as np
from typing import Dict, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from metrics.base_metric import BaseMetric


class LightingTypeMetric(BaseMetric):
    """
    Classify lighting type and quality.
    
    Detects:
    - golden_hour (warm, soft, cinematic)
    - blue_hour (cool twilight)
    - high_key (bright, low contrast)
    - low_key (dark, dramatic, high contrast)
    - natural (daylight, even)
    - backlit (silhouettes, high contrast)
    - three_point (studio lighting)
    - motivated (realistic light sources)
    
    Range: 0.0 (poor) to 1.0 (excellent)
    """
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, frame: np.ndarray, **kwargs) -> Dict:
        """
        Calculate lighting type and quality.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Dictionary with lighting classification
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        b_channel = lab[:, :, 2]  # Blue-Yellow axis
        
        # Calculate statistics
        l_mean = np.mean(l_channel)
        l_std = np.std(l_channel)
        l_min = np.min(l_channel)
        l_max = np.max(l_channel)
        b_mean = np.mean(b_channel)
        
        # Calculate histogram
        hist = cv2.calcHist([l_channel], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()
        
        # Detect lighting types
        lighting_types = []
        confidence_scores = {}
        
        # Golden Hour (warm, soft, low contrast in highlights)
        if b_mean > 135 and 100 < l_mean < 180 and l_std < 50:
            lighting_types.append('golden_hour')
            confidence_scores['golden_hour'] = min((b_mean - 128) / 20 * 100, 100)
        
        # Blue Hour (cool, even lighting)
        elif b_mean < 115 and 80 < l_mean < 150:
            lighting_types.append('blue_hour')
            confidence_scores['blue_hour'] = 70
        
        # Natural/Daylight (good exposure, moderate contrast)
        if 100 < l_mean < 180 and 30 < l_std < 60:
            lighting_types.append('natural')
            confidence_scores['natural'] = 75
        
        # High Key (bright, low contrast)
        if l_mean > 170 and l_std < 40:
            lighting_types.append('high_key')
            confidence_scores['high_key'] = min((l_mean - 170) / 85 * 100, 100)
        
        # Low Key (dark, high contrast, dramatic)
        elif l_mean < 100 and l_std > 45:
            lighting_types.append('low_key')
            confidence_scores['low_key'] = min((100 - l_mean) / 100 * 100, 100)
        
        # Backlit (high contrast with dark foreground)
        dark_ratio = np.sum(hist[0:50])
        bright_ratio = np.sum(hist[200:256])
        
        if dark_ratio > 0.3 and bright_ratio > 0.2 and l_std > 50:
            lighting_types.append('backlit')
            confidence_scores['backlit'] = 80
        
        # Three-Point Lighting (even distribution, studio look)
        quarters = [np.sum(hist[i*64:(i+1)*64]) for i in range(4)]
        if all(0.15 < q < 0.35 for q in quarters):
            lighting_types.append('three_point')
            confidence_scores['three_point'] = 70
        
        # Motivated Lighting (realistic light sources)
        if 90 < l_mean < 170 and 25 < l_std < 55:
            lighting_types.append('motivated')
            confidence_scores['motivated'] = 60
        
        # Default if no strong classification
        if not lighting_types:
            lighting_types.append('unknown')
            confidence_scores['unknown'] = 50
        
        # Get dominant type
        dominant_type = max(confidence_scores.items(), key=lambda x: x[1])[0] \
                       if confidence_scores else 'unknown'
        
        # Calculate overall quality score
        quality_score = confidence_scores.get(dominant_type, 50) / 100.0
        
        return {
            'dominant_type': dominant_type,
            'confidence_scores': confidence_scores,
            'all_types': lighting_types,
            'brightness': l_mean,
            'contrast': l_std,
            'dynamic_range': l_max - l_min,
            'is_warm': b_mean > 130,
            'is_cool': b_mean < 125,
            'is_dramatic': l_std > 50,
            'quality_score': quality_score
        }
    
    def get_description(self) -> str:
        return "Classifies lighting type (golden hour, low key, high key, etc.)"
