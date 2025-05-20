"""
Wall class for the masonry wall simulator.

This module defines the Wall class which represents the entire masonry wall structure.
"""

import sys
import os
# Add the base directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root to sys.path
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    NUM_COURSES, COURSE_HEIGHT, 
    STRETCHER_BOND, ENGLISH_CROSS_BOND, WILD_BOND,
    FULL_BRICK_LENGTH, FULL_BRICK_WIDTH, FULL_BRICK_HEIGHT, 
    HEAD_JOINT, STRIDE_WIDTH, STRIDE_HEIGHT
)

from bonds.stretcher import _initialize_stretcher_course
from bonds.stretcher import _get_optimal_starting_position as _stretcher__starting_position
from bonds.english_cross import _initialize_english_cross_course
from bonds.english_cross import _get_optimal_starting_position as _englishCross__starting_position
from bonds.wild import _initialize_wild_bond_course
from bonds.wild import _get_optimal_starting_position as _wild__starting_position

# from optimizer.stride_optimizer import StrideOptimizer
# from optimizer.support_checker import SupportChecker

class Wall:
    """
    A class representing the entire masonry wall.
    The wall consists of multiple courses (rows) of bricks with a specific bond pattern.
    """

    def __init__(self, width, height, bond_type=STRETCHER_BOND):
        """
        Initialize a new Wall object.
        
        Args:
            width (float): Wall width in mm.
            height (float): Wall height in mm.
            bond_type (int, optional): Bond pattern type. Defaults to STRETCHER_BOND.
        """
        self.width = width
        self.height = height
        self.bond_type = bond_type
        self.courses = NUM_COURSES
        self.grid = self._initialize_wall()
        self.current_stride = 0  # Color index for the current stride
        self.stride_map = {}  # Maps (row, col) to stride number
        
        # Stats tracking
        self.total_bricks = sum(len(row) for row in self.grid)
        self.placed_bricks = 0
        self.strides_used = 0
        self.total_movement_cost = 0
        
        # Calculate physical positions of each brick for stride optimization
        self._calculate_brick_positions()

        # self.support_checker = SupportChecker(self)
        # self.stride_optimizer = StrideOptimizer(self, self.support_checker)
        
        # Choose optimal starting position based on bond type
        if bond_type==STRETCHER_BOND:
            self.robot_position = _stretcher__starting_position(self)
        elif bond_type==ENGLISH_CROSS_BOND:
            self.robot_position = _englishCross__starting_position(self)
        elif bond_type==WILD_BOND:
            self.robot_position = _wild__starting_position(self)
        
        # Current stride bricks queue
        self.current_stride_bricks = []
        
        # Flag to track if we've started a new stride
        self.new_stride_started = False
        
        # Info for displaying instructions
        self.message = "Select bond type with 1/2/3; press ENTER to place bricks"
        # self.message_time = 0
        
        # Flag to track if the current stride has had any bricks placed
        self.current_stride_active = False
        
        # Flag to track if we need to count a stride
        self.stride_needs_counting = True
      
    def _initialize_wall(self):
        """Initialize the wall with the appropriate bond pattern."""
        wall = []
        
        for course in range(self.courses):
            if self.bond_type == STRETCHER_BOND:
                row = _initialize_stretcher_course(course)
            elif self.bond_type == ENGLISH_CROSS_BOND:
                row = _initialize_english_cross_course(course)
            elif self.bond_type == WILD_BOND:
                row = _initialize_wild_bond_course(course, wall)
            
            wall.append(row)
        
        return wall
    
    def _calculate_brick_positions(self):
        """Calculate the physical position of each brick in mm from bottom left."""
        self.brick_positions = []
        
        for course in range(self.courses):
            course_positions = []
            x_pos = 0
            y_pos = course * COURSE_HEIGHT
            
            for i, brick_info in enumerate(self.grid[course]):
                brick_length, _, orientation = brick_info
                
                # For headers, we need to adjust the visual dimensions
                visual_length = brick_length
                visual_height = FULL_BRICK_HEIGHT
                real_width = FULL_BRICK_WIDTH if orientation == 'stretcher' else FULL_BRICK_LENGTH
                
                course_positions.append({
                    'x': x_pos,
                    'y': y_pos,
                    'length': visual_length,  # Visual length on wall face
                    'height': visual_height,
                    'width': real_width,      # Actual width into the wall
                    'course': course,
                    'position': i,
                    'orientation': orientation
                })
                x_pos += brick_length + HEAD_JOINT
            
            self.brick_positions.append(course_positions)

    def _get_optimal_starting_position(self):
        """
        Determine the optimal starting position based on bond type and wall structure.
        
        Returns:
            tuple: (x, y) coordinates for robot starting position.
        """
        # This will be moved to the pattern-specific modules
        # Placeholder - start in the center of the first course
        return (self.width / 2, 0)
    
    def has_unbuilt_bricks(self):
        """Check if there are any unbuilt bricks left."""
        return self.placed_bricks < self.total_bricks
    
    def is_complete(self):
        """Check if the wall is complete."""
        return self.placed_bricks == self.total_bricks
    
    def brick_in_stride(self, course, position, stride_x, stride_y):
        """
        Check if a brick is within the current stride bounds.
        
        Args:
            course (int): The course number (0-based).
            position (int): The position within the course.
            stride_x (float): The x-coordinate of the stride's bottom-left corner.
            stride_y (float): The y-coordinate of the stride's bottom-left corner.
            
        Returns:
            bool: True if the brick is within the stride bounds, False otherwise.
        """

        brick = self.brick_positions[course][position]
        
        # Check if the brick is within the stride bounds
        return (brick['x'] >= stride_x and 
                brick['x'] + brick['length'] <= stride_x + STRIDE_WIDTH and
                brick['y'] >= stride_y and 
                brick['y'] + brick['height'] <= stride_y + STRIDE_HEIGHT)
    
    