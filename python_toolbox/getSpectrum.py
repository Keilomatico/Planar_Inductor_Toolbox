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
from scipy import interpolate

def getSpectrum(data, timestamps, N):
    # Computes an fft with N sampling points. Returns complex amplitude and frequency sorted by absolute amplitude

    # "Sample" the signal
    period = timestamps[-1]
    f_sample = N / period            # Sampling frequency
    time_interpol = np.arange(0, timestamps[-1], 1/f_sample)                 # Vector with sampling timestamps
    
    # Interpolate the given data to the sampling points
    f_interp = interpolate.interp1d(timestamps, data, kind='linear')
    data_interpol = f_interp(time_interpol)
    
    # Perform FFT
    fft_result = np.fft.fft(data_interpol)
    amplitude = fft_result[0:N//2+1] / N * 2
    amplitude[0] = amplitude[0] / 2  # DC component should only be divided by N
    
    frequency = f_sample / N * np.arange(0, N//2+1)
    return amplitude, frequency
