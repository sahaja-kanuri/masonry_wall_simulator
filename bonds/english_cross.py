"""
English Cross bond pattern generator for the masonry wall simulator.

This module provides functions to generate courses with an English Cross bond pattern
and calculate optimal robot positioning for this pattern.
"""
import sys
import os
# Add the base directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    FULL_BRICK_LENGTH, HEAD_JOINT, FULL_BRICK_WIDTH, 
    STRIDE_WIDTH, WALL_WIDTH, NUM_COURSES
)
# from models import wall
# from optimizer.support_checker import SupportChecker
# from optimizer.stride_optimizer import StrideOptimizer
# brick_in_stride
# from optimizer.stride_optimizer.StrideOptimizer import brick_in_stride


def _initialize_english_cross_course(course):
    """
    Initialize a course with English Cross Bond pattern with precise edge alignment.
    
    English Cross Bond has a 4-course repeat pattern:
    - Course 0: Full stretchers
    - Course 1: Headers with quarter-brick offset
    - Course 2: Stretchers with half-brick offset
    - Course 3: Headers with three-quarter-brick offset
    
    Args:
        course (int): The course number (0-based).
        
    Returns:
        list: List of tuples (brick_length, is_built, orientation) for the course.
    """

    row = []
    course_type = course % 4
    
    # Precise calculations for each course type
    if course_type == 0:  # First stretcher course
        # Calculate exact number of full stretchers that would fit (including joints)
        available_width = WALL_WIDTH
        num_full_bricks = int(available_width / (FULL_BRICK_LENGTH + HEAD_JOINT))
        
        # Add full stretchers
        x_pos = 0
        for i in range(num_full_bricks):
            row.append((FULL_BRICK_LENGTH, 0, 'stretcher'))
            x_pos += FULL_BRICK_LENGTH + HEAD_JOINT
        
        # Add last brick to perfectly reach wall width
        remaining_width = WALL_WIDTH - x_pos
        if remaining_width > 0:
            row.append((remaining_width, 0, 'stretcher'))
            
    elif course_type == 1:  # First header course - quarter brick offset
        quarter_offset = FULL_BRICK_LENGTH / 4
        row.append((quarter_offset, 0, 'header'))
        
        x_pos = quarter_offset + HEAD_JOINT
        available_width = WALL_WIDTH - x_pos
        
        # Add full header bricks
        num_headers = int(available_width / (FULL_BRICK_WIDTH + HEAD_JOINT))
        for i in range(num_headers):
            row.append((FULL_BRICK_WIDTH, 0, 'header'))
            x_pos += FULL_BRICK_WIDTH + HEAD_JOINT
        
        # Add last header to exactly reach wall width
        remaining_width = WALL_WIDTH - x_pos
        if remaining_width > 0:
            row.append((remaining_width, 0, 'header'))
            
    elif course_type == 2:  # Second stretcher course - half-brick offset
        half_offset = FULL_BRICK_LENGTH / 2
        row.append((half_offset, 0, 'stretcher'))
        
        x_pos = half_offset + HEAD_JOINT
        available_width = WALL_WIDTH - x_pos
        
        # Add full stretchers
        num_full_bricks = int(available_width / (FULL_BRICK_LENGTH + HEAD_JOINT))
        for i in range(num_full_bricks):
            row.append((FULL_BRICK_LENGTH, 0, 'stretcher'))
            x_pos += FULL_BRICK_LENGTH + HEAD_JOINT
        
        # Add last brick to perfectly reach wall width
        remaining_width = WALL_WIDTH - x_pos
        if remaining_width > 0:
            row.append((remaining_width, 0, 'stretcher'))
            
    else:  # course_type == 3, Second header course - quarter brick offset
        three_quarter_offset = FULL_BRICK_LENGTH / 4
        row.append((three_quarter_offset, 0, 'header'))
        
        x_pos = three_quarter_offset + HEAD_JOINT
        available_width = WALL_WIDTH - x_pos
        
        # Add full header bricks
        num_headers = int(available_width / (FULL_BRICK_WIDTH + HEAD_JOINT))
        for i in range(num_headers):
            row.append((FULL_BRICK_WIDTH, 0, 'header'))
            x_pos += FULL_BRICK_WIDTH + HEAD_JOINT
        
        # Add last header to exactly reach wall width
        remaining_width = WALL_WIDTH - x_pos
        if remaining_width > 0:
            row.append((remaining_width, 0, 'header'))
    
    # Verification step: ensure the total course width is exactly equal to wall width
    total_width = sum(brick[0] for brick in row) + (len(row) - 1) * HEAD_JOINT
    if abs(total_width - WALL_WIDTH) > 0.001:  # Allow for tiny floating-point errors
        # Adjust the last brick if needed
        last_brick_size = row[-1][0] + (WALL_WIDTH - total_width)
        row[-1] = (last_brick_size, 0, row[-1][2])
    
    return row


def _get_optimal_starting_position(brick_positions, StrideOptimizer):
    """
    Determine the optimal starting position for an English Cross bond wall.
    
    The function evaluates several potential starting positions to find the one
    that allows for the most efficient building of the wall, accounting for the
    complex header/stretcher pattern.
    
    Args:
        brick_positions (list): List of brick position data.
        
    Returns:
        tuple: (x, y) coordinates for the optimal starting position.
    """
    
    # For English cross bond, we need a more sophisticated approach
    # The pattern is more complex, so we'll evaluate multiple positions
    
    # For English Cross Bond, prioritize starting positions that align well
    # with the header/stretcher pattern
    
    # First, evaluate several potential starting positions
    best_position = (WALL_WIDTH / 2, 0)  # Default to center
    best_score = 0
    
    # Test a wider range of positions for English Cross Bond
    num_test_positions = 7  # Test more positions for complex pattern
    test_x_positions = [i * WALL_WIDTH / (num_test_positions - 1) for i in range(num_test_positions)]
    
    for pos_x in test_x_positions:
        # Calculate the stride bounds
        stride_x = max(0, pos_x - STRIDE_WIDTH / 2)
        stride_y = 0
        
        # Ensure stride doesn't exceed wall boundaries
        stride_x = min(stride_x, WALL_WIDTH - STRIDE_WIDTH)
        
        # Count bricks in the first few courses for this position
        total_score = 0
        max_course_to_check = min(4, NUM_COURSES)  # Check first 4 courses or all if fewer
        
        for course in range(max_course_to_check):
            course_bricks = 0
            course_weight = 1.0 / (course + 1)  # Weight earlier courses more heavily
            
            for position in range(len(brick_positions[course])):
                # stride_optimizer = StrideOptimizer()
                if StrideOptimizer.brick_in_stride(course, position, stride_x, stride_y):
                    # Give more weight to header bricks in English Cross Bond
                    if brick_positions[course][position][2] == 'header':
                        course_bricks += 1.2  # Headers get extra weight
                    else:
                        course_bricks += 1.0
            
            total_score += course_bricks * course_weight
        
        if total_score > best_score:
            best_score = total_score
            best_position = (pos_x, 0)
    
    return best_position
    
    

    
    
