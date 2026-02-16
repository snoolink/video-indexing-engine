"""
Stabilization Quality Metric

Assesses camera stabilization quality.
Detects tripod, gimbal, handheld stabilized, or handheld unstabilized.
"""

import cv2
import numpy as np
from typing import Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from metrics.base_metric import BaseMetric


class StabilizationMetric(BaseMetric):
    """
    Assess camera stabilization quality.
    
    Classifies stabilization type:
    - tripod (locked off, very stable)
    - gimbal (smooth, stabilized movement)
    - handheld_stabilized (IBIS/OIS, moderate stability)
    - handheld_unstabilized (shaky)
    
    Range: 0.0 (unstable) to 1.0 (perfectly stable)
    """
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, frame: np.ndarray, prev_frame: np.ndarray = None, **kwargs) -> Dict:
        """
        Calculate stabilization quality.
        
        Args:
            frame: Current video frame (BGR format)
            prev_frame: Previous video frame (required for analysis)
            
        Returns:
            Dictionary with stabilization type and score
        """
        if prev_frame is None:
            return {
                'stabilization_type': 'unknown',
                'stabilization_score': 0.5,
                'motion_consistency': 0.0
            }
        
        gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect feature points
        corners1 = cv2.goodFeaturesToTrack(
            gray1, 
            maxCorners=300, 
            qualityLevel=0.01, 
            minDistance=10
        )
        
        if corners1 is None or len(corners1) < 20:
            return {
                'stabilization_type': 'unknown',
                'stabilization_score': 0.5,
                'motion_consistency': 0.0
            }
        
        # Track features
        corners2, status, _ = cv2.calcOpticalFlowPyrLK(
            gray1, gray2, corners1, None,
            winSize=(21, 21),
            maxLevel=3
        )
        
        if corners2 is None or status is None:
            return {
                'stabilization_type': 'unknown',
                'stabilization_score': 0.5,
                'motion_consistency': 0.0
            }
        
        # Filter good matches
        good_old = corners1[status == 1]
        good_new = corners2[status == 1]
        
        if len(good_old) < 20:
            return {
                'stabilization_type': 'unknown',
                'stabilization_score': 0.5,
                'motion_consistency': 0.0
            }
        
        # Calculate motion vectors
        motion_vectors = good_new - good_old
        
        # Calculate consistency of motion (how similar are all vectors)
        motion_std = np.std(motion_vectors, axis=0)
        motion_mean = np.mean(np.abs(motion_vectors), axis=0)
        
        # Consistency score (low std relative to mean = high consistency)
        motion_consistency = 1.0 / (1.0 + np.mean(motion_std))
        
        # Normalized score (0-1)
        stabilization_score = motion_consistency
        
        # Classify stabilization type
        if stabilization_score >= 0.95:
            stabilization_type = 'tripod'
            description = 'Locked-off, tripod-mounted'
        elif stabilization_score >= 0.85:
            stabilization_type = 'gimbal'
            description = 'Gimbal-stabilized or high-quality steadicam'
        elif stabilization_score >= 0.70:
            stabilization_type = 'handheld_stabilized'
            description = 'Handheld with stabilization (IBIS/OIS)'
        else:
            stabilization_type = 'handheld_unstabilized'
            description = 'Handheld without stabilization'
        
        return {
            'stabilization_type': stabilization_type,
            'stabilization_score': stabilization_score,
            'motion_consistency': motion_consistency,
            'description': description,
            'is_stable': stabilization_score >= 0.85
        }
    
    def get_description(self) -> str:
        return "Assesses camera stabilization quality (tripod/gimbal/handheld)"
