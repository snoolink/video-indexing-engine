"""
Base Metric Class

All metrics inherit from this base class.
Provides a consistent interface for all metric calculations.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Tuple


class BaseMetric(ABC):
    """
    Abstract base class for all metrics.
    
    All metric classes should inherit from this and implement calculate().
    """
    
    def __init__(self):
        """Initialize the metric calculator"""
        self.metric_name = self.__class__.__name__.replace('Metric', '').lower()
    
    @abstractmethod
    def calculate(self, frame: np.ndarray, **kwargs) -> Union[float, Tuple[float, ...]]:
        """
        Calculate the metric for a given frame.
        
        Args:
            frame: Input video frame (BGR format)
            **kwargs: Additional arguments specific to the metric
            
        Returns:
            Metric score(s) between 0.0 and 1.0
        """
        pass
    
    def get_name(self) -> str:
        """Get the metric name"""
        return self.metric_name
    
    def get_description(self) -> str:
        """Get a description of what this metric measures"""
        return self.__doc__ or "No description available"
    
    def normalize(self, value: float, min_val: float, max_val: float) -> float:
        """
        Normalize a value to 0-1 range.
        
        Args:
            value: Value to normalize
            min_val: Minimum possible value
            max_val: Maximum possible value
            
        Returns:
            Normalized value (0.0 to 1.0)
        """
        if max_val == min_val:
            return 0.0
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
