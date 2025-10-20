# This file is part of the Planar Inductor Toolbox
# Copyright (C) 2025 Adrian Keil
# 
# The Planar Inductor Toolbox is free software: you can redistribute it 
# and/or modify it under the terms of the GNU General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
# 
# The Planar Inductor Toolbox is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  
# If not, see https://www.gnu.org/licenses/gpl-3.0.html

import numpy as np

def mirrorRects(rects, dir, value=0):
    # Mirrors each individual rectangle in x or y direction
    # dir specifies the direction
    # value specifies the mirror line:
    # for dir='x' the mirror-line is y=value
    # for dir='y' the mirror-line is x=value

    assert (dir == 'x') or (dir == 'y')
    
    if dir == 'x':
        rects[1, :, :] = 2 * value - rects[1, :, :]
    else:  # dir == 'y'
        rects[0, :, :] = 2 * value - rects[0, :, :]
    
    return rects
