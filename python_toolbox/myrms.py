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

# Calculates the rms value of ydata with datapoints at times specified in
# time. The distance between elements does not need to be constant as
# opposed to the built_in rms function
def myrms(time, ydata):
    sum_val = 0
    # Iterate over the array and integrate the square of the waveform. 
    # See report for a detailed explanation.
    for i in range(len(time) - 1):
        dt = time[i + 1] - time[i]
        if ydata[i + 1] == ydata[i]:
            # Constant value over the interval
            sum_val += dt * ydata[i]**2
        else:
            # Value changes linearly over the interval
            sum_val += dt * (ydata[i]**2 + ydata[i] * ydata[i + 1] + ydata[i + 1]**2) / 3

    # Compute the duration of the interval
    T = time[-1] - time[0]
    result = np.sqrt(sum_val / T)
    return result
