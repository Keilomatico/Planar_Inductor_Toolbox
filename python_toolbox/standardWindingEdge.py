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

def standardWindingEdge(myind, windingName, start, positionToCore, simParam):
    # Draws standard windings with edge-plating. 
    # Edge-plating is only possibe for single-turn inductors
    # windingName: Name of the circuit that shoud be used. A number is
    # automatically added depending on the turn
    # start: Coordinates where the winding starts: [startx; centery]
    # positionToCore: Either 'r' if it is on the right side of the core or
    # 'l' if it is on the left side of the core
    assert myind.turns == 1
    
    # Always draw from left to right
    if positionToCore == 'l':
        startx = start[0] - myind.pcb.edge_thickness
    else:
        startx = start[0]
    # Start at the bottom of the pcb, then draw upwards
    posy = start[1] - myind.pcb.thickness / 2

    # Draw the edge-plating
    femm.mi_drawrectangle(startx, posy,
                         startx + myind.pcb.edge_thickness, posy + myind.pcb.thickness)  # +2*(simParam.copper_thickness_outer-simParam.copper_thickness
    femm.mi_addblocklabel(startx + myind.pcb.edge_thickness / 2, posy + myind.pcb.thickness / 2)
    femm.mi_selectlabel(startx + myind.pcb.edge_thickness / 2, posy + myind.pcb.thickness / 2)
    femm.mi_setblockprop('Copper', simParam.COPPER_AUTOMESH, simParam.COPPER_MESHSIZE, f'{windingName}1', 0, 0, 1)
    femm.mi_clearselected()

    # If the winding is on the right side of the core the starting
    # x-coordinate needs to be adjusted
    if positionToCore == 'l':
        startx = start[0] - myind.winding['width']
    else:
        startx = start[0] + myind.pcb.edge_thickness
    mywidth = myind.winding['width'] - myind.pcb.edge_thickness

    # This fuction can only be called for single-turn inductors 
    # -> All turns are in parallel
    for j in range(1, myind.pcb.layers + 1):
        # Change the thickness for the outer layers
        if j == 1 or j == myind.pcb.layers:
            thickness = myind.pcb.copper_thickness_outer
        else:
            thickness = myind.pcb.copper_thickness
        
        femm.mi_drawrectangle(startx, posy, startx + mywidth, posy + thickness)
        femm.mi_addblocklabel(startx + mywidth / 2, posy + thickness / 2)
        femm.mi_selectlabel(startx + mywidth / 2, posy + thickness / 2)
        femm.mi_setblockprop('Copper', simParam.COPPER_AUTOMESH, simParam.COPPER_MESHSIZE, f'{windingName}1', 0, 0, 1)
        femm.mi_clearselected()

        posy = posy + thickness + myind.pcb.insulator_thickness
