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

import os
import femm
import numpy as np

def getInductancePlanar(myind, res, msg, simParam):
    # Determines the inductance for myind using a planar FEMM simulation
        
    femm.openfemm()
    if simParam.MINIMIZE_FEMM:
        femm.main_minimize()
    femm.opendocument(f"{myind.filename_planar}.fem")

    if not (os.path.isfile(f"{myind.filename_planar}.ans") and simParam.reuse_file):
        femm.mi_analyze()
    femm.mi_loadsolution()

    # Analze results
    valsAl = np.zeros((myind.turns, 3), dtype=complex)
    valsAr = np.zeros((myind.turns, 3), dtype=complex)
    for i in range(1, myind.turns + 1):
        valsAl[i-1, :] = femm.mo_getcircuitproperties(f'Al{i}')
        valsAr[i-1, :] = femm.mo_getcircuitproperties(f'Ar{i}')
        
    if not (myind.coupled == 0):
        valsBl = np.zeros((myind.turns, 3), dtype=complex)
        valsBr = np.zeros((myind.turns, 3), dtype=complex)
        for i in range(1, myind.turns + 1):
            valsBl[i-1, :] = femm.mo_getcircuitproperties(f'Bl{i}')
            valsBr[i-1, :] = femm.mo_getcircuitproperties(f'Br{i}')
    
    # Get the self inductance by dividing flux linkage by current. 
    # All series turns have the same current, so no need to add them up.
    # Due to rounding errors the value sometimes has a very small imaginary
    # component that needs to be removed
    res.L_self = (np.sum(np.real(valsAl[:, 2])) - np.sum(np.real(valsAr[:, 2]))) / valsAl[0, 0]
    if not (myind.coupled == 0):
        res.L_coupled = (np.sum(np.real(valsBl[:, 2])) - np.sum(np.real(valsBr[:, 2]))) / valsAl[0, 0]
        # Not sure why this was put here 
        # if sign(winding(1)) ~= sign(winding(2))
        #    res.L_coupled = -res.L_coupled
        # end
    else:
        res.L_coupled = 0
    
    res.k = res.L_coupled / res.L_self
    res.calcTrafoModel()
    
    msg.print_msg(2, f'Simulated inductance planar: Lself={res.L_self*1e9:.1f} nH, k={res.k:.2f}\n', simParam)
    msg.print_msg(5, f'L_mutual={res.L_coupled*1e9:.1f} nH; L_out={res.L_out*1e9:.1f} nH; L_m={res.L_m*1e9:.1f} nH\n', simParam)
    
    femm.closefemm()
    return res
