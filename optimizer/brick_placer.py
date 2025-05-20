"""
Brick placer for the masonry wall simulator.

This module provides the BrickPlacer class which handles the logic
for placing bricks in the wall.
"""

import sys
import os
# Add the base directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    HORIZONTAL_MOVE_COST, VERTICAL_MOVE_COST
)

class BrickPlacer():
    """
    A class for placing bricks in the wall.
    
    This class handles the mechanics of placing individual bricks
    and groups of bricks (strides).
    
    Attributes:
        wall (Wall): The wall object containing brick grid and positions.
        support_checker (SupportChecker): For checking brick support.
        stride_optimizer (StrideOptimizer): For optimizing stride placement.
    """
    def __init__(self, wall, support_checker, stride_optimizer):
        """
        Initialize a BrickPlacer.

        Args:
            wall (Wall): The wall object to place bricks in.
            support_checker (SupportChecker): For checking brick support.
            stride_optimizer (StrideOptimizer, optional): For stride optimization.
        """
        self.wall = wall
        self.support_checker = support_checker
        self.stride_optimizer = stride_optimizer

    def place_brick(self, course, position):
        """
        Place a single brick at the specified position.
        
        Args:
            course (int): The course number (0-based).
            position (int): The position within the course.
            
        Returns:
            bool: True if the brick was placed, False otherwise.
        """

        if course < 0 or course >= self.wall.courses:
            return False
        
        if position < 0 or position >= len(self.wall.grid[course]):
            return False
        
        # Check if the brick is already built
        if self.wall.grid[course][position][1] == 1:
            return False
        
        # Check if the brick is supported
        if course > 0 and not self.support_checker._is_supported(course, position):
            return False
        
        # Calculate movement cost to this brick
        brick_pos = self.wall.brick_positions[course][position]
        old_pos = self.wall.robot_position
        new_pos = (brick_pos['x'] + brick_pos['length']/2, brick_pos['y'] + brick_pos['height']/2)
        
        # Calculate horizontal and vertical movement costs
        horizontal_distance = abs(new_pos[0] - old_pos[0])
        vertical_distance = abs(new_pos[1] - old_pos[1])
        movement_cost = (horizontal_distance * HORIZONTAL_MOVE_COST + 
                         vertical_distance * VERTICAL_MOVE_COST)
        
        self.wall.total_movement_cost += movement_cost
        
        # Mark the brick as built
        brick_length, _, orientation = self.wall.grid[course][position]
        self.wall.grid[course][position] = (brick_length, 1, orientation)
        self.wall.stride_map[(course, position)] = self.wall.current_stride
        self.wall.placed_bricks += 1
        
        # Update robot position to the center of this brick
        self.wall.robot_position = new_pos
        
        # Mark that we've placed at least one brick in this stride
        self.wall.current_stride_active = True
        
        # If this is the first brick placed in a new stride that needs counting,
        # increment the stride count
        if self.wall.stride_needs_counting and self.wall.current_stride_active:
            self.wall.strides_used += 1
            self.wall.stride_needs_counting = False
        
        return True
    
    def place_single_brick_from_stride(self):
        """
        Place a single brick from the current stride.
        
        If there are no bricks in the current stride, a new stride is calculated.
        
        Returns:
            bool: True if a brick was placed, False otherwise.
        """
        if not self.wall.current_stride_bricks:
            # Check if the wall is complete
            if not self.wall.has_unbuilt_bricks():
                self.wall.message = "Wall is complete!"
                return False
            
            # We're about to calculate a new stride, which means the previous one is complete
            # Increment the color index if we've placed at least one brick
            if self.wall.current_stride_active:
                self.wall.current_stride += 1
                self.wall.current_stride_active = False
            
            # Calculate the next stride (and set stride_needs_counting flag)
            if not self.stride_optimizer.calculate_next_stride():
                # If calculate_next_stride fails but there are still unbuilt bricks,
                # try the fallback approach
                if self.wall.has_unbuilt_bricks():
                    self.wall.message = "Trying alternative approach to find placeable bricks..."
                    self.stride_optimizer._find_any_placeable_bricks()
                    if self.wall.current_stride_bricks:
                        self.stride_optimizer._optimize_brick_placement_order()
                    else:
                        self.wall.message = "No more bricks can be placed!"
                        return False
                else:
                    self.wall.message = "Wall is complete!"
                    return False
        
        # Get the next brick to place from the current stride
        if self.wall.current_stride_bricks:
            brick = self.wall.current_stride_bricks.pop(0)
            course = brick['course']
            position = brick['position']
            
            # Place the brick
            return self.place_brick(course, position)
        
        return False
    
    def place_all_bricks_in_stride(self):
        """
        Place all bricks in the current stride at once.
        
        If there are no bricks in the current stride, a new stride is calculated.
        
        Returns:
            bool: True if any bricks were placed, False otherwise.
        """
        if not self.wall.current_stride_bricks:
            # Check if the wall is complete
            if not self.wall.has_unbuilt_bricks():
                self.wall.message = "Wall is complete!"
                return False
            
            # Calculate the next stride
            if not self.stride_optimizer.calculate_next_stride():
                # If calculate_next_stride fails but there are still unbuilt bricks,
                # try the fallback approach
                if self.wall.has_unbuilt_bricks():
                    self.wall.message = "Trying alternative approach to find placeable bricks..."
                    self.stride_optimizer._find_any_placeable_bricks()
                    if self.wall.current_stride_bricks:
                        self.stride_optimizer._optimize_brick_placement_order()
                    else:
                        self.wall.message = "No more bricks can be placed!"
                        return False
                else:
                    self.wall.message = "Wall is complete!"
                    return False
        
        # Place all bricks in the current stride
        placed = False
        
        while self.wall.current_stride_bricks:
            brick = self.wall.current_stride_bricks.pop(0)
            course = brick['course']
            position = brick['position']
            
            if self.place_brick(course, position):
                placed = True
        
        # Mark the stride as complete and prepare for the next one
        if placed:
            # Don't increment display_stride here - we'll do it when we start the next stride
            # We just finished a stride, so prepare for the next one
            self.stride_optimizer._start_new_stride()
            return True
        
        return False
    