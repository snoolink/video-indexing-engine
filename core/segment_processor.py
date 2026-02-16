"""
Segment Processor Module

Processes video segments and aggregates metrics from individual frames.
Uses the MetricsManager to calculate all metrics.
"""

import numpy as np
from typing import List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_models import ScoreMetrics
from core.metrics_manager import MetricsManager


class SegmentProcessor:
    """
    Processes video segments and calculates aggregate metrics.
    
    Takes a list of frames and returns a ScoreMetrics object with
    all metrics calculated and averaged over the segment.
    """
    
    def __init__(self):
        """Initialize the segment processor with metrics manager"""
        self.metrics_manager = MetricsManager()
    
    def process_segment(self, frames: List[np.ndarray]) -> ScoreMetrics:
        """
        Calculate all metrics for a list of frames representing a segment.
        
        Samples frames at different intervals for different metrics to
        optimize performance while maintaining accuracy.
        
        Args:
            frames: List of video frames (BGR format) representing a segment
            
        Returns:
            ScoreMetrics object with all calculated and averaged metrics
        """
        metrics = ScoreMetrics()
        
        # Storage for individual frame scores - Basic metrics
        sharpness_scores = []
        brightness_scores = []
        contrast_scores = []
        color_scores = []
        motion_scores = []
        composition_scores = []
        person_scores = []
        center_focus_scores = []
        
        # Storage for cinematic metrics
        camera_movements = []
        stabilization_data = []
        focus_data = []
        lighting_data = []
        color_grading_data = []
        exposure_data = []
        framing_data = []
        
        prev_frame = None
        
        for i, frame in enumerate(frames):
            # Sample every 3rd frame for basic metrics (performance optimization)
            if i % 3 == 0:
                # Basic metrics
                sharpness_scores.append(
                    self.metrics_manager.calculate_sharpness(frame)
                )
                brightness_scores.append(
                    self.metrics_manager.calculate_brightness(frame)
                )
                contrast_scores.append(
                    self.metrics_manager.calculate_contrast(frame)
                )
                color_scores.append(
                    self.metrics_manager.calculate_color_vibrancy(frame)
                )
                composition_scores.append(
                    self.metrics_manager.calculate_composition(frame)
                )
                
                # Person detection every 6th frame (more expensive operation)
                if i % 6 == 0:
                    person_score, center_score = \
                        self.metrics_manager.calculate_person_detection(frame)
                    person_scores.append(person_score)
                    center_focus_scores.append(center_score)
                
                # Motion requires previous frame
                if prev_frame is not None:
                    motion_scores.append(
                        self.metrics_manager.calculate_motion(frame, prev_frame)
                    )
                
                # Cinematic metrics every 6th frame (more expensive)
                if i % 6 == 0 and prev_frame is not None:
                    # Camera movement analysis
                    cam_movement = self.metrics_manager.calculate_camera_movement(
                        frame, prev_frame
                    )
                    camera_movements.append(cam_movement)
                    
                    # Stabilization quality
                    stabilization = self.metrics_manager.calculate_stabilization(
                        frame, prev_frame
                    )
                    stabilization_data.append(stabilization)
                    
                    # Focus change detection
                    focus = self.metrics_manager.calculate_focus_change(
                        frame, prev_frame
                    )
                    focus_data.append(focus)
                    
                    # Lighting type
                    lighting = self.metrics_manager.calculate_lighting_type(frame)
                    lighting_data.append(lighting)
                    
                    # Color grading
                    grading = self.metrics_manager.calculate_color_grading(frame)
                    color_grading_data.append(grading)
                    
                    # Exposure quality
                    exposure = self.metrics_manager.calculate_exposure(frame)
                    exposure_data.append(exposure)
                    
                    # Shot framing
                    framing = self.metrics_manager.calculate_shot_framing(frame)
                    framing_data.append(framing)
                
                prev_frame = frame.copy()
        
        # Aggregate basic scores by averaging
        metrics.sharpness = np.mean(sharpness_scores) if sharpness_scores else 0.0
        metrics.brightness = np.mean(brightness_scores) if brightness_scores else 0.0
        metrics.contrast = np.mean(contrast_scores) if contrast_scores else 0.0
        metrics.color_vibrancy = np.mean(color_scores) if color_scores else 0.0
        metrics.motion_score = np.mean(motion_scores) if motion_scores else 0.0
        metrics.composition_score = np.mean(composition_scores) if composition_scores else 0.0
        metrics.person_score = np.mean(person_scores) if person_scores else 0.5
        metrics.center_focus_score = np.mean(center_focus_scores) if center_focus_scores else 0.5
        
        # Aggregate cinematic metrics
        self._aggregate_camera_movement(metrics, camera_movements)
        self._aggregate_stabilization(metrics, stabilization_data)
        self._aggregate_focus(metrics, focus_data)
        self._aggregate_lighting(metrics, lighting_data)
        self._aggregate_color_grading(metrics, color_grading_data)
        self._aggregate_exposure(metrics, exposure_data)
        self._aggregate_framing(metrics, framing_data)
        
        return metrics
    
    def _aggregate_camera_movement(self, metrics: ScoreMetrics, data: list):
        """Aggregate camera movement metrics"""
        if not data:
            return
        
        # Get most common movement type
        movement_types = [d['movement_type'] for d in data]
        metrics.camera_movement_type = max(set(movement_types), key=movement_types.count)
        
        # Average quality metrics
        metrics.camera_movement_quality = np.mean([d['cinematic_quality'] for d in data]) / 100.0
        metrics.camera_movement_smoothness = np.mean([d['smoothness'] for d in data]) / 100.0
        metrics.camera_movement_confidence = np.mean([d['confidence'] for d in data]) / 100.0
    
    def _aggregate_stabilization(self, metrics: ScoreMetrics, data: list):
        """Aggregate stabilization metrics"""
        if not data:
            return
        
        stab_types = [d['stabilization_type'] for d in data]
        metrics.stabilization_type = max(set(stab_types), key=stab_types.count)
        metrics.stabilization_score = np.mean([d['stabilization_score'] for d in data])
    
    def _aggregate_focus(self, metrics: ScoreMetrics, data: list):
        """Aggregate focus change metrics"""
        if not data:
            return
        
        # Check if any frame had focus change
        metrics.focus_has_change = any(d['has_focus_change'] for d in data)
        metrics.focus_change_amount = np.mean([d['focus_change_amount'] for d in data])
        metrics.focus_sharpness = np.mean([d['current_sharpness'] for d in data])
        metrics.focus_has_bokeh = any(d['has_shallow_dof'] for d in data)
    
    def _aggregate_lighting(self, metrics: ScoreMetrics, data: list):
        """Aggregate lighting type metrics"""
        if not data:
            return
        
        lighting_types = [d['dominant_type'] for d in data]
        metrics.lighting_type = max(set(lighting_types), key=lighting_types.count)
        metrics.lighting_quality = np.mean([d['quality_score'] for d in data])
        metrics.lighting_is_dramatic = any(d['is_dramatic'] for d in data)
    
    def _aggregate_color_grading(self, metrics: ScoreMetrics, data: list):
        """Aggregate color grading metrics"""
        if not data:
            return
        
        grading_styles = [d['dominant_profile'] for d in data]
        metrics.color_grading_style = max(set(grading_styles), key=grading_styles.count)
        metrics.color_grading_strength = np.mean([d['grading_strength'] for d in data])
        metrics.color_saturation = np.mean([d['saturation_level'] for d in data])
        metrics.color_warmth = np.mean([d['warmth_level'] for d in data])
    
    def _aggregate_exposure(self, metrics: ScoreMetrics, data: list):
        """Aggregate exposure metrics"""
        if not data:
            return
        
        exposure_classes = [d['exposure_class'] for d in data]
        metrics.exposure_quality = max(set(exposure_classes), key=exposure_classes.count)
        metrics.exposure_score = np.mean([d['exposure_quality'] for d in data])
        metrics.exposure_is_well_exposed = all(d['is_well_exposed'] for d in data)
    
    def _aggregate_framing(self, metrics: ScoreMetrics, data: list):
        """Aggregate shot framing metrics"""
        if not data:
            return
        
        framing_types = [d['shot_size'] for d in data]
        metrics.shot_framing_type = max(set(framing_types), key=framing_types.count)
        metrics.shot_composition_score = np.mean([d['composition_score'] for d in data])
        metrics.shot_follows_rule_of_thirds = any(d['follows_rule_of_thirds'] for d in data)
    
    def get_sampling_info(self) -> dict:
        """
        Get information about frame sampling strategy.
        
        Returns:
            Dictionary with sampling details for each metric type
        """
        return {
            'basic_metrics': {
                'metrics': ['sharpness', 'brightness', 'contrast', 
                           'color_vibrancy', 'composition'],
                'sampling': 'every 3rd frame',
                'reason': 'balance between accuracy and performance'
            },
            'person_detection': {
                'metrics': ['person_score', 'center_focus_score'],
                'sampling': 'every 6th frame',
                'reason': 'expensive operation, less temporal variation'
            },
            'motion_detection': {
                'metrics': ['motion_score'],
                'sampling': 'every 3rd frame',
                'reason': 'requires consecutive frames, moderate cost'
            }
        }
    
    def get_available_metrics(self) -> List[str]:
        """Get list of all available metrics"""
        return self.metrics_manager.get_available_metrics()
