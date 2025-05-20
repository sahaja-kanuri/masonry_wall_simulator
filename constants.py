"""
Constants for the masonry wall simulator.

This file contains all the constant values used throughout the application,
including physical dimensions, visualization parameters, and simulation settings.
"""

from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent

# -----------------------------------------------------------------------------
# Brick and wall physical dimensions (mm)
# -----------------------------------------------------------------------------

# Brick dimensions
FULL_BRICK_LENGTH = 210  # mm
FULL_BRICK_WIDTH = 100   # mm
FULL_BRICK_HEIGHT = 50   # mm

HALF_BRICK_LENGTH = 100  # mm
HALF_BRICK_WIDTH = 100   # mm
HALF_BRICK_HEIGHT = 50   # mm

# Joint dimensions
HEAD_JOINT = 10          # mm (vertical joint)
BED_JOINT = 12.5         # mm (horizontal joint)
COURSE_HEIGHT = 62.5     # mm (brick height + bed joint)

# Wall dimensions
WALL_WIDTH = 2300        # mm
WALL_HEIGHT = 2000       # mm

# Robot capabilities
STRIDE_WIDTH = 800       # mm
STRIDE_HEIGHT = 1300     # mm

# -----------------------------------------------------------------------------
# Bond type enumerations
# -----------------------------------------------------------------------------
STRETCHER_BOND = 0
ENGLISH_CROSS_BOND = 1
WILD_BOND = 2

# Mapping of bond types to names for display
BOND_NAMES = {
    STRETCHER_BOND: "Stretcher Bond",
    ENGLISH_CROSS_BOND: "English Cross Bond",
    WILD_BOND: "Wild Bond"
}

# -----------------------------------------------------------------------------
# Movement cost weights
# -----------------------------------------------------------------------------
HORIZONTAL_MOVE_COST = 1.5  # Driving is more costly than lifting
VERTICAL_MOVE_COST = 1.0    # Platform movement

# -----------------------------------------------------------------------------
# Visualization settings
# -----------------------------------------------------------------------------
# Scale factor (mm to pixels)
SCALE = 0.3

# Calculate derived constants

# Calculate number of courses
NUM_COURSES = int(WALL_HEIGHT / COURSE_HEIGHT)

# -----------------------------------------------------------------------------
# Colors for visualization
# -----------------------------------------------------------------------------
BACKGROUND_COLOR = (240, 240, 240)
UNBUILT_BRICK_COLOR = (220, 220, 220)
BUILT_BRICK_COLOR = (180, 100, 100)
CURRENT_STRIDE_COLOR = (200, 200, 100)
TEXT_COLOR = (0, 0, 0)
JOINT_COLOR = (200, 200, 200)
GRID_COLOR = (180, 180, 180)

# Stride colors
STRIDE_COLORS = [
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (100, 100, 255),  # Blue
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
    (100, 255, 255),  # Cyan
    (200, 150, 100),  # Brown
    (150, 200, 100),  # Light green
    (100, 150, 200),  # Light blue
]

# -----------------------------------------------------------------------------
# Simulation parameters
# -----------------------------------------------------------------------------
# Support threshold - percentage of brick that must be supported from below
SUPPORT_THRESHOLD = 0.9  # 90% support required

# # Pattern detection parameters
# PATTERN_ALIGNMENT_THRESHOLD = FULL_BRICK_LENGTH / 4  # Max distance for aligned bricks
# MAX_CONSECUTIVE_HEADERS = 3    # Maximum consecutive header bricks
# MAX_CONSECUTIVE_STRETCHERS = 5  # Maximum consecutive stretcher bricks
# MAX_FALLING_TEETH_LENGTH = 5   # Maximum length of "falling teeth" pattern

# -----------------------------------------------------------------------------
# UI settings
# -----------------------------------------------------------------------------
FPS = 60  # Frames per second for UI updates
STATS_SPACE = 180  # Extra space in pixels below wall visualization for stats