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
import matplotlib.pyplot as plt
from myintegral import myintegral
from mymean import mymean
from myrms import myrms

def calcCapacitance(time, current, res, simParam):
    """Calculates the required capacitance to achieve a certain input and
    output ripple based on the phase-current waveforms"""
    
    del_ = 1e-12
    timestamps = np.array([time[0], time[1], time[1]+del_, time[2], time[2]+del_, time[3], time[3]+del_, time[4]])
    i_in = np.zeros(8)
    
    if simParam.D < 0.5:
        i_in[0:2] = current['i1'][0:2]
        i_in[2:4] = 0
        i_in[4:6] = current['i2'][2:4]
        i_in[6:8] = 0
    else:
        i_in[0:2] = current['i1'][0:2] + current['i2'][0:2]
        i_in[2:4] = current['i1'][1:3]
        i_in[4:6] = current['i1'][2:4] + current['i2'][2:4]
        i_in[6:8] = current['i2'][3:5]
    
    time_interpol1, inChrg = myintegral(timestamps, mymean(timestamps, i_in) - i_in)
    inChrg_ripple = max(inChrg) - min(inChrg)
    # C = Q / V
    res.Cin = inChrg_ripple / simParam.DeltaVinMax
    print(f"Iin,rms = {myrms(timestamps, i_in):.1f}")

    iout = current['i1'] + current['i2']
    time_interpol2, outChrg = myintegral(time, simParam.iout_avg - iout)
    outChrg_ripple = max(outChrg) - min(outChrg)
    res.Cout = outChrg_ripple / simParam.DeltaVoutMax
    print(f"Iout,rms = {myrms(time, iout):.1f}")

    if simParam.SHOWPLOTS:
        plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(timestamps*1e6, i_in, label="I_{in}")
        plt.plot(time*1e6, iout, label="I_{out}")
        plt.grid(True)
        plt.xlabel("Time [us]")
        plt.ylabel("Current [A]")
        plt.legend(loc='upper left')
        
        plt.subplot(2, 1, 2)
        plt.plot(time_interpol1*1e6, (inChrg - np.mean(inChrg))*1e6, label="Q_{in}")
        plt.plot(time_interpol2*1e6, (outChrg - np.mean(outChrg))*1e6, label="Q_{out}")
        plt.grid(True)
        plt.xlabel("Time [us]")
        plt.ylabel("Charge [uC]")
        plt.legend(loc='upper left')
        plt.show()
    
    return res
