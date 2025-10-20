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

# Calculates the curve of integrating ydata with datapoints at times specified in
# time. The distance between elements does not need to be constant.
def myintegral(time, ydata):
    x = np.linspace(time[0], time[-1], 1001)
    y = np.zeros(len(x))
    # Iterate over the array and integrate the the waveform. 
    j = 1
    init = 0
    for i in range(len(time) - 1):
        while j < len(x) and x[j] <= time[i + 1]:
            y[j] = init + (x[j] - time[i]) * (ydata[i + 1] - ydata[i]) / (time[i + 1] - time[i])
            j += 1
        init = y[j - 1]
    
    return x, y
