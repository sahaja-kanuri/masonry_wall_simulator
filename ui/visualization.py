"""
Visualization module for the masonry wall simulator.

This module provides the WallVisualizer class for drawing the wall with pygame.
"""

import pygame
import sys
import os
# Add the base directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (
    SCALE, BACKGROUND_COLOR, UNBUILT_BRICK_COLOR, BUILT_BRICK_COLOR,
    CURRENT_STRIDE_COLOR, TEXT_COLOR, JOINT_COLOR, GRID_COLOR,
    STRIDE_COLORS, BOND_NAMES, FULL_BRICK_LENGTH, HALF_BRICK_LENGTH, FULL_BRICK_WIDTH,
    STRETCHER_BOND, ENGLISH_CROSS_BOND, WILD_BOND
)

class WallVisualizer:
    """
    A class for visualizing the masonry wall with pygame.
    
    Attributes:
        wall (Wall): The wall object to visualize.
    """

    def __init__(self, wall):
        """
        Initialize a WallVisualizer.
        
        Args:
            wall (Wall): The wall object to visualize.
        """

        self.wall = wall

    def draw(self, screen, font):
        """
        Draw the complete wall visualization with Pygame graphics.
        
        Args:
            screen (pygame.Surface): The pygame surface to draw on.
            font (pygame.font.Font): The font to use for text.
        """

        # Clear the screen
        screen.fill(BACKGROUND_COLOR)
        
        # Calculate wall height in pixels
        wall_height_px = int(self.wall.height * SCALE)
        
        # Draw a grid
        for x in range(0, int(self.wall.width * SCALE) + 1, 100):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, wall_height_px), 1)
        for y in range(0, wall_height_px + 1, 100):
            pygame.draw.line(screen, GRID_COLOR, (0, wall_height_px - y), (int(self.wall.width * SCALE), wall_height_px - y), 1)
        
        # Draw the wall bricks
        for course in range(self.wall.courses):
            for i, (brick_length, is_built, orientation) in enumerate(self.wall.grid[course]):
                brick = self.wall.brick_positions[course][i]
                
                # Calculate brick rectangle
                x = brick['x'] * SCALE
                y = (self.wall.height - brick['y'] - brick['height']) * SCALE  # Flip Y to draw from bottom up
                width = brick['length'] * SCALE
                height = brick['height'] * SCALE
                rect = pygame.Rect(x, y, width, height)
                
                # Determine brick color
                if is_built:
                    # Get stride color for built bricks
                    stride_num = self.wall.stride_map.get((course, i), 0)
                    color_idx = stride_num % len(STRIDE_COLORS)
                    brick_color = STRIDE_COLORS[color_idx]
                else:
                    # Check if this brick is in the current stride queue
                    in_current_stride = any(b['course'] == course and b['position'] == i for b in self.wall.current_stride_bricks)
                    if in_current_stride:
                        brick_color = CURRENT_STRIDE_COLOR
                    else:
                        brick_color = UNBUILT_BRICK_COLOR
                
                # Draw the brick
                pygame.draw.rect(screen, brick_color, rect)
                pygame.draw.rect(screen, TEXT_COLOR, rect, 1)  # Brick outline
                
                # For header bricks, add a visual indicator (diagonal line)
                if orientation == 'header':
                    start_pos = (int(x), int(y))
                    end_pos = (int(x + width), int(y + height))
                    pygame.draw.line(screen, TEXT_COLOR, start_pos, end_pos, 1)
                    # Add a second diagonal line in the opposite direction for headers
                    pygame.draw.line(screen, TEXT_COLOR, (int(x), int(y + height)), (int(x + width), int(y)), 1)
                
                # For custom-sized bricks (not full or half-sized), add a vertical marker
                standard_sizes = [FULL_BRICK_LENGTH, HALF_BRICK_LENGTH, FULL_BRICK_WIDTH]
                is_custom = abs(brick_length - FULL_BRICK_LENGTH) > 1 and abs(brick_length - HALF_BRICK_LENGTH) > 1 and abs(brick_length - FULL_BRICK_WIDTH) > 1
                if is_custom:
                    mid_x = x + width / 2
                    pygame.draw.line(screen, TEXT_COLOR, (int(mid_x), int(y)), (int(mid_x), int(y + height)), 1)
        
        # Draw robot position
        robot_x = self.wall.robot_position[0] * SCALE
        robot_y = (self.wall.height - self.wall.robot_position[1]) * SCALE
        pygame.draw.circle(screen, (0, 0, 255), (int(robot_x), int(robot_y)), 5)
        
        # Draw stats below the wall
        if self.wall.bond_type == STRETCHER_BOND:
            bond_name = "Stretcher Bond"
        elif self.wall.bond_type == ENGLISH_CROSS_BOND:
            bond_name = "English Cross Bond"
        elif self.wall.bond_type == WILD_BOND:
            bond_name = "Wild Bond"

        # Check if wall is complete
        if self.wall.placed_bricks >= self.wall.total_bricks:
            completion_message = f"Wall completed! Total strides: {self.wall.strides_used}, Movement cost: {self.wall.total_movement_cost:.1f}"
        else:
            completion_message = self.wall.message
        
        stats_text = [
            f"Wall ({self.wall.width}mm x {self.wall.height}mm) - {bond_name}",
            f"Bricks placed: {self.wall.placed_bricks}/{self.wall.total_bricks}, Strides used: {self.wall.strides_used}",
            f"Robot position: ({self.wall.robot_position[0]:.1f}mm, {self.wall.robot_position[1]:.1f}mm), Total movement cost: {self.wall.total_movement_cost:.1f}",
            f"Bricks in current stride: {len(self.wall.current_stride_bricks)}",
            completion_message,
            f"Press 1 for Stretcher Bond, 2 for English Cross Bond, 3 for Wild Bond",
            f"ENTER to place a brick, s for stride, q to quit"
        ]
        
        # Place text below the wall image
        for i, text in enumerate(stats_text):
            text_surface = font.render(text, True, TEXT_COLOR)
            screen.blit(text_surface, (10, wall_height_px + 15 + i * 25))
    