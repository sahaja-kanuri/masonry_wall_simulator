"""
Package initialization file for the masonry simulator patterns.

This file makes key functions from the bonds package available at the package level.
"""

import sys
import os
# Add project root to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bonds.stretcher import _initialize_stretcher_course
from bonds.stretcher import _get_optimal_starting_position as _stretcher__starting_position
from bonds.english_cross import _initialize_english_cross_course
from bonds.english_cross import _get_optimal_starting_position as _englishCross__starting_position
from bonds.wild import _initialize_wild_bond_course
from bonds.wild import _get_optimal_starting_position as _wild__starting_position

__all__ = [
    '_initialize_stretcher_course', 
    '_initialize_english_cross_course', 
    '_initialize_wild_bond_course',
    '_stretcher__starting_position',
    '_englishCross__starting_position',
    '_wild__starting_position'
]