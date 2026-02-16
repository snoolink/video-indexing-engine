"""
Shot Framing Analysis Metric

Analyzes shot size/framing type and composition.
Detects extreme close-up, close-up, medium, wide, extreme wide shots.
"""

import cv2
import numpy as np
from typing import Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from metrics.base_metric import BaseMetric


class ShotFramingMetric(BaseMetric):
    """
    Analyze shot size/framing type.
    
    Shot types:
    - extreme_close_up (face details)
    - close_up (head and shoulders)
    - medium (waist up)
    - wide (full body)
    - extreme_wide (establishing shot)
    - insert (object detail)
    
    Range: 0.0 (poor composition) to 1.0 (excellent composition)
    """
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, frame: np.ndarray, **kwargs) -> Dict:
        """
        Calculate shot framing and composition.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Dictionary with shot framing analysis
        """
        h, w = frame.shape[:2]
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Edge detection to find subjects
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours (potential subjects)
        contours, _ = cv2.findContours(
            edges, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            return self._get_default_result()
        
        # Find largest contour (assumed main subject)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, cw, ch = cv2.boundingRect(largest_contour)
        
        # Calculate subject size relative to frame
        subject_area = cw * ch
        frame_area = w * h
        subject_ratio = subject_area / frame_area
        
        # Classify shot size based on subject ratio
        shot_size, description = self._classify_shot_size(
            subject_ratio, cw, ch, w, h
        )
        
        # Analyze composition
        composition_analysis = self._analyze_composition(
            gray, edges, x, y, cw, ch, w, h
        )
        
        return {
            'shot_size': shot_size,
            'description': description,
            'subject_ratio': subject_ratio * 100,
            'subject_position': {
                'x': x, 'y': y, 
                'width': cw, 'height': ch
            },
            'composition_score': composition_analysis['score'] / 100.0,
            'rule_of_thirds_score': composition_analysis['thirds_score'] / 100.0,
            'has_good_composition': composition_analysis['score'] > 60,
            'follows_rule_of_thirds': composition_analysis['thirds_score'] > 60
        }
    
    def _classify_shot_size(self, subject_ratio, cw, ch, w, h):
        """Classify shot size based on subject coverage"""
        if subject_ratio > 0.6:
            shot_size = 'extreme_close_up'
            description = 'Extreme close-up (face details)'
        elif subject_ratio > 0.35:
            shot_size = 'close_up'
            description = 'Close-up (head and shoulders)'
        elif subject_ratio > 0.15:
            shot_size = 'medium'
            description = 'Medium shot (waist up)'
        elif subject_ratio > 0.05:
            shot_size = 'wide'
            description = 'Wide shot (full body)'
        else:
            shot_size = 'extreme_wide'
            description = 'Extreme wide (establishing shot)'
        
        # Additional detection: Insert shot (small object detail)
        if subject_ratio > 0.4 and cw < w * 0.6 and ch < h * 0.6:
            shot_size = 'insert'
            description = 'Insert (object detail)'
        
        return shot_size, description
    
    def _analyze_composition(self, gray, edges, x, y, cw, ch, w, h):
        """Analyze composition quality using rule of thirds"""
        # Calculate rule of thirds lines
        third_w = w / 3
        third_h = h / 3
        
        # Power points (intersections of thirds)
        power_points = [
            (third_w, third_h),
            (2 * third_w, third_h),
            (third_w, 2 * third_h),
            (2 * third_w, 2 * third_h)
        ]
        
        # Calculate subject center
        subject_center_x = x + cw / 2
        subject_center_y = y + ch / 2
        
        # Find distance to nearest power point
        min_distance = float('inf')
        for px, py in power_points:
            distance = np.sqrt((subject_center_x - px)**2 + (subject_center_y - py)**2)
            min_distance = min(min_distance, distance)
        
        # Score based on proximity to power points
        max_acceptable_distance = min(w, h) * 0.1
        proximity_score = max(0, 100 - (min_distance / max_acceptable_distance * 100))
        
        # Check horizon placement
        horizontal_edges = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        horizontal_edges = np.abs(horizontal_edges)
        row_strengths = np.sum(horizontal_edges, axis=1)
        horizon_y = np.argmax(row_strengths)
        
        # Check if horizon is near a thirds line
        if abs(horizon_y - third_h) < h * 0.05 or abs(horizon_y - 2 * third_h) < h * 0.05:
            horizon_score = 100
        else:
            dist_to_third = min(abs(horizon_y - third_h), abs(horizon_y - 2 * third_h))
            horizon_score = max(0, 100 - (dist_to_third / third_h * 100))
        
        # Check for negative space
        left_space = x
        right_space = w - (x + cw)
        top_space = y
        bottom_space = h - (y + ch)
        
        total_space = left_space + right_space + top_space + bottom_space
        frame_perimeter = 2 * (w + h)
        negative_space_ratio = total_space / frame_perimeter
        
        # Good negative space = 0.3 to 0.7
        if 0.3 < negative_space_ratio < 0.7:
            negative_space_score = 100
        else:
            negative_space_score = max(0, 100 - abs(negative_space_ratio - 0.5) * 200)
        
        # Overall composition score
        composition_score = (
            proximity_score * 0.4 + 
            horizon_score * 0.3 + 
            negative_space_score * 0.3
        )
        
        return {
            'score': composition_score,
            'thirds_score': proximity_score,
            'horizon_score': horizon_score,
            'negative_space_score': negative_space_score
        }
    
    def _get_default_result(self):
        """Return default result when no subject is detected"""
        return {
            'shot_size': 'unknown',
            'description': 'Unable to detect subject',
            'subject_ratio': 0,
            'subject_position': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
            'composition_score': 0.5,
            'rule_of_thirds_score': 0.5,
            'has_good_composition': False,
            'follows_rule_of_thirds': False
        }
    
    def get_description(self) -> str:
        return "Analyzes shot framing type and composition quality"
