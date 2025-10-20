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

from Inductor import Inductor
from standardWinding import standardWinding
from standardWindingEdge import standardWindingEdge
from curvedWinding import curvedWinding
from coreSingleInductor import coreSingleInductor
from coreFourPole import coreFourPole

def designs(design_num, simParam):
    """This file contains the different inductor designs"""

    # Create a new raw inductor object from a certain material
    myind = Inductor("PC200")

    # coreParam contains all the free parameters of a certain core.
    # Then a processing function like coreSingleInductor() is called which
    # uses those parameters to create a fully-filled Inductor object
    # This struct contains different fields depending on the specific design.
    fpParam = {}

    ## Single Inductors
    if design_num == 1:
        # Specify a single inductor which just consists of a UU-core 
        # without gap. 
        # The structure is symmetrical in x and y direction, 
        # so only side and top need to be parameterized.
        # This design is absolutely not feasible in reality and just
        # here to provide an easy first example
        myind.description = "Single Inductor without pillar"
        myind.turns = 2
        myind.winding['width'] = 3
        myind.winding['function'] = standardWinding
        
        # Specify the parameters of the inductor
        # Area of the side (per side)
        singleIndParam = {}
        singleIndParam['A_side'] = 40
        # Area inside the winding
        singleIndParam['A_winding'] = 110
        # Cross-sectional area of the top/bottom piece 
        # Note: Actually, just cores with rectangular limbs have a constant
        # cross-sectional area of the top/bottom, so this dimension is
        # a bit arbitrary here. For planar simulation, it is actually
        # the cross-sectional area but not in reality.
        singleIndParam['A_top'] = 50
        # Vertical spacing between PCB and core
        singleIndParam['PCB_Spacing'] = 2

        myind = coreSingleInductor(myind, singleIndParam, simParam)
    
    elif design_num == 2:
        # Example for another single inductor like the previous one but
        # with different parameters
        # Much more reasonable design but still very high copper loss
        # due to missing pillar
        myind.description = "Single Inductor without pillar, 1.5 MHz, edge plating"
        myind.turns = 1
        myind.winding['width'] = 2
        myind.winding['function'] = standardWindingEdge
        
        # Specify the parameters of the inductor
        # Area of the side (per side)
        singleIndParam = {}
        singleIndParam['A_side'] = 25
        # Area inside the winding
        singleIndParam['A_winding'] = 80
        # Cross-sectional area of the top/bottom piece 
        # Note: Actually, just cores with rectangular limbs have a constant
        # cross-sectional area of the top/bottom, so this dimension is
        # a bit arbitrary here. For planar simulation, it is actually
        # the cross-sectional area but not in reality.
        singleIndParam['A_top'] = 40
        # Vertical spacing between PCB and core
        singleIndParam['PCB_Spacing'] = 0.2

        myind = coreSingleInductor(myind, singleIndParam, simParam)
    
    ## Coupled Inductors
    elif design_num == 3:
        # Four-Pole structure
        myind.description = "Four-pole, standard winding"
        # Single turn
        myind.turns = 1
        # Negative coupling
        myind.coupled = -1
        myind.winding['width'] = 3
        myind.winding['function'] = standardWinding

        # Specify the parameters of the inductor
        # Area of the side (for each side)
        fpParam['A_side'] = 40
        # Area of the pillar
        fpParam['A_pillar'] = 50
        # Cross-sectional area of the top/bottom piece 
        fpParam['A_top'] = 40
        fpParam['A_bot'] = 45
        # Express gaps in relation to the area such that reluctance
        # stays more or less constant when area is modified
        fpParam['gap_side'] = fpParam['A_side'] / 32
        fpParam['gap_pillar'] = fpParam['A_pillar'] / 55
        # Vertical spacing between PCB and core
        fpParam['PCB_Spacing_top'] = 1.4
        fpParam['PCB_Spacing_bot'] = 1.2
        # Center the pillar
        fpParam['centerPillar'] = True

        myind = coreFourPole(myind, fpParam, simParam)
    
    elif design_num == 4:
        # Four-Pole with curved windings
        myind.description = "Four-pole, curved winding"
        # Single turn
        myind.turns = 1
        # Negative coupling
        myind.coupled = -1
        myind.winding['width'] = 3
        myind.winding['function'] = curvedWinding
        # Settings for curved windings. 
        # Add them to myind such that they will be passed to the
        # function
        myind.winding['shortenWindingRadius'] = 0.6
        # Increase the effect of shortening
        myind.winding['shortenFactor'] = 4

        # Specify the parameters of the inductor
        # Area of the side (for each side)
        fpParam['A_side'] = 40
        # Area of the pillar
        fpParam['A_pillar'] = 50
        # Cross-sectional area of the top/bottom piece 
        fpParam['A_top'] = 40
        fpParam['A_bot'] = 45
        # Express gaps in relation to the area such that reluctance
        # stays more or less constant when area is modified
        fpParam['gap_side'] = fpParam['A_side'] / 32
        fpParam['gap_pillar'] = fpParam['A_pillar'] / 55
        # Vertical spacing between PCB and core
        fpParam['PCB_Spacing_top'] = 1.4
        fpParam['PCB_Spacing_bot'] = 1.2
        # Center the pillar
        fpParam['centerPillar'] = True

        myind = coreFourPole(myind, fpParam, simParam)
    
    elif design_num == 5:
        # Four-Pole with negative coupling
        myind.description = "Four-pole, positive coupling"
        # Single turn
        myind.turns = 1
        # Negative coupling
        myind.coupled = 1
        myind.winding['width'] = 3
        myind.winding['function'] = standardWinding

        # Specify the parameters of the inductor
        # Area of the side (for each side)
        fpParam['A_side'] = 40
        # Area of the pillar
        fpParam['A_pillar'] = 50
        # Cross-sectional area of the top/bottom piece 
        fpParam['A_top'] = 40
        fpParam['A_bot'] = 45
        # Express gaps in relation to the area such that reluctance
        # stays more or less constant when area is modified
        fpParam['gap_side'] = fpParam['A_side'] / 32
        fpParam['gap_pillar'] = fpParam['A_pillar'] / 55
        # Vertical spacing between PCB and core
        fpParam['PCB_Spacing_top'] = 1.4
        fpParam['PCB_Spacing_bot'] = 1.2
        # Center the pillar
        fpParam['centerPillar'] = True

        myind = coreFourPole(myind, fpParam, simParam)

    # Calculate the centers
    myind.calcCenters()
    customText = f"wnum{design_num}"
    myind.createUniqueName(customText, simParam)
    
    return myind
