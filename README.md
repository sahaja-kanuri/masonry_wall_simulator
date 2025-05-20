# Masonry Wall Simulator

## Description

A Python simulator for building masonry walls with different bond patterns using a robotic system.

### Features

- Multiple bond patterns (Stretcher, English Cross, Wild)
- Optimized brick placement algorithms
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
<!-- 
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
└── requirements.txt -->

masonry_wall_simulator/
├── constants.py
├── models/
│   ├── init.py
│   └── wall.py
├── patterns/
│   ├── init.py
│   ├── stretcher_bond.py
│   ├── english_cross_bond.py
│   └── wild_bond.py
├── core/
│   ├── init.py
│   ├── brick_placer.py
│   ├── support_checker.py
│   └── stride_optimizer.py
└── ui/
├── init.py
├── visualization.py
main.py
setup.py

## Setup

Python 3.6 or higher is required.

<pre><code>
$ python3 -m venv robotics
$ source robotics/bin/activate
$ pip install -U pip
$ pip install -r requirements.txt

$ python3 main.py
</code></pre>