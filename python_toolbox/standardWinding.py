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

import femm

def standardWinding(myind, windingName, start, positionToCore, simParam):
    # Draws standard windings
    # windingName: Name of the circuit that shoud be used. A number is
    # automatically added depending on the turn
    # start: Coordinates where the winding starts: [startx; centery]
    # positionToCore: Either 'r' if it is on the right side of the core or
    # 'l' if it is on the left side of the core
    
    # Always draw from left to right
    if positionToCore == 'l':
        startx = start[0] - myind.winding['width']
    else:
        startx = start[0]
    # Start at the bottom of the pcb, then draw upwards
    posy = start[1] - myind.pcb.thickness / 2

    for i in range(1, myind.turns + 1):
        # Put the maximum number of layers in parallel. 
        # No interleaving here.
        parLayers = myind.pcb.layers // myind.turns
        for j in range(1, parLayers + 1):
            # Change the thickness for the outer layers
            if (i - 1) * parLayers + j == 1 or (i - 1) * parLayers + j == myind.pcb.layers:
                thickness = myind.pcb.copper_thickness_outer
            else:
                thickness = myind.pcb.copper_thickness
            
            femm.mi_drawrectangle(startx, posy, startx + myind.winding['width'], posy + thickness)
            femm.mi_addblocklabel(startx + myind.winding['width'] / 2, posy + thickness / 2)
            femm.mi_selectlabel(startx + myind.winding['width'] / 2, posy + thickness / 2)
            femm.mi_setblockprop('Copper', simParam.COPPER_AUTOMESH, simParam.COPPER_MESHSIZE, f'{windingName}{i}', 0, 0, 1)
            femm.mi_clearselected()

            posy = posy + thickness + myind.pcb.insulator_thickness
