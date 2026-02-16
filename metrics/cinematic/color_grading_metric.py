"""
Color Grading Style Detection Metric

Detects color grading style/look.
Identifies warm, cool, teal-orange, vintage, monochrome, etc.
"""

import cv2
import numpy as np
from typing import Dict, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from metrics.base_metric import BaseMetric


class ColorGradingMetric(BaseMetric):
    """
    Detect color grading style/look.
    
    Profiles detected:
    - warm (golden, sunset tones)
    - cool (blue/teal)
    - teal_orange (Hollywood look)
    - desaturated (muted, cinematic)
    - vibrant (saturated, colorful)
    - monochrome (black and white)
    - vintage (film-like)
    - neutral (no strong grading)
    
    Range: 0.0 (no grading) to 1.0 (strong grading)
    """
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, frame: np.ndarray, **kwargs) -> Dict:
        """
        Calculate color grading style.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Dictionary with color grading profile
        """
        # Convert to multiple color spaces
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        # Extract channels
        h, s, v = cv2.split(hsv)
        l, a, b = cv2.split(lab)
        
        # Calculate statistics
        saturation_mean = np.mean(s)
        saturation_std = np.std(s)
        value_mean = np.mean(v)
        
        # Blue-Yellow axis (b channel in LAB)
        b_mean = np.mean(b)
        # Green-Red axis (a channel in LAB)
        a_mean = np.mean(a)
        
        profiles = []
        confidence_scores = {}
        
        # Warm (golden hour, sunset tones) - high b channel
        if b_mean > 135:
            profiles.append('warm')
            confidence_scores['warm'] = min((b_mean - 128) / 127 * 100, 100)
        
        # Cool (blue/teal) - low b channel
        elif b_mean < 120:
            profiles.append('cool')
            confidence_scores['cool'] = min((128 - b_mean) / 128 * 100, 100)
        
        # Desaturated (low saturation, muted)
        if saturation_mean < 80:
            profiles.append('desaturated')
            confidence_scores['desaturated'] = (1 - saturation_mean / 255) * 100
        
        # Vibrant (high saturation)
        elif saturation_mean > 150:
            profiles.append('vibrant')
            confidence_scores['vibrant'] = (saturation_mean / 255) * 100
        
        # Monochrome (very low saturation)
        if saturation_mean < 20:
            profiles.append('monochrome')
            confidence_scores['monochrome'] = (1 - saturation_mean / 20) * 100
        
        # Teal-Orange (Hollywood look)
        # Check for teal (cyan) in shadows and orange in highlights
        dark_pixels = frame[v < 100]
        bright_pixels = frame[v > 155]
        
        if len(dark_pixels) > 0 and len(bright_pixels) > 0:
            dark_b_mean = np.mean(dark_pixels[:, 0])  # Blue channel
            bright_r_mean = np.mean(bright_pixels[:, 2])  # Red channel
            
            if dark_b_mean > 120 and bright_r_mean > 140:
                profiles.append('teal_orange')
                confidence_scores['teal_orange'] = 75
        
        # Vintage (desaturated with warm tones)
        if saturation_mean < 100 and b_mean > 130:
            profiles.append('vintage')
            confidence_scores['vintage'] = 70
        
        # Default to neutral if no strong profile
        if not profiles:
            profiles.append('neutral')
            confidence_scores['neutral'] = 50
        
        # Get dominant profile
        dominant_profile = max(confidence_scores.items(), key=lambda x: x[1])[0] \
                          if confidence_scores else 'neutral'
        
        # Calculate overall grading strength
        grading_strength = confidence_scores.get(dominant_profile, 50) / 100.0
        
        return {
            'dominant_profile': dominant_profile,
            'all_profiles': profiles,
            'confidence_scores': confidence_scores,
            'saturation_level': saturation_mean,
            'warmth_level': b_mean,
            'brightness_level': value_mean,
            'grading_strength': grading_strength,
            'is_colorful': saturation_mean > 100,
            'is_muted': saturation_mean < 60,
            'is_warm': b_mean > 130,
            'is_cool': b_mean < 125
        }
    
    def get_description(self) -> str:
        return "Detects color grading style (warm/cool/teal-orange/vintage/etc.)"
