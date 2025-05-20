# Masonry Wall Simulator

## Description

A Python simulator (using pygame) for building masonry walls with different bond patterns using a robotic system made out of a crane on top of a ground vehicle.

Wall dimensions and specifications of the robotic crane that places the bricks can be specified in the `constants.py` file.

The brick-laying algorithm is designed to optimize the number of bricks placed by the crane, before the robot has to be moved (which is relatively slow compared to crane movement).

### Features

- Multiple brick bond patterns (Stretcher, English Cross, Wild)
- Optimized brick placement algorithm
- Visualization of the building process 
- Stride-based optimization for robotic movement

### Controls

ENTER: Place a single brick <br />
s: Place all bricks in the current stride <br />
1: Switch to Stretcher Bond <br />
2: Switch to English Cross Bond <br />
3: Switch to Wild Bond <br />
q or ESC: Quit the simulator

## Project Structure

```
masonry_wall_simulator/
├── constants.py
├── models/
│   ├── __init__.py
│   └── wall.py
├── bonds/
│   ├── __init__.py
│   ├── stretcher.py
│   ├── english_cross.py
│   └── wild.py
├── optimizer/
│   ├── __init__.py
│   ├── brick_placer.py
│   ├── support_checker.py
│   └── stride_optimizer.py
├── ui/
│   ├── __init__.py
│   └── visualization.py
└── main.py
```

### Definitions

Wild Bond adheres to the following rules:
- No two head joints directly on top of each other
- Not more than 5 consecutive "staggered steps" or "falling teeth" patterns, where the ends of bricks form a jagged, step-like appearance
- There may be a maximum of 3 headers next to each other
- There may be a maximum of 5 stretchers next to each other

A brick is slightly more than two times longer than it is deep. Say, you have a brick placed with its stretcher (length) facing out. To perfectly fit 2 bricks above it with their headers (width) facing out, the total length adds to 2 times the width/depth plus the head joint. Therefore, the stretcher length has to be (2*Width + Head Joint).

## Setup

Python 3.6 or higher is required.

Bash script that installs all necessary dependencies and runs the main script:

<pre><code>
$ bash run.sh
</code></pre>

OR

Run these commands in the terminal:

<pre><code>
$ python3 -m venv robotics
$ source robotics/bin/activate
$ pip install -U pip
$ pip install -r requirements.txt

$ python3 main.py
</code></pre>