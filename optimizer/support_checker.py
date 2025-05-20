"""
Support checker for the masonry wall simulator.

This module provides the SupportChecker class which checks if bricks
are properly supported by bricks in the courses below.
"""
import sys
import os
# Add the base directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    SUPPORT_THRESHOLD
)

class SupportChecker():
    """
    A class for checking if bricks are properly supported in the wall.
    
    Attributes:
        wall (Wall): The wall object containing brick grid and positions.
    """

    def __init__(self, wall):
        """
        Initialize a SupportChecker.
        
        Args:
            wall (Wall): The wall object to check support for.
        """

        self.wall = wall

    def _is_supported(self, course, position):
        """
        Check if a brick is supported by bricks below it.
        
        Args:
            course (int): The course number (0-based).
            position (int): The position within the course.
            
        Returns:
            bool: True if the brick is supported, False otherwise.
        """
        
        # If it's the first course, it's always supported
        if course == 0:
            return True
        
        # Get the physical position of this brick
        brick = self.wall.brick_positions[course][position]
        brick_start_x = brick['x']
        brick_end_x = brick_start_x + brick['length']
        brick_orientation = brick['orientation']
        
        # Check if there are built bricks below that support this brick
        support_length = 0
        for pos in self.wall.brick_positions[course-1]:
            # Skip if the brick below isn't built
            if self.wall.grid[course-1][pos['position']][1] == 0:
                continue
                
            # If the brick below overlaps with this brick
            if (pos['x'] < brick_end_x and pos['x'] + pos['length'] > brick_start_x):
                # Calculate the overlap
                overlap_start = max(brick_start_x, pos['x'])
                overlap_end = min(brick_end_x, pos['x'] + pos['length'])
                support_length += overlap_end - overlap_start
        
        # Calculate support ratio
        support_ratio = support_length / brick['length']
        
        # Require 'SUPPORT_THRESHOLD' support regardless of bond type or brick orientation
        return support_ratio >= SUPPORT_THRESHOLD
    
    def _would_be_supported(self, course, position, added_bricks):
        """
        Check if a brick would be supported by already built bricks and bricks in added_bricks.
        
        This is used during stride planning to determine which bricks can be placed.
        
        Args:
            course (int): The course number (0-based).
            position (int): The position within the course.
            added_bricks (set): Set of (course, position) tuples of bricks to be added.
            
        Returns:
            bool: True if the brick would be supported, False otherwise.
        """
        # If it's the first course, it's always supported
        if course == 0:
            return True
        
        # Get the physical position of this brick
        brick = self.wall.brick_positions[course][position]
        brick_orientation = brick['orientation']
        
        # Get the support level
        support_ratio = self._calculate_support_level(course, position, added_bricks)

        # Require 'SUPPORT_THRESHOLD' support regardless of bond type or brick orientation
        return support_ratio >= SUPPORT_THRESHOLD
    
    def _calculate_support_level(self, course, position, added_bricks):
        """
        Calculate how much support a brick would have from already added bricks.
        
        Args:
            course (int): The course number (0-based).
            position (int): The position within the course.
            added_bricks (set): Set of (course, position) tuples of bricks to be added.
            
        Returns:
            float: Support ratio (0.0 to 1.0).
        """
        if course == 0:
            return 1.0  # Bottom course is fully supported
        
        # Get the physical position of this brick
        brick = self.wall.brick_positions[course][position]
        brick_start_x = brick['x']
        brick_end_x = brick_start_x + brick['length']
        
        # Check for support from built bricks and bricks in optimized_order
        support_length = 0
        for pos in self.wall.brick_positions[course-1]:
            # If the brick below is already built
            if self.wall.grid[course-1][pos['position']][1] == 1:
                if (pos['x'] < brick_end_x and pos['x'] + pos['length'] > brick_start_x):
                    # Calculate the overlap
                    overlap_start = max(brick_start_x, pos['x'])
                    overlap_end = min(brick_end_x, pos['x'] + pos['length'])
                    support_length += overlap_end - overlap_start
            # Or if the brick below is in the current stride
            elif (course-1, pos['position']) in added_bricks:
                if (pos['x'] < brick_end_x and pos['x'] + pos['length'] > brick_start_x):
                    # Calculate the overlap
                    overlap_start = max(brick_start_x, pos['x'])
                    overlap_end = min(brick_end_x, pos['x'] + pos['length'])
                    support_length += overlap_end - overlap_start
        
        # Return the support ratio (0.0 to 1.0)
        return support_length / brick['length']
