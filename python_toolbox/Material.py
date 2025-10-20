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

class Material:
    # Stores all material parameters. Different material can be loaded
    # using setMaterial().
    
    def __init__(self, materialName):
        # MATERIAL Construct an instance of this class
        # Important note: The way alpha and beta are used is not clearly
        # defined. In order to avoid confusion, we use bexp for the
        # exponent of the flux density and fexp for the exponent 
        self.name = ""
        self.fexp = 0.0
        self.bexp = 0.0
        self.k = 0.0
        self.bhcurve = []
        self.mu = 0.0
        
        self.setMaterial(materialName)
    
    def setMaterial(self, materialName):
        # Loads the parameters of a certain material
        # Valid options: "ML91S", "3F46", "PC200"
        self.name = materialName

        if materialName == "ML91S":
            # Steinmetz Parameters for Proterial 1-3 MHz, 100 °C
            # https://www.proterial.com/e/products/soft_magnetism/pdf/PR-EM13_MaDC-F.pdf#page=5 
            self.fexp = 2.784
            self.bexp = 3.077
            self.k = 2.067e-11

            # Specify the BH-curve. First row is B in mT, second row H in A/m
            self.bhcurve = np.array([[0, 15, 29, 45, 61, 79, 99, 123, 153, 183, 214, 277, 320, 346, 364, 377, 395, 404, 409, 413, 417, 419, 422, 424, 427, 428, 429],
                                     [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000]]).T

            self.mu = 900
        elif materialName == "3F46":
            # Steinmetz Parameters for Ferroxcube at 1MHz, 100°C
            # https://download.ferrite.de/pdf/3f46.pdf
            self.fexp = 2.5
            self.bexp = 2.34
            self.k = 3.3e-10
            self.mu = 550
        elif materialName == "PC200":
            # Steinmetz Parameters for TDK PC200. 
            # https://tools.tdk-electronics.tdk.com/mdt/index.php/pl_flux_density
            self.fexp = 1.67
            self.bexp = 2.3834
            P = 181.15
            f = 1e6
            B = 50e-3
            self.k = P / (f**self.fexp * B**self.bexp)
            self.mu = 800
