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
import shutil

class SimulationParameters:
    # Parameters of the core are defined here
    
    def __init__(self):
        # Construct an instance of this class
        
        ## ----------------------FEMM Simulation-------------------
        # To speed up the simulation, it is faster to use a linear BH-relationship.
        # Speeds up by approx. 2x. The error is negligible (<1% for the inductance).
        self.USE_BHCURVE = 0
        # FEMM parameters
        # Automesh the core, so meshsize doesn't matter
        self.CORE_AUTOMESH = 1
        self.CORE_MESHSIZE = 0
        # Automesh air, so meshsize doesn't matter
        self.AIR_AUTOMESH = 1
        self.AIR_MESHSIZE = 0
        # Use custom meshsize for copper as the automesh is a bit too coarse
        self.COPPER_AUTOMESH = 0
        self.COPPER_MESHSIZE = 0.05
        # Minimize the FEMM windows
        self.MINIMIZE_FEMM = 0
        # Hide the FEMM window (0 = show, 1 = hide)
        self.HIDE_FEMM = 1

        # In order to calculate the depth for the planar simulation, the
        # round coild needs to be streched into a linear shape.
        # We assume that the current flows on average not in the center of the
        # winding but closer to the center. 
        # 2*planar_depth = 2*pi*(inner_winding_radius + weighted_center*winding_width);
        self.weighted_center = 0.1

        ## -----------------Script parameters-----------------
        # Enable/disable planar/axisymmetric simulation [Planar_enable, Axi_enable]. 
        # For coupled designs, the inductance is always determined from
        # planar simulation because axisymmetric cannot reflect coupling
        # (except for designs with both windigs on one limb but that is 
        # too special to make an exception)
        self.SIMULATIONS = [1, 0]
        # Calculate the required capacitance
        self.CALC_CAP = True
        # Show plots
        self.SHOWPLOTS = 1
        # Show the design in the end
        self.SHOWDESIGN = 1
        # Which simulation to show: 0 = planar, 1 = axisymmetric
        self.SHOWDESIGN_SIMULATION = 0
    
        # Max. number of harmonics to analyze
        self.NUM_HARMONICS = 4
        # If amplitude of a harmonic is smaller than HARMONIC_FACTOR*amp_fundamental: Ignore
        self.HARMONIC_FACTOR = 0.1


        # Enable verbose with a certain detail-level. 0 is only the most
        # relevant stuff.
        self.verbose = True
        self.verbose_detail = 4
        # Enable writing to the logfile
        self.writeLogfile = True
        self.logfile_detail = 5

        # Choose if you want to reuse previously generated files. Not all parameters are embedded into
        # the filename, so this may lead to wrong results. Check uniqueName for the included parameters.
        self.reuse_file = 1

        # Path to the folder in which the femm-files are stored
        self.femm_folder = 'femm'
        # Path to the folder in which the logfiles are stored
        self.log_folder = 'logfiles'
        # Path to the folder in which the .m-files are stored
        self.datafolder = 'data'
        # Clear the datafolder before starting the script
        self.clearData = 0

        ## -----------------Physical constants-----------------
        self.mu0 = 1.256637061e-6
        self.eps0 = 8.8541878e-12
        self.rho_copper = 1.68e-8   # Ohm*m

        ## -----------------Operating Point-----------------
        self.Vin = 48
        self.Vout = 12
        # Average output current for both phases together
        self.iout_avg = 0.01
        # Frequency at which the inductance is measured. Doesn't really matter
        # whether it's 1 or 3 MHz, but difference to DC is big.
        self.target_fs = 1.5e6
        
        # Overwrite the calculated switching frequency with a fixed value [Hz]
        # Set to -1 to use the calculated frequency (default behavior)
        # If set to a positive value, this frequency will be used instead of calculating it
        self.fs_overwrite = 2e6

        # Desired input and output ripple for capacitor calculation
        self.DeltaVinMax = 150e-3
        self.DeltaVoutMax = 50e-3
        
        ## --------------------FET--------------------
        self.Rds_on = 1.4e-3 / 2           # Total on-resistance
        self.Cds = 1e-9                  # Drain-Source capacitance
        self.deadTime = 5e-9            # Desired dead time
        
        # Calculated parameters
        self.D = self.Vout / self.Vin
        self.pout = self.Vout * self.iout_avg
        self.Ts = 1 / self.target_fs

        # Clear/create data folder if wanted/needed
        if os.path.isdir(self.datafolder):
            if self.clearData:
                shutil.rmtree(self.datafolder)
                os.makedirs(self.datafolder)
        else:
            os.makedirs(self.datafolder)

        # Create femm_folder if it doesn't exist
        if not os.path.isdir(self.femm_folder):
            os.makedirs(self.femm_folder)

        # Create log_folder if it doesn't exist
        if not os.path.isdir(self.log_folder):
            os.makedirs(self.log_folder)
