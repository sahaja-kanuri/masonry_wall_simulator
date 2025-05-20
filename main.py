"""
Main module for the masonry wall simulator.

This module initializes pygame, creates the necessary objects,
and runs the main game loop for the simulation.
"""

import pygame
import sys

from constants import (
    WALL_WIDTH, WALL_HEIGHT, SCALE, 
    STRETCHER_BOND, ENGLISH_CROSS_BOND, WILD_BOND,
    STATS_SPACE, FPS, BOND_NAMES
)
from models.wall import Wall
from bonds.stretcher import _initialize_stretcher_course
from bonds.english_cross import _initialize_english_cross_course
from bonds.wild import _initialize_wild_bond_course
from optimizer.support_checker import SupportChecker
from optimizer.stride_optimizer import StrideOptimizer
from optimizer.brick_placer import BrickPlacer
from ui.visualization import WallVisualizer
# from .ui.event_handler import EventHandler

def main():
    """
    Main function to initialize and run the masonry wall simulator.
    """

    # Initialize pygame
    pygame.init()
    
    # Calculate wall dimensions in pixels
    wall_width_px = int(WALL_WIDTH * SCALE)
    wall_height_px = int(WALL_HEIGHT * SCALE)
    
    # Calculate window size with space below for text
    window_width = wall_width_px + 20  # Just enough for the wall plus a small margin
    window_height = wall_height_px + 180  # Extra space below for stats (increased for more text)
    
    # Create the window
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Masonry Wall Simulation")
    
    # Initialize font
    font = pygame.font.SysFont(None, 24)
    
    # Start with stretcher bond
    bond_type = STRETCHER_BOND
    
    # Create the wall
    wall = Wall(WALL_WIDTH, WALL_HEIGHT, bond_type)

    support_checker = SupportChecker(wall)
    stride_optimizer = StrideOptimizer(wall, support_checker)
    brick_placer = BrickPlacer(wall, support_checker, stride_optimizer)
    visualizer = WallVisualizer(wall)
    
    # Calculate the first stride before displaying
    stride_optimizer.calculate_next_stride()
    
    # Add reset function for bond switching
    def reset_wall(new_bond_type):
        # nonlocal wall, bond_type 
        nonlocal wall, bond_type, support_checker, stride_optimizer, brick_placer, visualizer  
        bond_type = new_bond_type
        wall = Wall(WALL_WIDTH, WALL_HEIGHT, bond_type)
        support_checker = SupportChecker(wall)
        stride_optimizer = StrideOptimizer(wall, support_checker)
        brick_placer = BrickPlacer(wall, support_checker, stride_optimizer)
        visualizer = WallVisualizer(wall)
        
        # Display the starting position in the message
        start_pos = wall.robot_position
        wall.message = f"Ready with {BOND_NAMES.get(bond_type, 'Unknown Bond')}"
        wall.message += f" - Starting at position: ({start_pos[0]:.1f}mm, {start_pos[1]:.1f}mm)"
        
        # Calculate the first stride
        stride_optimizer.calculate_next_stride()
    
    # Main game loop
    running = True
    clock = pygame.time.Clock()
    
    # bond_names = {
    #     STRETCHER_BOND: "Stretcher Bond",
    #     ENGLISH_CROSS_BOND: "English Cross Bond",
    #     WILD_BOND: "Wild Bond"
    # }

    # Display initial starting position
    start_pos = wall.robot_position
    # wall.message = f"Ready with {'Stretcher Bond' if bond_type == STRETCHER_BOND else 'English Cross Bond'}"
    wall.message = f"Ready with {BOND_NAMES.get(bond_type, 'Unknown Bond')}"
    wall.message += f" - Starting at position: ({start_pos[0]:.1f}mm, {start_pos[1]:.1f}mm)"
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_RETURN:
                    # Place a single brick
                    brick_placer.place_single_brick_from_stride()
                elif event.key == pygame.K_s:
                    # Place all bricks in the stride
                    brick_placer.place_all_bricks_in_stride()
                    
                    # Calculate the next stride - don't call this here for 's' 
                    # as it's already handled in place_all_bricks_in_stride
                    
                elif event.key == pygame.K_1:
                    # Switch to Stretcher Bond
                    reset_wall(STRETCHER_BOND)
                elif event.key == pygame.K_2:
                    # Switch to English Cross Bond
                    reset_wall(ENGLISH_CROSS_BOND)
                elif event.key == pygame.K_3:
                    # Switch to English Cross Bond
                    reset_wall(WILD_BOND)
        
        # Draw everything
        visualizer.draw(screen, font)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
        
        # Check if wall is complete
        if wall.is_complete():
            wall.message = f"Wall completed! Total strides: {wall.strides_used}, Movement cost: {wall.total_movement_cost:.1f}"
    
    # Quit pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()