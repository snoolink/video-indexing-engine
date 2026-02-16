"""
Camera Movement Detection Metric

Detects and classifies camera movements with high accuracy.
Uses optical flow and feature tracking.
"""

import cv2
import numpy as np
from typing import Tuple, Dict
from enum import Enum
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from metrics.base_metric import BaseMetric


class CameraMovement(Enum):
    """Types of camera movements detected."""
    STATIC = "Static"
    PAN_LEFT = "Pan Left"
    PAN_RIGHT = "Pan Right"
    TILT_UP = "Tilt Up"
    TILT_DOWN = "Tilt Down"
    ZOOM_IN = "Zoom In"
    ZOOM_OUT = "Zoom Out"
    DOLLY_IN = "Dolly In"
    DOLLY_OUT = "Dolly Out"
    ROTATION_CW = "Rotation CW"
    ROTATION_CCW = "Rotation CCW"
    HANDHELD = "Handheld/Shake"
    COMPLEX = "Complex Movement"


class CameraMovementMetric(BaseMetric):
    """
    Detect and classify camera movement with cinematic quality assessment.
    
    Returns dictionary with movement type, confidence, smoothness, and quality.
    """
    
    def __init__(self):
        super().__init__()
    
    def calculate(self, frame: np.ndarray, prev_frame: np.ndarray = None, **kwargs) -> Dict:
        """
        Calculate camera movement analysis.
        
        Args:
            frame: Current video frame (BGR format)
            prev_frame: Previous video frame (required for motion analysis)
            
        Returns:
            Dictionary with movement analysis
        """
        if prev_frame is None:
            return self._get_static_result()
        
        h, w = frame.shape[:2]
        gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate dense optical flow
        flow = cv2.calcOpticalFlowFarneback(
            gray1, gray2, None,
            pyr_scale=0.5, levels=5, winsize=21,
            iterations=5, poly_n=7, poly_sigma=1.5, flags=0
        )
        
        # Get flow components
        flow_x = flow[..., 0]
        flow_y = flow[..., 1]
        magnitude, angle = cv2.cartToPolar(flow_x, flow_y)
        
        # Calculate statistics
        mean_mag = np.mean(magnitude)
        std_mag = np.std(magnitude)
        mean_x = np.mean(flow_x)
        mean_y = np.mean(flow_y)
        
        # Feature tracking for better accuracy
        scale_factor, rotation_angle, translation_x, translation_y = \
            self._track_features(gray1, gray2)
        
        # Analyze radial flow for zoom detection
        radial_flow = self._calculate_radial_flow(flow_x, flow_y, h, w)
        median_radial = np.median(radial_flow)
        
        # Classify movement
        movement_result = self._classify_movement(
            mean_mag, std_mag, translation_x, translation_y,
            scale_factor, rotation_angle, median_radial
        )
        
        return movement_result
    
    def _track_features(self, gray1, gray2):
        """Track features between frames for accurate motion estimation"""
        corners1 = cv2.goodFeaturesToTrack(gray1, maxCorners=300, qualityLevel=0.01, minDistance=10)
        
        scale_factor = 1.0
        rotation_angle = 0.0
        translation_x = 0.0
        translation_y = 0.0
        
        if corners1 is not None and len(corners1) > 15:
            corners2, status, _ = cv2.calcOpticalFlowPyrLK(
                gray1, gray2, corners1, None,
                winSize=(21, 21), maxLevel=3
            )
            
            if corners2 is not None and status is not None:
                good_old = corners1[status == 1]
                good_new = corners2[status == 1]
                
                if len(good_old) > 15:
                    try:
                        transform_matrix, _ = cv2.estimateAffinePartial2D(
                            good_old, good_new,
                            method=cv2.RANSAC,
                            ransacReprojThreshold=3.0
                        )
                        
                        if transform_matrix is not None:
                            translation_x = transform_matrix[0, 2]
                            translation_y = transform_matrix[1, 2]
                            
                            sx = np.sqrt(transform_matrix[0, 0]**2 + transform_matrix[1, 0]**2)
                            sy = np.sqrt(transform_matrix[0, 1]**2 + transform_matrix[1, 1]**2)
                            scale_factor = (sx + sy) / 2
                            
                            rotation_angle = np.arctan2(transform_matrix[1, 0], 
                                                       transform_matrix[0, 0]) * 180 / np.pi
                    except:
                        pass
        
        return scale_factor, rotation_angle, translation_x, translation_y
    
    def _calculate_radial_flow(self, flow_x, flow_y, h, w):
        """Calculate radial flow from center for zoom detection"""
        center_y, center_x = h // 2, w // 2
        y_coords, x_coords = np.mgrid[0:h, 0:w]
        dx_from_center = x_coords - center_x
        dy_from_center = y_coords - center_y
        distance_from_center = np.sqrt(dx_from_center**2 + dy_from_center**2) + 1e-6
        
        radial_flow = (flow_x * dx_from_center + flow_y * dy_from_center) / distance_from_center
        return radial_flow
    
    def _classify_movement(self, mean_mag, std_mag, translation_x, translation_y,
                          scale_factor, rotation_angle, median_radial):
        """Classify the type of camera movement"""
        motion_threshold = 0.3
        pan_threshold = 0.8
        tilt_threshold = 0.8
        zoom_threshold = 0.15
        rotation_threshold = 0.8
        
        variance_ratio = std_mag / (mean_mag + 1e-6)
        direction_consistency = max(0, min(1, 1.0 - (std_mag / (mean_mag + 1e-6))))
        
        movement_type = CameraMovement.STATIC
        confidence = 0
        cinematic_quality = 50
        smoothness = 100
        
        # Priority 1: Shake/handheld
        if variance_ratio > 1.5 and mean_mag > motion_threshold:
            movement_type = CameraMovement.HANDHELD
            confidence = min(100, variance_ratio * 30)
            cinematic_quality = 30
        
        # Priority 2: Rotation
        elif abs(rotation_angle) > rotation_threshold:
            movement_type = CameraMovement.ROTATION_CCW if rotation_angle > 0 else CameraMovement.ROTATION_CW
            confidence = min(100, abs(rotation_angle) / rotation_threshold * 40)
            cinematic_quality = 75
        
        # Priority 3: Zoom/Dolly
        elif abs(scale_factor - 1.0) > 0.01 or abs(median_radial) > zoom_threshold:
            zoom_strength = max(abs(scale_factor - 1.0) * 50, abs(median_radial))
            is_zoom_in = scale_factor < 1.0 or median_radial < 0
            
            if is_zoom_in:
                movement_type = CameraMovement.ZOOM_IN if direction_consistency > 0.6 else CameraMovement.DOLLY_IN
                cinematic_quality = 85 if direction_consistency > 0.6 else 90
            else:
                movement_type = CameraMovement.ZOOM_OUT if direction_consistency > 0.6 else CameraMovement.DOLLY_OUT
                cinematic_quality = 70 if direction_consistency > 0.6 else 80
            
            confidence = min(100, zoom_strength / zoom_threshold * 60)
        
        # Priority 4: Pan
        elif abs(translation_x) > pan_threshold:
            movement_type = CameraMovement.PAN_RIGHT if translation_x > 0 else CameraMovement.PAN_LEFT
            confidence = min(100, abs(translation_x) / pan_threshold * 60)
            cinematic_quality = 75
        
        # Priority 5: Tilt
        elif abs(translation_y) > tilt_threshold:
            movement_type = CameraMovement.TILT_DOWN if translation_y > 0 else CameraMovement.TILT_UP
            confidence = min(100, abs(translation_y) / tilt_threshold * 60)
            cinematic_quality = 70
        
        # Priority 6: Complex movement
        elif mean_mag > motion_threshold:
            movement_type = CameraMovement.COMPLEX
            confidence = min(100, mean_mag / motion_threshold * 40)
            cinematic_quality = 65
        
        else:
            # Static
            movement_type = CameraMovement.STATIC
            confidence = 100
            cinematic_quality = 50
        
        # Calculate smoothness
        if mean_mag > 0.1:
            smoothness = max(0, 100 - (variance_ratio * 30))
        
        # Adjust cinematic quality based on smoothness
        if movement_type not in [CameraMovement.STATIC, CameraMovement.HANDHELD]:
            smoothness_bonus = (smoothness / 100) * 25
            cinematic_quality = min(100, cinematic_quality + smoothness_bonus)
        
        return {
            'movement_type': movement_type.value,
            'confidence': confidence,
            'magnitude': mean_mag,
            'smoothness': smoothness,
            'cinematic_quality': cinematic_quality,
            'direction_consistency': direction_consistency,
            'scale_factor': scale_factor,
            'rotation_angle': rotation_angle
        }
    
    def _get_static_result(self):
        """Return result for static/no previous frame case"""
        return {
            'movement_type': CameraMovement.STATIC.value,
            'confidence': 0,
            'magnitude': 0,
            'smoothness': 100,
            'cinematic_quality': 50,
            'direction_consistency': 1.0,
            'scale_factor': 1.0,
            'rotation_angle': 0.0
        }
    
    def get_description(self) -> str:
        return "Detects camera movement type with cinematic quality assessment"

