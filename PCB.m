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

classdef PCB
    % Stores all the data regarding the PCB. 
    % These values are usually constant for a set of simulations, 
    % as they are defined by the manufacturer.
    
    properties
        copper_thickness = 0.1%0.07;        % Copper thickness
        copper_thickness_outer = 0.05%0.035; % Copper thickness of outer layers
        layers = 6;                 % Number of usable PCB Layers
        thickness = 1;            % Total thickness of the board
        spacing_hor = 0.2;          % Horizontal distance between windings and the core
        edge_thickness = 0.025;     % Thickness of the edge-plating (on designs with single turn you may use edge-plating inside the coil to decrease losses)
        insulator_thickness         % Prepreg thickness if all layers were spaced evenly
    end
    
    methods
        function obj = PCB()
            % Construct an instance of this class
            total_copper = (obj.layers-2)*obj.copper_thickness+2*obj.copper_thickness_outer;
            obj.insulator_thickness = (obj.thickness-total_copper)/(obj.layers-1);
        end
    end
end

