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

class PCB:
    # Stores all the data regarding the PCB. 
    # These values are usually constant for a set of simulations, 
    # as they are defined by the manufacturer.
    
    def __init__(self):
        # Construct an instance of this class
        self.copper_thickness = 0.1  # 0.07;        # Copper thickness
        self.copper_thickness_outer = 0.05  # 0.035; # Copper thickness of outer layers
        self.layers = 6                 # Number of usable PCB Layers
        self.thickness = 1            # Total thickness of the board
        self.spacing_hor = 0.2          # Horizontal distance between windings and the core
        self.edge_thickness = 0.025     # Thickness of the edge-plating (on designs with single turn you may use edge-plating inside the coil to decrease losses)
        
        total_copper = (self.layers - 2) * self.copper_thickness + 2 * self.copper_thickness_outer
        self.insulator_thickness = (self.thickness - total_copper) / (self.layers - 1)  # Prepreg thickness if all layers were spaced evenly
