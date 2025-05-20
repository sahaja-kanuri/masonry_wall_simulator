"""
Stretcher bond pattern generator for the masonry wall simulator.

This module provides functions to generate courses with a stretcher bond pattern
and calculate optimal robot positioning for this pattern.
"""
import sys
import os
# Add the base directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    FULL_BRICK_LENGTH, HALF_BRICK_LENGTH, HEAD_JOINT, 
    STRIDE_WIDTH, WALL_WIDTH
)

def _initialize_stretcher_course(course):
    """
    Initialize a course with stretcher bond pattern
    
    In stretcher bond:
    - Odd courses start with a half brick
    - Even courses start with a full brick
    
    Args:
        course (int): The course number (0-based).
        
    Returns:
        list: List of tuples (brick_length, is_built, orientation) for the course.
    """
    
    row = []
    
    # For stretcher bond, odd courses start with a half brick
    if course % 2 == 1:
        # Start with half brick
        row.append((HALF_BRICK_LENGTH, 0, 'stretcher'))  # (brick_length, is_built, orientation)
        
        # Add full bricks
        remaining_width = WALL_WIDTH - HALF_BRICK_LENGTH - HEAD_JOINT
        while remaining_width >= FULL_BRICK_LENGTH:
            row.append((FULL_BRICK_LENGTH, 0, 'stretcher'))
            remaining_width -= (FULL_BRICK_LENGTH + HEAD_JOINT)
        
        # Add final half brick if needed
        if remaining_width > 0:
            row.append((min(remaining_width, HALF_BRICK_LENGTH), 0, 'stretcher'))
    else:
        # Start with full bricks
        remaining_width = WALL_WIDTH
        while remaining_width >= FULL_BRICK_LENGTH:
            row.append((FULL_BRICK_LENGTH, 0, 'stretcher'))
            remaining_width -= (FULL_BRICK_LENGTH + HEAD_JOINT)
        
        # Add final half brick if needed
        if remaining_width > 0:
            row.append((min(remaining_width, HALF_BRICK_LENGTH), 0, 'stretcher'))
    
    return row

def _get_optimal_starting_position(wall):
    """
    Determine the optimal starting position for a stretcher bond wall.
    
    The function evaluates several potential starting positions to find the one
    that allows for the most bricks to be laid in the first stride.
    
    Args:
        wall (Wall): The wall object to optimize for.
        
    Returns:
        tuple: (x, y) coordinates for the optimal starting position.
    """
    
    # First, evaluate several potential starting positions
    best_position = (WALL_WIDTH / 2, 0)  # Default to center
    best_brick_count = 0
    
    # Try different starting positions across the bottom of the wall
    stride_width_half = STRIDE_WIDTH / 2
    
    # Try positions at left, center, and right, plus quarter positions
    test_positions = [
        (stride_width_half, 0),  # Left-aligned
        (WALL_WIDTH / 4, 0),     # Quarter from left
        (WALL_WIDTH / 2, 0),     # Center
        (3 * WALL_WIDTH / 4, 0), # Quarter from right
        (WALL_WIDTH - stride_width_half, 0)  # Right-aligned
    ]
    
    for pos_x, pos_y in test_positions:
        # Calculate the stride bounds
        stride_x = max(0, pos_x - stride_width_half)
        stride_y = 0
        
        # Ensure stride doesn't exceed wall boundaries
        stride_x = min(stride_x, WALL_WIDTH - STRIDE_WIDTH)
        
        # Count how many first-course bricks would be in this stride
        bricks_in_stride = 0
        for position in range(len(wall.grid[0])):
            if wall.brick_in_stride(0, position, stride_x, stride_y):
                bricks_in_stride += 1
        
        # If this position allows more bricks in the first stride, use it
        if bricks_in_stride > best_brick_count:
            best_brick_count = bricks_in_stride
            best_position = (pos_x, pos_y)
            
    return best_position
        
      
    