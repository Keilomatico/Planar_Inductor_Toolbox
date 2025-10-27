% This file is part of the Planar Inductor Toolbox
% Copyright (C) 2025 Adrian Keil
% 
% The Planar Inductor Toolbox is free software: you can redistribute it 
% and/or modify it under the terms of the GNU General Public License as 
% published by the Free Software Foundation, either version 3 of the 
% License, or (at your option) any later version.
% 
% The Planar Inductor Toolbox is distributed in the hope that it will be
% useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with this program.  
% If not, see https://www.gnu.org/licenses/gpl-3.0.html

classdef simulationParameters
    % Parameters of the core are defined here
    
    properties
        %% ----------------------FEMM Simulation-------------------
        % To speed up the simulation, it is faster to use a linear BH-relationship.
        % Speeds up by approx. 2x. The error is negligible (<1% for the inductance).
        USE_BHCURVE = 0;
        % FEMM parameters
        % Automesh the core, so meshsize doesn't matter
        CORE_AUTOMESH = 1;
        CORE_MESHSIZE = 0;
        % Automesh air, so meshsize doesn't matter
        AIR_AUTOMESH = 1;
        AIR_MESHSIZE = 0;
        % Use custom meshsize for copper as the automesh is a bit too coarse
        COPPER_AUTOMESH = 0;
        COPPER_MESHSIZE = 0.05;
        % Minimize the FEMM windows
        MINIMIZE_FEMM = 0;

        % In order to calculate the depth for the planar simulation, the
        % round coild needs to be streched into a linear shape.
        % We assume that the current flows on average not in the center of the
        % winding but closer to the center. 
        % 2*planar_depth = 2*pi*(inner_winding_radius + weighted_center*winding_width);
        weighted_center = 0.1;

        %% -----------------Script parameters-----------------
        % Enable/disable planar/axisymmetric simulation [Planar_enable, Axi_enable]. 
        % For coupled designs, the inductance is always determined from
        % planar simulation because axisymmetric cannot reflect coupling
        % (except for designs with both windigs on one limb but that is 
        % too special to make an exception)
        SIMULATIONS = [1, 0];
        % Calculate the required capacitance
        CALC_CAP = false;
        % Show plots
        SHOWPLOTS = 1;
        % Show the design in the end
        SHOWDESIGN = 1;
    
        % Max. number of harmonics to analyze
        NUM_HARMONICS = 4;
        % If amplitude of a harmonic is smaller than HARMONIC_FACTOR*amp_fundamental: Ignore
        HARMONIC_FACTOR = 0.1;     


        % Enable verbose with a certain detail-level. 0 is only the most
        % relevant stuff.
        verbose = true;
        verbose_detail = 4;
        % Enable writing to the logfile
        writeLogfile = true;
        logfile_detail = 5;

        % Choose if you want to reuse previously generated files. Not all parameters are embedded into
        % the filename, so this may lead to wrong results. Check uniqueName for the included parameters.
        reuse_file = 0;

        % Path to the folder in which the femm-files are stored
        femm_folder = 'C:\Users\adria\Documents\Masterarbeit\femm'
        % Path to the folder in which the logfiles are stored
        log_folder = 'logfiles'
        % Path to the folder in which the .m-files are stored
        datafolder = 'data';
        % Clear the datafolder before starting the script
        clearData = 0;

        %% -----------------Physical constants-----------------
        mu0 = 1.256637061e-6;
        eps0 = 8.8541878e-12;
        rho_copper = 1.68e-8;   % Ohm*m

        %% -----------------Operating Point-----------------
        Vin = 48;
        Vout = 12;
        D;
        % Average output current for both phases together
        iout_avg = 80;
        pout;
        % Frequency at which the inductance is measured. Doesn't really matter
        % whether it's 1 or 3 MHz, but difference to DC is big.
        target_fs = 1.5e6;

        % Desired input and output ripple for capacitor calculation
        DeltaVinMax = 150e-3;
        DeltaVoutMax = 50e-3;
        
        %% --------------------FET--------------------
        Rds_on = 1.4e-3/2;           % Total on-resistance
        Cds = 1e-9;                  % Drain-Source capacitance
        deadTime = 5e-9;             % Desired dead time
    end

    methods
        function obj = simulationParameters()
            % Construct an instance of this class
            obj.D = obj.Vout/obj.Vin;
            obj.pout = obj.Vout*obj.iout_avg;

            % Clear/create data folder if wanted/needed
            if isfolder(obj.datafolder)
                if obj.clearData
                    delete(sprintf("%s/*", obj.datafolder));
                end
            else
                mkdir(obj.datafolder)
            end

            % Create femm_folder if it doesn't exist
            if ~isfolder(obj.femm_folder)
                mkdir(obj.femm_folder)
            end

            % Create log_folder if it doesn't exist
            if ~isfolder(obj.log_folder)
                mkdir(obj.log_folder)
            end
        end
    end
end



