"""
Stride optimizer for the masonry wall simulator.

This module provides the StrideOptimizer class which handles the logic
for optimizing the placement of bricks in strides.
"""

import sys
import os
# Add the base directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    HORIZONTAL_MOVE_COST, VERTICAL_MOVE_COST,
    STRIDE_WIDTH, STRIDE_HEIGHT
)

class StrideOptimizer():
    """
    A class for optimizing stride placement in the wall.
    
    A stride is a group of bricks that can be placed without moving the robot
    horizontally or vertically beyond its reach.
    
    Attributes:
        wall (Wall): The wall object containing brick grid and positions.
        support_checker (SupportChecker): For checking brick support.
    """
    
    def __init__(self, wall, support_checker):
        """
        Initialize a StrideOptimizer.
        
        Args:
            wall (Wall): The wall object to optimize strides for.
            support_checker (SupportChecker): For checking brick support.
        """
        self.wall = wall
        self.support_checker = support_checker

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

        brick = self.wall.brick_positions[course][position]
        
        # Check if the brick is within the stride bounds
        return (brick['x'] >= stride_x and 
                brick['x'] + brick['length'] <= stride_x + STRIDE_WIDTH and
                brick['y'] >= stride_y and 
                brick['y'] + brick['height'] <= stride_y + STRIDE_HEIGHT)
    
    def _start_new_stride(self):
        """
        Handle the transition to a new stride.
        
        This method is called after completing a stride to prepare for the next one.
        """
        # Only increment the current stride color index
        self.wall.current_stride += 1
        
        # Reset stride flags for next stride
        self.wall.current_stride_active = False
        self.wall.new_stride_started = False
        
        # Calculate the next stride automatically after completing this one
        self.calculate_next_stride()
    
    def calculate_next_stride(self):
        """
        Calculate the optimal next stride using maximum brick placement strategy.
        
        Returns:
            bool: True if bricks were found for the next stride, False otherwise.
        """

        # First, check if there are any unbuilt bricks left
        if self.wall.placed_bricks >= self.wall.total_bricks:
            return False
        
        # Clear current stride bricks before calculating a new stride
        self.wall.current_stride_bricks = []
        
        # Set flag that we've started a new stride
        self.wall.new_stride_started = True
        
        # Set flag that this stride needs to be counted
        self.wall.stride_needs_counting = True
        
        # If this is the first stride, use the optimal starting position
        if self.wall.placed_bricks == 0:
            # Use the robot's current position (which is already optimized for bond type)
            stride_x = max(0, min(self.wall.robot_position[0] - STRIDE_WIDTH/2, self.wall.width - STRIDE_WIDTH))
            stride_y = 0
            self._find_maximum_bricks_for_stride(stride_x, stride_y)
        else:
            # Find the optimal stride position based on maximum brick placement
            self._find_optimal_stride_position_maximized()
        
        # If we still don't have any bricks, use a more aggressive approach
        # to find any placeable bricks
        if not self.wall.current_stride_bricks:
            self._find_any_placeable_bricks()
        
        # If we found bricks to place in this stride, sort them for optimal movement
        if self.wall.current_stride_bricks:
            self._optimize_brick_placement_order()
            return True
        
        return False
    
    def _find_maximum_bricks_for_stride(self, stride_x, stride_y):
        """
        Find maximum number of bricks that can be placed in a stride at the given position.
        
        Updates wall.current_stride_bricks with the found bricks.
        
        Args:
            stride_x (float): The x-coordinate of the stride's bottom-left corner.
            stride_y (float): The y-coordinate of the stride's bottom-left corner.
        """

        self.wall.current_stride_bricks = self._get_all_placeable_bricks_in_stride(stride_x, stride_y)
    
    
    def _find_optimal_stride_position_maximized(self):
        """
        Find the stride position that maximizes the number of bricks that can be placed.
        
        This method tries different positions for the stride and selects the one
        that allows the most bricks to be placed.
        
        Updates wall.current_stride_bricks with the found bricks.
        """

        best_count = 0
        best_score = float('-inf')
        best_stride_pos = None
        best_bricks = []
        
        # Create a more detailed grid of potential stride positions
        # Use smaller steps for more precision in finding the optimal position
        step_size = min(STRIDE_WIDTH, STRIDE_HEIGHT) / 8
        
        # Try different positions for the stride with finer granularity
        for x in range(0, int(self.wall.width - STRIDE_WIDTH) + 1, max(1, int(step_size))):
            for y in range(0, int(self.wall.height - STRIDE_HEIGHT) + 1, max(1, int(step_size))):
                # Find all placeable bricks in this stride position
                placeable_bricks = self._get_all_placeable_bricks_in_stride(x, y)
                
                if placeable_bricks:
                    # Calculate score based primarily on number of bricks
                    # with a smaller factor for proximity
                    num_bricks = len(placeable_bricks)
                    
                    # Get proximity factor (closest brick to current position)
                    closest_distance = float('inf')
                    for brick in placeable_bricks:
                        brick_center_x = brick['x'] + brick['length'] / 2
                        brick_center_y = brick['y'] + brick['height'] / 2
                        
                        h_dist = abs(brick_center_x - self.wall.robot_position[0])
                        v_dist = abs(brick_center_y - self.wall.robot_position[1])
                        distance = h_dist * HORIZONTAL_MOVE_COST + v_dist * VERTICAL_MOVE_COST
                        
                        closest_distance = min(closest_distance, distance)
                    
                    # Weight heavily in favor of maximizing bricks
                    proximity_factor = 5000 / (closest_distance + 1)  # Avoid division by zero
                    
                    # The primary score factor is the number of bricks
                    # with proximity as a secondary factor
                    score = (num_bricks * 1000) + proximity_factor
                    
                    # Bonus for completing courses or large regions
                    course_coverage = {}
                    for brick in placeable_bricks:
                        course = brick['course']
                        if course not in course_coverage:
                            course_coverage[course] = 0
                        course_coverage[course] += 1
                    
                    # Bonus for courses that are substantially completed in this stride
                    for course, count in course_coverage.items():
                        total_in_course = len(self.wall.grid[course])
                        built_in_course = sum(1 for _, is_built, _ in self.wall.grid[course] if is_built)
                        remaining = total_in_course - built_in_course
                        
                        # If this stride completes more than 90% of a course, add bonus
                        if count >= remaining * 0.9:
                            score += 500
                    
                    # Update best position if this one is better
                    if num_bricks > best_count or (num_bricks == best_count and score > best_score):
                        best_count = num_bricks
                        best_score = score
                        best_stride_pos = (x, y)
                        best_bricks = placeable_bricks
        
        # Set the stride position and bricks
        if best_stride_pos:
            self.wall.current_stride_bricks = best_bricks
    
    def _get_all_placeable_bricks_in_stride(self, stride_x, stride_y):
        """
        Get all bricks that can be placed in a stride, maximizing the count.
        
        Args:
            stride_x (float): The x-coordinate of the stride's bottom-left corner.
            stride_y (float): The y-coordinate of the stride's bottom-left corner.
            
        Returns:
            list: List of dictionaries containing brick information.
        """

        # First, get all unbuilt bricks in this stride
        unbuilt_bricks = []
        for course in range(self.wall.courses):
            for position in range(len(self.wall.grid[course])):
                # Skip already built bricks
                if self.wall.grid[course][position][1] == 1:
                    continue
                
                # Check if brick is in stride
                if self.brick_in_stride(course, position, stride_x, stride_y):
                    brick = self.wall.brick_positions[course][position]
                    unbuilt_bricks.append({
                        'course': course,
                        'position': position,
                        'x': brick['x'],
                        'y': brick['y'],
                        'length': brick['length'],
                        'height': brick['height'],
                        'orientation': brick['orientation']
                    })
        
        # Now determine which bricks can actually be placed due to support constraints
        placeable_bricks = []
        added_bricks = set()
        
        # First pass: add all bricks from the first course
        for brick in unbuilt_bricks:
            if brick['course'] == 0:
                placeable_bricks.append(brick)
                added_bricks.add((brick['course'], brick['position']))
        
        # Multiple passes to catch all placeable bricks
        # Repeat until no more bricks can be added
        max_passes = 5  # Increase the number of passes to ensure thorough checking
        for _ in range(max_passes):
            bricks_added_this_round = 0
            
            # Sort remaining bricks by course to ensure bottom-up building
            remaining_unbuilt = [b for b in unbuilt_bricks if (b['course'], b['position']) not in added_bricks]
            remaining_unbuilt.sort(key=lambda b: b['course'])
            
            # Check each unbuilt brick
            for brick in remaining_unbuilt:
                course = brick['course']
                position = brick['position']
                
                # Skip if already added
                if (course, position) in added_bricks:
                    continue
                
                # Check if it can be placed now
                can_place = False
                
                # First course bricks can always be placed
                if course == 0:
                    can_place = True
                else:
                    # Check if already supported by built bricks
                    if self.support_checker._is_supported(course, position):
                        can_place = True
                    # Check if would be supported by bricks we've already selected for this stride
                    elif self.support_checker._would_be_supported(course, position, added_bricks):
                        can_place = True
                
                if can_place:
                    placeable_bricks.append(brick)
                    added_bricks.add((course, position))
                    bricks_added_this_round += 1
            
            # If no bricks were added this round, we're done
            if bricks_added_this_round == 0:
                break
        
        return placeable_bricks
    
    def _find_any_placeable_bricks(self):
        """
        Find any bricks that can be placed, using a more robust approach.
        
        This is a fallback method for when the optimal stride position doesn't yield any bricks.
        
        Updates wall.current_stride_bricks with the found bricks.
        """

        # Try to find any unbuilt bricks that can be placed
        for course in range(self.wall.courses):
            for position in range(len(self.wall.grid[course])):
                # Skip already built bricks
                if self.wall.grid[course][position][1] == 1:
                    continue
                
                # Check if the brick is supported and can be placed
                if course == 0 or self.support_checker._is_supported(course, position):
                    brick = self.wall.brick_positions[course][position]
                    self.wall.current_stride_bricks.append({
                        'course': course,
                        'position': position,
                        'x': brick['x'],
                        'y': brick['y'],
                        'length': brick['length'],
                        'height': brick['height'],
                        'orientation': brick['orientation']
                    })
        
        # If we found any bricks, prioritize them by course (bottom to top) 
        # and then by distance
        if self.wall.current_stride_bricks:
            # First sort by course to ensure bottom-up building
            self.wall.current_stride_bricks.sort(key=lambda b: b['course'])
            
            # Then optimize movement within each course
            self._optimize_movement_within_courses()
    
    def _optimize_movement_within_courses(self):
        """
        Optimize brick placement order within each course to minimize movement.
        
        Updates wall.current_stride_bricks with the optimized order.
        """

        if not self.wall.current_stride_bricks:
            return
            
        # Group bricks by course
        bricks_by_course = {}
        for brick in self.wall.current_stride_bricks:
            course = brick['course']
            if course not in bricks_by_course:
                bricks_by_course[course] = []
            bricks_by_course[course].append(brick)
            
        # Start building the optimized order
        optimized_order = []
        current_pos = self.wall.robot_position
        
        # Process each course
        for course in sorted(bricks_by_course.keys()):
            course_bricks = bricks_by_course[course].copy()
            
            # Optimize movement within this course
            while course_bricks:
                # Find closest brick in current course
                closest_idx = 0
                closest_distance = float('inf')
                
                for i, brick in enumerate(course_bricks):
                    brick_center_x = brick['x'] + brick['length'] / 2
                    brick_center_y = brick['y'] + brick['height'] / 2
                    
                    h_dist = abs(brick_center_x - current_pos[0])
                    v_dist = abs(brick_center_y - current_pos[1])
                    distance = h_dist * HORIZONTAL_MOVE_COST + v_dist * VERTICAL_MOVE_COST
                    
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_idx = i
                
                # Add closest brick to optimized order
                brick = course_bricks.pop(closest_idx)
                optimized_order.append(brick)
                
                # Update current position
                current_pos = (brick['x'] + brick['length'] / 2, brick['y'] + brick['height'] / 2)
        
        # Update the stride bricks with the optimized order
        self.wall.current_stride_bricks = optimized_order
    
    def _optimize_brick_placement_order(self):
        """
        Optimize the order of brick placement to minimize robot movement while respecting support constraints.
        
        Updates wall.current_stride_bricks with the optimized order.
        """

        if not self.wall.current_stride_bricks:
            return
        
        # Start from the current robot position
        current_pos = self.wall.robot_position
        optimized_order = []
        remaining_bricks = self.wall.current_stride_bricks.copy()
        
        # First, identify and sort bricks by course (bottom to top)
        bricks_by_course = {}
        for brick in remaining_bricks:
            course = brick['course']
            if course not in bricks_by_course:
                bricks_by_course[course] = []
            bricks_by_course[course].append(brick)
        
        # Keep track of which bricks have been added to the optimized order
        added_coords = set()
        
        # Process each course from bottom to top to ensure proper support
        for course in sorted(bricks_by_course.keys()):
            course_bricks = bricks_by_course[course]
            
            # Continue until all bricks in this course are placed or no more can be placed
            while course_bricks:
                # Find the closest brick that can be placed now
                closest_idx = -1
                closest_distance = float('inf')
                
                for i, brick in enumerate(course_bricks):
                    position = brick['position']
                    
                    # Check if this brick can be placed (is supported)
                    can_place = (course == 0)  # First course is always supported
                    
                    if not can_place:
                        # Check if supported by already built bricks
                        if self.support_checker._is_supported(course, position):
                            can_place = True
                        # Check if would be supported by bricks we've already added to optimized_order
                        elif self.support_checker._would_be_supported(course, position, added_coords):
                            can_place = True
                    
                    if can_place:
                        # Calculate distance to current position
                        brick_center_x = brick['x'] + brick['length'] / 2
                        brick_center_y = brick['y'] + brick['height'] / 2
                        
                        h_dist = abs(brick_center_x - current_pos[0])
                        v_dist = abs(brick_center_y - current_pos[1])
                        distance = h_dist * HORIZONTAL_MOVE_COST + v_dist * VERTICAL_MOVE_COST
                        
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_idx = i
                
                # If we found a brick to place, add it to the optimized order
                if closest_idx != -1:
                    brick = course_bricks.pop(closest_idx)
                    optimized_order.append(brick)
                    added_coords.add((brick['course'], brick['position']))
                    current_pos = (brick['x'] + brick['length'] / 2, brick['y'] + brick['height'] / 2)
                else:
                    # If no brick can be placed now, move to the next course
                    break
        
        # Second pass: Check if there are any remaining bricks that couldn't be placed yet
        remaining_bricks = []
        for course in bricks_by_course.values():
            remaining_bricks.extend(course)
        
        # Multiple iterations to ensure we catch any bricks that become supported
        # after placing others
        max_iterations = 3  # Limit iterations to avoid infinite loops
        iteration = 0
        
        while remaining_bricks and iteration < max_iterations:
            iteration += 1
            bricks_added = 0
            
            # Sort remaining bricks by course for bottom-up approach
            remaining_bricks.sort(key=lambda b: b['course'])
            
            # Try to place any remaining bricks that are now supported
            i = 0
            while i < len(remaining_bricks):
                brick = remaining_bricks[i]
                course = brick['course']
                position = brick['position']
                
                # Check if this brick can be placed now
                can_place = (course == 0)  # First course is always supported
                
                if not can_place:
                    # Check if supported by already built bricks
                    if self.support_checker._is_supported(course, position):
                        can_place = True
                    # Check if would be supported by bricks we've already added to optimized_order
                    elif self.support_checker._would_be_supported(course, position, added_coords):
                        can_place = True
                
                if can_place:
                    # Add the brick to the optimized order
                    optimized_order.append(brick)
                    added_coords.add((course, position))
                    current_pos = (brick['x'] + brick['length'] / 2, brick['y'] + brick['height'] / 2)
                    remaining_bricks.pop(i)
                    bricks_added += 1
                else:
                    i += 1
            
            # If no bricks were added in this iteration, break out
            if bricks_added == 0:
                break
        
        # Update the stride bricks with the optimized order
        self.wall.current_stride_bricks = optimized_order
    