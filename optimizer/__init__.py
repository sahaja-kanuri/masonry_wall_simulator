"""
Package initialization file for the masonry simulator optimizer components.

This file makes key classes from the optimizer package available at the package level.
"""

import sys
import os
# Add project root to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimizer.support_checker import SupportChecker
from optimizer.brick_placer import BrickPlacer
from optimizer.stride_optimizer import StrideOptimizer

__all__ = ['SupportChecker', 'BrickPlacer', 'StrideOptimizer']