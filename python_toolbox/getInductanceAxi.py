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

def getInductanceAxi(myind, res, msg, simParam):
    # Determines the inductance for myind using an axisymmetric FEMM simulation
        
    femm.openfemm()
    if simParam.MINIMIZE_FEMM:
        femm.main_minimize()
    femm.opendocument(f"{myind.filename_axi}.fem")

    if not (os.path.isfile(f"{myind.filename_axi}.ans") and simParam.reuse_file):
        femm.mi_analyze()
    femm.mi_loadsolution()

    # Analze results
    vals = np.zeros((myind.turns, 3), dtype=complex)
    for i in range(1, myind.turns + 1):
        vals[i-1, :] = femm.mo_getcircuitproperties(str(i))

    # Analze results
    # Get the self inductance by dividing flux linkage by current
    # Due to rounding errors the value sometimes has a very small imaginary
    # component that needs to be removed
    res.L_self = np.real(np.sum(vals[:, 2]) / vals[0, 0])
    res.calcTrafoModel()
    msg.print_msg(2, f'Simulated inductance axi: Lself={res.L_self*1e9:.1f} nH\n', simParam)
    
    femm.closefemm()
    return res
