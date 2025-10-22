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

def drawAxisymmetricInductor(myind, simParam):
    # Draws the inductor for the axisymmetric simulation in FEMM and saves the
    # result in myind.filename_axi+'.fem'

    if not (os.path.isfile(f"{myind.filename_axi}.fem") and simParam.reuse_file):
        femm.openfemm()
        if simParam.MINIMIZE_FEMM:
            femm.main_minimize()
        femm.newdocument(0)
        femm.mi_showgrid()
        
        ## Setup FEMM
        # Define the problem type.
        femm.mi_probdef(simParam.target_fs, 'millimeters', 'axi', 1.e-8, 0, 30)
        
        # Add some material-properties
        femm.mi_getmaterial('Air')
        femm.mi_getmaterial('Copper')
        if simParam.USE_BHCURVE:
            # Create the core material.
            # First, we create a material in the same way as if we 
            # were creating a linear material, except the values used for 
            # permeability are merely placeholders.
            femm.mi_addmaterial('Core', 2100, 2100, 0, 0, 0, 0, 0, 1, 0, 0, 0)
        
            # Data which was extracted was in mT, so rescale to T
            mybhcurve = myind.material.bhcurve.copy()
            mybhcurve[:, 0] = mybhcurve[:, 0] * 1e-3
        
            # Associate this BH curve with the Core material:
            femm.mi_addbhpoints('Core', mybhcurve)
        else:
            # Add a linear BH-Curve 
            femm.mi_addmaterial('Core', myind.material.mu, myind.material.mu, 0, 0, 0, 0, 0, 1)
        
        # Create a parallel circuit property for each turn. There is only
        # half of a single winding, so one circuit property for each turn.
        # Test current doesn't really matter so just use average phase
        # current
        for i in range(1, myind.turns + 1):
            femm.mi_addcircprop(str(i), simParam.iout_avg / 2, 0)

        ## Draw the core and add block labels
        for i in range(myind.rects_axi.shape[0]):
            femm.mi_drawrectangle(myind.rects_axi[i, 0, 0], myind.rects_axi[i, 0, 1],
                                myind.rects_axi[i, 1, 0], myind.rects_axi[i, 1, 1])
            femm.mi_addblocklabel(myind.centers_axi[0, i], myind.centers_axi[1, i])
            femm.mi_selectlabel(myind.centers_axi[0, i], myind.centers_axi[1, i])
            femm.mi_setblockprop('Core', simParam.CORE_AUTOMESH, simParam.CORE_MESHSIZE, '<None>', 0, 0, 0)
            femm.mi_clearselected()

        ## Add air-properties
        for i in range(myind.air_axi.shape[0]):
            femm.mi_addblocklabel(myind.air_axi[i, 0], myind.air_axi[i, 1])
            femm.mi_selectlabel(myind.air_axi[i, 0], myind.air_axi[i, 1])
            femm.mi_setblockprop('Air', simParam.AIR_AUTOMESH, simParam.AIR_MESHSIZE, '<None>', 0, 0, 0)
            femm.mi_clearselected()

        # Draw the windings
        myind.winding['function'](myind, '', myind.winding['axi_start'], 'r', simParam)
        
        # Make the Dirichlet Boundary at the end because for some reason this
        # speeds up the process a lot. Automatically zooms to natural at the end.
        femm.mi_makeABC(3, np.max(np.abs(myind.rects_axi[:, :, 0])) * 2, 0, 0, 0)
        
        # Save the file
        # Convert to absolute path to avoid working directory issues
        file_path = os.path.abspath(f"{myind.filename_axi}.fem")
        file_dir = os.path.dirname(file_path)
        
        # Ensure directory exists
        if file_dir and not os.path.exists(file_dir):
            os.makedirs(file_dir)
        
        # Remove existing file if it exists (in case it's read-only or locked)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not remove existing file {file_path}: {e}")
        
        femm.mi_saveas(file_path)
    
        femm.closefemm()
