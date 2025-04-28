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

classdef Result
    % This class stores all results that are obtained from a certain
    % simulation.
    % The idea is to have one object for the results from axisymmetric
    % simulation and one for the results from planar simulation
    
    properties   
        L_self double           % Self-inductance from planar simulation
        k double = 0            % coupling-factor
        L_coupled double = 0    % mutual inductance
        L_out double            % Common inductance in the transformer model
        L_m double              % Magnetizing inductance in the transformer model

        % switching frequency
        fs double
        % Required input and output capacitance
        Cin double
        Cout double
        % FET conduction loss
        conduction_loss double = 0
        
        % Copper loss per coil for each harmonic
        loss_copper_harmonic double = []
        % Total copper loss
        loss_copper double = 0
        % Total core loss / core loss per area when calculating in x and y 
        % direction separately and then summing both
        loss_core double = 0
        loss_core_area double = []
        % Total loss of the design (including MOSFET conduction losses)
        % Uses loss_core_xy
        loss_total double = 0
        % Stores Bx(t), By(t), and |B(t)| for each area at timestamps defined in time_interpol
        bx_waveform double = []
        by_waveform double = []
        babs_waveform double = []
        time_interpol double = []
        % Hdc for each area
        Hdc double = []

        % Time it took for the simulation to complete
        elapsedTime
    end
    
    methods
        function obj = Result()
            % Create a result object
        end
        function obj = calcTrafoModel(obj)
            obj.L_out = (obj.L_self+obj.L_coupled)/2;
            obj.L_m = (obj.L_self-obj.L_coupled)/2;
        end
    end
end

