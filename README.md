# Masonry Wall Simulator

## Description

A Python simulator for building masonry walls with different bond patterns using a robotic system.

### Features

- Multiple bond patterns (Stretcher, English Cross, Wild)
- Optimized brick placement algorithms
- Visualization of the building process
- Stride-based optimization for robotic movement

### Controls

ENTER: Place a single brick
s: Place all bricks in the current stride
1: Switch to Stretcher Bond
2: Switch to English Cross Bond
3: Switch to Wild Bond
q or ESC: Quit the simulator

## Project Structure

masonry_simulator/
├── constants.py
├── main.py
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
│   ├── visualization.py
└── requirements.txt

## Setup

Python 3.6 or higher is required.

<pre><code>
$ python3 -m venv robotics
$ source robotics/bin/activate
$ pip install -U pip
$ pip install -r requirements.txt

$ python3 main.py
</code></pre>