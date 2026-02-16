"""
Person Detection Metric

Detects people in frames and calculates coverage + centering scores.
Uses HOG (Histogram of Oriented Gradients) + SVM detector.
"""

import cv2
import numpy as np
from typing import Tuple
from .base_metric import BaseMetric


class PersonDetectionMetric(BaseMetric):
    """
    Detect people in frames using HOG + SVM.
    
    Returns two scores:
    1. Person score - How well a person is detected and sized
    2. Center focus score - How centered the person is
    
    Range: Each score from 0.0 to 1.0
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize HOG person detector
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Optimal person coverage (20-60% of frame)
        self.optimal_coverage_min = 0.15
        self.optimal_coverage_max = 0.7
    
    def calculate(self, frame: np.ndarray, **kwargs) -> Tuple[float, float]:
        """
        Calculate person detection and center focus scores.
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            Tuple of (person_score, center_focus_score)
        """
        h, w = frame.shape[:2]
        
        # Resize for faster detection
        scale = 0.5
        small_frame = cv2.resize(frame, None, fx=scale, fy=scale)
        
        try:
            # Detect people
            boxes, weights = self.hog.detectMultiScale(
                small_frame,
                winStride=(4, 4),
                padding=(8, 8),
                scale=1.05,
                hitThreshold=0.5
            )
            
            # No person detected
            if len(boxes) == 0:
                return 0.0, 0.0
            
            # Find largest detection (most prominent person)
            max_idx = np.argmax([bw * bh for (bx, by, bw, bh) in boxes])
            best_box = boxes[max_idx]
            x, y, box_w, box_h = best_box
            
            # Scale back to original size
            x = int(x / scale)
            y = int(y / scale)
            box_w = int(box_w / scale)
            box_h = int(box_h / scale)
            
            # Calculate person detection score
            person_score = self._calculate_person_score(
                box_w, box_h, w, h
            )
            
            # Calculate center focus score
            center_focus_score = self._calculate_center_focus(
                x, y, box_w, box_h, w, h
            )
            
            return person_score, center_focus_score
            
        except Exception as e:
            # If detection fails, return neutral scores
            return 0.5, 0.5
    
    def _calculate_person_score(self, box_w: int, box_h: int, 
                                frame_w: int, frame_h: int) -> float:
        """
        Calculate score based on person size in frame.
        
        Optimal is 20-60% of frame area.
        """
        person_area = box_w * box_h
        frame_area = frame_w * frame_h
        coverage = person_area / frame_area
        
        # Score based on coverage
        if coverage < self.optimal_coverage_min:
            # Too small - person is far away
            score = (coverage / self.optimal_coverage_min) * 0.6
        elif coverage > self.optimal_coverage_max:
            # Too large - person is too close
            score = max(0.3, 1.0 - (coverage - self.optimal_coverage_max) / 0.3)
        else:
            # Optimal range
            range_size = self.optimal_coverage_max - self.optimal_coverage_min
            position = (coverage - self.optimal_coverage_min) / range_size
            score = 0.6 + (min(position, 0.4) * 1.0)
        
        return max(0.0, min(1.0, score))
    
    def _calculate_center_focus(self, x: int, y: int, box_w: int, box_h: int,
                                frame_w: int, frame_h: int) -> float:
        """
        Calculate score based on how centered the person is.
        
        Perfect center = 1.0, far from center = 0.0
        """
        # Calculate person center
        person_center_x = x + box_w / 2
        person_center_y = y + box_h / 2
        
        # Calculate frame center
        frame_center_x = frame_w / 2
        frame_center_y = frame_h / 2
        
        # Calculate normalized distance from center
        dist_x = abs(person_center_x - frame_center_x) / (frame_w / 2)
        dist_y = abs(person_center_y - frame_center_y) / (frame_h / 2)
        center_distance = np.sqrt(dist_x**2 + dist_y**2)
        
        # Score decreases as distance from center increases
        score = max(0.0, 1.0 - center_distance * 0.8)
        
        return score
    
    def get_description(self) -> str:
        return "Detects people and scores based on size and centering using HOG + SVM"
