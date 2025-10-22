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
import numpy as np
import femm
from Material import Material
from PCB import PCB
from standardWinding import standardWinding

class Inductor:
    # This class stores all parameters that are specific to a certain
    # inductor design.
    # It contains the properties of the 3d-design, the properties translated for
    # planar and axisymmetric simulation, inductance,...
    # It does NOT contain information about the PCB, the core material
    # Note: Python objects are already reference types (like MATLAB handle class)
    # https://www.mathworks.com/matlabcentral/answers/322241-why-does-the-property-of-my-class-object-not-getting-changed-via-a-method
    
    def __init__(self, mymaterial):
        # Construct an instance of this class
        
        # Textual description of the design
        self.description = ""

        # Unique name of the design
        self.uniqueName = ""

        # Filenames of the simulation files in their basic configuration
        self.filename_planar = ""
        self.filename_axi = ""

        # Number of turns in a coil
        self.turns = 0

        # Positive (1), negative (-1) or no coupling (0)
        self.coupled = 0

        # Dimensions of the 3d-design in mm.
        # Properties are for a single structure, so if 'coupled'==1 for the
        # whole coupled inductor and if 'coupled'==0 for the single
        # inductor.
        self.dimension = {'width': 0, 'height': 0, 'depth': 0}

        # Define if the design is symmetrical in no, one or both axis.
        # Use with [x,y]. E.g. [0, 1] means symmetrical in y-axis only
        # If the design is symmetrical, only parts of the areas need to be
        # evaluated.
        # For designs that are symmetrical in one axis: Only the first half
        # of the rects is evaluated. Then length(names) = length(rects)/2
        # For designs that are symmetrical in both axis: Only the first quater
        # of the rects is evaluated. Then length(names) = length(rects)/4
        self.symm = []

        # Areas of the design in planar simulation. Each area is rectangular and has
        # four coordinates, so the array is 3d and needs to look as follows:
        # First dimension: Rectangle index. Second dimension: Corner (0 or 1). Third dimension: Coordinate (x=0, y=1)
        # I.e. rects_planar[0,0,:] gives both coordinates of the first corner of the first rectangle
        # rects_planar[:,:,0] gives all x coordinates of all corners of all rectangles
        # rects_planar[0,:,:] = [[rect0_x_start, rect0_y_start], [rect0_x_end, rect0_y_end]]
        # rects_planar[1,:,:] = [[rect1_x_start, rect1_y_start], [rect1_x_end, rect1_y_end]]
        # start and end need to be opposing corners
        self.rects_planar = []
        # Names of the different areas. If an area is not out of
        # core material but Air, name it "Air". names_planar needs to have 
        # the same length as rects_planar!
        self.names_planar = []
        # Centers of the areas that should be evaluated in the simulation
        self.centers_planar = []
        # Simulation depth for the planar simulation
        self.depth_planar = 0
        # Points where the "air"-property should be added to the
        # simulation.
        # Use as follows: [[airx1, airy1], [airx2, airy2], ...]
        self.air_planar = []
      
        # Areas of the design in axisymmetric simulation.
        # Works in the same way as planar
        self.rects_axi = []
        # Names of the areas
        self.names_axi = []
        # Centers of the areas that should be evaluated in the simulation
        self.centers_axi = []
        # Points where the "air"-property should be added to the
        # simulation.
        # Use as follows: [[airx1, airy1], [airx2, airy2], ...]
        self.air_axi = []

        # Winding-related things:
        # Stores the function-pointer to the winding function that is used
        # to draw the windings
        # planar/axi_start: [[Aleft_startx, Aleft_centery], [Aright_startx, Aright_centery], ...]; 
        self.winding = {'function': standardWinding,
                        'width': 0,
                        'planar_start': np.array([[0, 0], [0, 0]]),
                        'axi_start': np.array([[0, 0], [0, 0]])}

        # Store the material properties in here as well. The material is
        # initialized when calling Inductor(mymaterial)
        self.material = Material(mymaterial)
        # Create a new pcb object that is also stored here
        self.pcb = PCB()

    # Calculates the centers of the rectangles specified in
    # rects_planar and rects_axi.
    def calcCenters(self):
        # Planar
        if len(self.rects_planar) > 0:
            self.centers_planar = np.zeros((2, self.rects_planar.shape[0]))
            for i in range(self.rects_planar.shape[0]):
                self.centers_planar[:, i] = [np.mean(self.rects_planar[i, :, 0]), np.mean(self.rects_planar[i, :, 1])]
        # Axi
        if len(self.rects_axi) > 0:
            self.centers_axi = np.zeros((2, self.rects_axi.shape[0]))
            for i in range(self.rects_axi.shape[0]):
                self.centers_axi[:, i] = [np.mean(self.rects_axi[i, :, 0]), np.mean(self.rects_axi[i, :, 1])]

    # Complile the most important parameters into a unique name.
    # This also sets filename_planar and filename_axi
    def createUniqueName(self, customText, simParam):
        self.uniqueName = f"{customText}_{self.description}_{self.material.name}_whd_{self.dimension['width']:.2f}_{self.dimension['height']:.2f}_{self.dimension['depth']:.2f}"
        self.filename_planar = os.path.join(simParam.femm_folder, f"planar_{self.uniqueName}")
        self.filename_axi = os.path.join(simParam.femm_folder, f"axi_{self.uniqueName}")

    # Show the design
    # result: Array with the result objects
    # sim == 1: Planar, sim == 2: Axi
    # harmonic: Number of the harmonic (0=DC)
    # type: Type of the plot. Valid options are directly from
    # mo_showdensityplot. Common: 'mag' for B, 'jmag' for J, hmag for H
    # max: Upper limit of the scale
    def showDesign(self, result, sim, harmonic, type, maxScale):
        femm.openfemm()
        if sim == 1:
            freqfile = f"{self.filename_planar}_f{result[0].fs/1e6*harmonic:.2f}MHz"
            rects = self.rects_planar
        else:
            freqfile = f"{self.filename_axi}_f{result[1].fs/1e6*harmonic:.2f}MHz"
            rects = self.rects_axi
        femm.opendocument(f"{freqfile}.fem")
        femm.mi_loadsolution()

        femm.mo_zoom(np.min(rects[:, :, 0]) * 1.1,
                    np.min(rects[:, :, 1]) * 1.1,
                    np.max(rects[:, :, 0]) * 1.1,
                    np.max(rects[:, :, 1]) * 1.1)
        # Show flux-density
        femm.mo_showdensityplot(1, 0, maxScale, 0, type)
