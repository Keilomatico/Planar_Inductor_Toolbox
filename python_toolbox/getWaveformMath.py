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

def getWaveformMath(sp, fs, res):
    """Determines the converter waveforms by solving the differential equations"""
    data = {}
    data['imag'] = np.zeros(5)
    data['iout'] = np.zeros(5)
    data['i1'] = np.zeros(5)
    data['i2'] = np.zeros(5)
    
    Ts = 1/fs
    if sp.D < 0.5:
        timestamps = np.array([0, sp.D*Ts, Ts/2, Ts/2+sp.D*Ts, Ts])
        deltaI_mag = sp.Vin*Ts*sp.D/(2*res.L_m)
        deltaI_out = sp.Vin*Ts/res.L_out*sp.D*(0.5-sp.D)
        # Magnetizing current
        data['imag'][0] = -deltaI_mag/2
        data['imag'][1] = data['imag'][0] + sp.D*Ts/res.L_m*sp.Vin/2
        data['imag'][2] = data['imag'][1]
        data['imag'][3] = data['imag'][2] - sp.D*Ts/res.L_m*sp.Vin/2
        data['imag'][4] = data['imag'][3]
        # Output current
        data['iout'][0] = sp.iout_avg - deltaI_out/2
        data['iout'][1] = data['iout'][0] + sp.D*Ts*1/res.L_out*(sp.Vin/2-sp.Vout)
        data['iout'][2] = data['iout'][1] + (0.5-sp.D)*Ts*(-sp.Vout)/res.L_out
        data['iout'][3] = data['iout'][2] + sp.D*Ts*1/res.L_out*(sp.Vin/2-sp.Vout)
        data['iout'][4] = data['iout'][3] + (0.5-sp.D)*Ts*(-sp.Vout)/res.L_out
    else:
        timestamps = np.array([0, (sp.D-0.5)*Ts, Ts/2, sp.D*Ts, Ts])
        deltaI_mag = sp.Vin*Ts/(2*res.L_m)*(1-sp.D)
        deltaI_out = sp.Vin*Ts/res.L_out*(sp.D-0.5)*(1-sp.D)
        # Magnetizing current
        data['imag'][0] = -deltaI_mag/2
        data['imag'][1] = data['imag'][0]
        data['imag'][2] = data['imag'][1] + (1-sp.D)*Ts/res.L_m*sp.Vin/2
        data['imag'][3] = data['imag'][2]
        data['imag'][4] = data['imag'][3] - (1-sp.D)*Ts/res.L_m*sp.Vin/2
        # Output current
        data['iout'][0] = sp.iout_avg - deltaI_out/2
        data['iout'][1] = data['iout'][0] + (sp.D-0.5)*Ts*1/res.L_out*(sp.Vin-sp.Vout)
        data['iout'][2] = data['iout'][1] + (1-sp.D)*Ts*(sp.Vin/2-sp.Vout)/res.L_out
        data['iout'][3] = data['iout'][2] + (sp.D-0.5)*Ts*1/res.L_out*(sp.Vin-sp.Vout)
        data['iout'][4] = data['iout'][3] + (1-sp.D)*Ts*(sp.Vin/2-sp.Vout)/res.L_out
    
    data['i1'] = (data['iout'] + data['imag']) / 2
    data['i2'] = (data['iout'] - data['imag']) / 2
    
    return data, timestamps
