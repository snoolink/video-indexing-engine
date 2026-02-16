"""
Motion Metric

Measures motion between frames using optical flow.
Moderate motion is ideal - not static, not chaotic.
"""

import cv2
import numpy as np
from .base_metric import BaseMetric


class MotionMetric(BaseMetric):
    """
    Calculate motion between frames using optical flow.
    
    Uses dense optical flow (Farneback method) to measure
    movement between consecutive frames.
    
    Range: 0.0 (no motion) to 1.0 (optimal motion)
    """
    
    def __init__(self):
        super().__init__()
        self.low_motion_threshold = 3.0   # Below this is too static
        self.high_motion_threshold = 20.0  # Above this is too chaotic
    
    def calculate(self, frame: np.ndarray, prev_frame: np.ndarray = None, **kwargs) -> float:
        """
        Calculate motion score between two frames.
        
        Args:
            frame: Current video frame (BGR format)
            prev_frame: Previous video frame (BGR format), required!
            
        Returns:
            Motion score (0.0 to 1.0)
        """
        # Motion requires a previous frame
        if prev_frame is None:
            return 0.0
        
        # Convert both frames to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate dense optical flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )
        
        # Calculate magnitude of motion vectors
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        avg_motion = np.mean(magnitude)
        
        # Score based on optimal motion range
        if avg_motion < self.low_motion_threshold:
            # Too static
            score = (avg_motion / self.low_motion_threshold) * 0.5
        elif avg_motion > self.high_motion_threshold:
            # Too chaotic
            score = max(0.0, 1.0 - (avg_motion - self.high_motion_threshold) / 30.0)
        else:
            # Optimal motion range
            motion_range = self.high_motion_threshold - self.low_motion_threshold
            normalized = (avg_motion - self.low_motion_threshold) / motion_range
            score = 0.5 + (normalized * 0.5)
        
        return max(0.0, min(1.0, score))
    
    def get_description(self) -> str:
        return "Measures motion between frames using optical flow, optimal at moderate levels"
