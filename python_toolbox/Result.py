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

class Result:
    # This class stores all results that are obtained from a certain
    # simulation.
    # The idea is to have one object for the results from axisymmetric
    # simulation and one for the results from planar simulation
    
    def __init__(self):
        # Create a result object
        self.L_self = 0.0           # Self-inductance from planar simulation
        self.k = 0.0                # coupling-factor
        self.L_coupled = 0.0        # mutual inductance
        self.L_out = 0.0            # Common inductance in the transformer model
        self.L_m = 0.0              # Magnetizing inductance in the transformer model

        # switching frequency
        self.fs = 0.0
        # Required input and output capacitance
        self.Cin = 0.0
        self.Cout = 0.0
        # FET conduction loss
        self.conduction_loss = 0.0
        
        # Copper loss per coil for each harmonic
        self.loss_copper_harmonic = []
        # Total copper loss
        self.loss_copper = 0.0
        # Total core loss / core loss per area when calculating in x and y 
        # direction separately and then summing both
        self.loss_core = 0.0
        self.loss_core_area = []
        # Total loss of the design (including MOSFET conduction losses)
        # Uses loss_core_xy
        self.loss_total = 0.0
        # Stores Bx(t), By(t), and |B(t)| for each area at timestamps defined in time_interpol
        self.bx_waveform = []
        self.by_waveform = []
        self.babs_waveform = []
        self.time_interpol = []
        # Hdc for each area
        self.Hdc = []

        # Time it took for the simulation to complete
        self.elapsedTime = 0.0
    
    def calcTrafoModel(self):
        self.L_out = (self.L_self + self.L_coupled) / 2
        self.L_m = (self.L_self - self.L_coupled) / 2
