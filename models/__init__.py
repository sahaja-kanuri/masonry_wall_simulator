"""
Package initialization file for the masonry simulator models.

This file makes key classes from the models package available at the package level.
"""

import sys
import os
# Add project root to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.wall import Wall

__all__ = ['Wall']