"""
Wild bond pattern generator for the masonry wall simulator.

This module provides functions to generate courses with a wild bond pattern,
identify and manage falling teeth patterns, and calculate optimal robot positioning.
"""

import sys
import os
# Add the base directory to the Python path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    FULL_BRICK_LENGTH, HEAD_JOINT, FULL_BRICK_WIDTH, 
    STRIDE_WIDTH, WALL_WIDTH, NUM_COURSES, HALF_BRICK_LENGTH
)

def _initialize_wild_bond_course(course, wall):
    """
    Initialize a course with wild bond pattern following the constraints.
    
    Wild bond uses a mix of headers and stretchers with variation in alignment,
    avoiding long "falling teeth" patterns.
    
    Args:
        course (int): The course number (0-based).
        wall
        
    Returns:
        list: List of tuples (brick_length, is_built, orientation) for the course.
    """
    row = []
    
    # Track consecutive brick types
    consecutive_headers = 0
    consecutive_stretchers = 0
    
    # Brick size constants
    quarter_brick = FULL_BRICK_LENGTH / 4
    
    # Get previous course head joint positions and brick ends (for pattern checking)
    prev_head_joints = []
    prev_brick_ends = []  # Track end positions of all bricks in previous courses
    
    # Store falling teeth patterns we've identified so far
    falling_teeth_patterns = []
    
    # Build a map of brick end positions for previous courses
    if course > 0:
        for prev_course in range(max(0, course-5), course):
            course_brick_ends = []
            x_pos = 0
            for brick_idx, (brick_length, _, _) in enumerate(wall[prev_course]):
                x_pos += brick_length
                # Store the end position and brick details
                course_brick_ends.append({
                    'x': x_pos,
                    'course': prev_course,
                    'index': brick_idx
                })
                if brick_idx < len(wall[prev_course]) - 1:  # Skip last joint
                    x_pos += HEAD_JOINT
            
            # Store this course's brick ends for pattern checking
            prev_brick_ends.append(course_brick_ends)
            
            # For direct previous course, also get head joint positions
            if prev_course == course - 1:
                current_pos = 0
                for brick_length, _, orientation in wall[prev_course]:
                    current_pos += brick_length
                    if orientation == 'header':
                        prev_head_joints.append(current_pos)
                    current_pos += HEAD_JOINT
    
    # Identify existing falling teeth patterns
    # This builds a map of vertical "teeth" patterns we need to avoid extending
    if course > 0:
        falling_teeth_patterns = _identify_falling_teeth_patterns(course, wall)
    
    # Step 1: Handle the left edge - may need a special brick
    left_edge_brick = None
    starting_offset = 0
    
    # Decide if we should offset this course for pattern variation
    # Create variation in the starting position for a more interesting pattern
    if course % 4 == 0:
        # No offset
        starting_offset = 0
    elif course % 4 == 1:
        # Quarter brick offset
        starting_offset = quarter_brick
        left_edge_brick = (quarter_brick, 0, 'stretcher')
    elif course % 4 == 2:
        # Half brick offset
        starting_offset = quarter_brick * 2
        left_edge_brick = (quarter_brick * 2, 0, 'stretcher')
    elif course % 4 == 3:
        # Three-quarter brick offset
        starting_offset = quarter_brick * 3
        left_edge_brick = (quarter_brick * 3, 0, 'stretcher')
    
    # Add the left edge brick if we have one
    if left_edge_brick:
        row.append(left_edge_brick)
    
    # Step 2: Fill the interior with full-sized stretchers and headers
    x_pos = starting_offset
    
    # Decide on starting brick type based on course number for variety
    use_starting_header = (course % 3 == 1)
    
    # Create a plan for the whole course before adding bricks
    # This allows us to check if we need to adjust the right edge
    interior_plan = []
    
    # Calculate a safe width threshold to ensure there's enough space for the final brick
    # We want to leave at least a half brick length for the final brick
    safe_width_threshold = WALL_WIDTH - HALF_BRICK_LENGTH
    
    while x_pos + FULL_BRICK_WIDTH + HEAD_JOINT < safe_width_threshold:
        # Decide whether to place header or stretcher next
        place_header = False
        
        # Force stretcher if we've hit header limit
        if consecutive_headers >= 3:
            place_header = False
        # Force header if we've hit stretcher limit
        elif consecutive_stretchers >= 5:
            place_header = True
        # Start with predetermined type for course variety
        elif len(interior_plan) == 0:
            place_header = use_starting_header
        else:
            # Use deterministic but varied brick selection
            # Based on position and course number for variety
            place_header = ((x_pos + course) % 7 == 0) or ((x_pos + course) % 11 == 0)
            
            # Check head joint alignment with previous course
            if course > 0:
                # Don't place a head joint too close to one in the course below
                for prev_joint in prev_head_joints:
                    # If we'd create a head joint within 1/4 brick of one below, switch type
                    potential_joint_pos = x_pos + (FULL_BRICK_WIDTH if place_header else FULL_BRICK_LENGTH)
                    if abs(potential_joint_pos - prev_joint) < quarter_brick:
                        place_header = not place_header
                        break
        
        # Calculate brick dimensions
        if place_header:
            brick_length = FULL_BRICK_WIDTH
            orientation = 'header'
        else:
            brick_length = FULL_BRICK_LENGTH
            orientation = 'stretcher'
        
        # Check if this brick would extend a falling teeth pattern beyond 5 courses
        # Calculate where this brick would end
        brick_end_pos = x_pos + brick_length
        
        # Check if this brick end would continue an existing falling teeth pattern
        would_extend_pattern = False
        for pattern in falling_teeth_patterns:
            if len(pattern) >= 5:  # Only worry about long patterns
                # Check if this brick would align with the pattern
                if abs(brick_end_pos - pattern[-1]['x']) < quarter_brick:
                    # This would extend an already long pattern
                    would_extend_pattern = True
                    break
        
        # If this brick would extend a long pattern, try the other brick type
        if would_extend_pattern:
            # Switch brick type to break the pattern
            if place_header:
                brick_length = FULL_BRICK_LENGTH
                orientation = 'stretcher'
            else:
                brick_length = FULL_BRICK_WIDTH
                orientation = 'header'
        
        # Update consecutive counters after potential adjustment
        if orientation == 'header':
            consecutive_headers += 1
            consecutive_stretchers = 0
        else:
            consecutive_stretchers += 1
            consecutive_headers = 0
        
        # Only add the brick if it doesn't go beyond our safe threshold
        if x_pos + brick_length + HEAD_JOINT <= safe_width_threshold:
            interior_plan.append((brick_length, orientation))
            x_pos += brick_length + HEAD_JOINT
        else:
            # We've reached the threshold, break out
            break
    
    # Add all planned interior bricks
    for brick_length, orientation in interior_plan:
        row.append((brick_length, 0, orientation))
    
    # Calculate the exact size for the final brick to make the course exactly 2300mm wide
    current_width = sum(brick[0] for brick in row) + (len(row) - 1) * HEAD_JOINT if row else 0
    final_brick_length = WALL_WIDTH - current_width
    
    # Ensure the final brick is a reasonable size (at least quarter brick)
    if final_brick_length >= quarter_brick:
        # Add the final edge brick with the exact calculated length
        row.append((final_brick_length, 0, 'stretcher'))
    else:
        # If the remaining space is too small, adjust the previous brick
        if row:
            last_brick_length, _, last_orientation = row[-1]
            row[-1] = (last_brick_length + final_brick_length, 0, last_orientation)
    
    # Final verification of the course width (use very small tolerance for floating point precision)
    course_width = sum(brick[0] for brick in row) + HEAD_JOINT * (len(row) - 1)
    if abs(course_width - WALL_WIDTH) > 0.001:  # Tighter tolerance for exact width
        # Adjust the last brick size to match exactly 2300mm
        last_brick_length, last_is_built, last_orientation = row[-1]
        adjustment = WALL_WIDTH - course_width
        row[-1] = (last_brick_length + adjustment, last_is_built, last_orientation)
    
    return row
    
    
def _identify_falling_teeth_patterns(course, wall):
    """
    Identify all existing falling teeth patterns up to the current course.
    
    A "falling teeth" pattern occurs when brick edges align vertically across
    multiple courses, creating a visual pattern that should be avoided beyond
    a certain length.
    
    Args:
        course (int): The course number to check up to.
        wall
        
    Returns:
        list: List of patterns, where each pattern is a list of brick end positions.
    """

    if course <= 1:
        return []  # Need at least 2 courses to have a pattern
    
    # Get all brick end positions for previous courses
    course_brick_ends = []
    for c in range(max(0, course-5), course):
        ends = []
        x_pos = 0
        for brick_idx, (brick_length, _, _) in enumerate(wall[c]):
            x_pos += brick_length
            ends.append({
                'x': x_pos,
                'course': c,
                'index': brick_idx
            })
            if brick_idx < len(wall[c]) - 1:  # Skip last joint
                x_pos += HEAD_JOINT
        course_brick_ends.append(ends)
    
    # Identify patterns by tracking aligned ends across courses
    patterns = []
    
    # Start from the most recent course and work backwards
    for i in range(len(course_brick_ends) - 1, 0, -1):
        current_course_ends = course_brick_ends[i]
        prev_course_ends = course_brick_ends[i-1]
        
        # Check each end in the current course
        for end in current_course_ends:
            # Look for an aligned end in the previous course
            found_pattern = False
            
            for prev_end in prev_course_ends:
                # If this end aligns with one in the previous course
                if abs(end['x'] - prev_end['x']) < FULL_BRICK_LENGTH / 4:
                    # Check if this is part of an existing pattern
                    extended = False
                    for pattern in patterns:
                        if pattern[-1]['course'] == prev_end['course'] and abs(pattern[-1]['x'] - prev_end['x']) < 1:
                            # Extend this pattern
                            pattern.append(end)
                            extended = True
                            break
                    
                    if not extended:
                        # Start a new pattern
                        patterns.append([prev_end, end])
                    
                    found_pattern = True
                    break
    
    # Filter to only keep patterns with at least 2 steps
    return [p for p in patterns if len(p) >= 2]

def _would_create_falling_teeth(course, end_pos, wall, existing_patterns):
    """
    Check if a brick ending at end_pos would create or extend a falling teeth pattern.
    
    Args:
        course_number (int): The course number being built.
        end_pos (float): The ending x-position of the brick.
        wall
        existing_patterns (list): List of identified falling teeth patterns.
        
    Returns:
        bool: True if it would extend a pattern beyond the 5 steps limit, False otherwise.
    """
    # If we're in the first few courses, no danger of excessive patterns
    if course < 5:
        return False
    
    # Look for existing patterns that this brick might extend
    for pattern in existing_patterns:
        # Check if the pattern is already at 5 steps
        if len(pattern) >= 5:
            # Check if this brick would align with the pattern
            latest_end = pattern[-1]
            if abs(end_pos - latest_end['x']) < FULL_BRICK_LENGTH / 4:
                # This would extend an already long pattern
                return True
    
    # Also check for patterns not in our tracked list
    # This is a more thorough check for the current position
    count = 1  # Start with this brick
    prev_pos = end_pos
    
    # Check previous courses for alignment
    for c in range(course-1, max(0, course-5), -1):
        found_alignment = False
        
        # Check each brick in this course
        x_pos = 0
        for brick_length, _, _ in wall[c]:
            x_pos += brick_length
            
            # If this end aligns with our position
            if abs(x_pos - prev_pos) < FULL_BRICK_LENGTH / 4:
                count += 1
                prev_pos = x_pos
                found_alignment = True
                break
            
            x_pos += HEAD_JOINT
        
        # If no alignment found, pattern is broken
        if not found_alignment:
            break
    
    # Return True if we would exceed 5 steps
    return count > 5

def _get_optimal_starting_position(wall):
    """
    Determine the optimal starting position for a wild bond wall.
    
    Wild bond has an irregular pattern, so the function focuses on areas with a
    mix of headers and stretchers for the most efficient starting position.
    
    Args:
        wall (Wall): The wall object to optimize for.
        
    Returns:
        tuple: (x, y) coordinates for the optimal starting position.
    """
        
    # For Wild Bond, analyze the pattern complexity
    # Focus on areas with a mix of headers and stretchers
    
    # First, evaluate several potential starting positions
    best_position = (WALL_WIDTH / 2, 0)  # Default to center
    best_score = 0
    
    # Try positions across the bottom of the wall
    stride_width_half = STRIDE_WIDTH / 2
    
    # Test more positions for wild bond due to its irregular nature
    num_test_positions = 9  # More test positions for wild bond
    test_x_positions = [i * WALL_WIDTH / (num_test_positions - 1) for i in range(num_test_positions)]
    
    for pos_x in test_x_positions:
        # Calculate the stride bounds
        stride_x = max(0, pos_x - stride_width_half)
        stride_y = 0
        
        # Ensure stride doesn't exceed wall boundaries
        stride_x = min(stride_x, WALL_WIDTH - STRIDE_WIDTH)
        
        # Count bricks in the first few courses for this position
        total_score = 0
        max_course_to_check = min(4, NUM_COURSES)  # Check first 4 courses
        
        for course in range(max_course_to_check):
            course_bricks = 0
            course_weight = 1.0 / (course + 1)  # Weight earlier courses more heavily
            
            for position in range(len(wall.grid[course])):
                if wall.brick_in_stride(course, position, stride_x, stride_y):
                    # Give more weight to areas with pattern transitions
                    # (where stretchers and headers meet)
                    is_header = wall.grid[course][position][2] == 'header'
                    
                    # Check if there's a pattern transition nearby
                    has_transition = False
                    if position > 0:
                        prev_is_header = wall.grid[course][position-1][2] == 'header'
                        if prev_is_header != is_header:
                            has_transition = True
                    
                    if has_transition:
                        course_bricks += 1.5  # Bonus for transitions
                    else:
                        course_bricks += 1.0
            
            total_score += course_bricks * course_weight
        
        if total_score > best_score:
            best_score = total_score
            best_position = (pos_x, 0)
    
    return best_position
    