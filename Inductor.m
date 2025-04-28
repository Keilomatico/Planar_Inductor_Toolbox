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

classdef Inductor < handle 
    % This class stores all parameters that are specific to a certain
    % inductor design.
    % It contains the properties of the 3d-design, the properties translated for
    % planar and axisymmetric simulation, inductance,...
    % It does NOT contain information about the PCB, the core material
    % Inherit the handle class to be able to work on its own values. See
    % https://www.mathworks.com/matlabcentral/answers/322241-why-does-the-property-of-my-class-object-not-getting-changed-via-a-method
    
    properties
        % Textual description of the design
        description string

        % Unique name of the design
        uniqueName string

        % Filenames of the simulation files in their basic configuration
        filename_planar string
        filename_axi string

        % Number of turns in a coil
        turns double

        % Positive (1), negative (-1) or no coupling (0)
        coupled double

        % Dimensions of the 3d-design in mm.
        % Properties are for a single structure, so if 'coupled'==1 for the
        % whole coupled inductor and if 'coupled'==0 for the single
        % inductor.
        dimension struct = struct('width', 0, ...
                           'height', 0, ...
                           'depth', 0)

        % Define if the design is symmetrical in no, one or both axis.
        % Use with [x,y]. E.g. [0, 1] means symmetrical in y-axis only
        % If the design is symmetrical, only parts of the areas need to be
        % evaluated.
        % For designs that are symmetrical in one axis: Only the first half
        % of the rects is evaluated. Then length(names) = length(rects)/2
        % For designs that are symmetrical in both axis: Only the first quater
        % of the rects is evaluated. Then length(names) = length(rects)/4
        symm double = []

        % Areas of the design in planar simulation. Each area is rectangular and has
        % four coordinates, so the array is 3d and needs to look as follows:
        % rects_planar(:,:,1) = [[rect1_x_start; rect1_y_start], [rect1_x_end; rect1_y_end]];
        % rects_planar(:,:,2) = [[rect2_x_start; rect2_y_start], [rect2_x_end; rect2_y_end]];
        % start and end need to be opposing corners
        rects_planar double = []
        % Names of the different areas. If an area is not out of
        % core material but Air, name it "Air". names_planar needs to have 
        % the same length as rects_planar!
        names_planar string {mustBeText} = []
        % Centers of the areas that should be evaluated in the simulation
        centers_planar double = []
        % Simulation depth for the planar simulation
        depth_planar double;
        % Points where the "air"-property should be added to the
        % simulation.
        % Use as follows: [airx1; airy1], [airx2; airy2], ...]
        air_planar double = [];
      
        % Areas of the design in axisymmetric simulation.
        % Works in the same way as planar
        rects_axi double = []
        % Names of the areas
        names_axi string {mustBeText} = []
        % Centers of the areas that should be evaluated in the simulation
        centers_axi double = []
        % Points where the "air"-property should be added to the
        % simulation.
        % Use as follows: [airx1; airy1], [airx2; airy2], ...]
        air_axi double = [];

        % Winding-related things:
        % Stores the function-pointer to the winding function that is used
        % to draw the windings
        % planar/axi_start: [[Aleft_startx; Aleft_centery], [Aright_startx; Aleft_centery], ...]; 
        winding = struct('function', @standardWinding, ...
                         'width', 0, ...
                         'planar_start', [[0; 0], [0; 0]], ...
                         'axi_start', [[0; 0], [0; 0]])

        % Store the material properties in here as well. The material is
        % initialized when calling Inductor(mymaterial)
        material Material
        % Create a new pcb object that is also stored here
        pcb PCB
    end
    
    methods
        function obj = Inductor(mymaterial)
            % Construct an instance of this class
            obj.material = Material(mymaterial);
            obj.pcb = PCB();
        end

        % Calculates the centers of the rectangles specified in
        % rects_planar and rects_axi.
        function calcCenters(obj)
            % Planar
            for i=1:length(obj.rects_planar)
                obj.centers_planar(:, i) = [mean(obj.rects_planar(1,:,i)), mean(obj.rects_planar(2,:,i))];
            end
            % Axi
            for i=1:length(obj.rects_axi)
                obj.centers_axi(:, i) = [mean(obj.rects_axi(1,:,i)), mean(obj.rects_axi(2,:,i))];
            end
        end

        % Complile the most important parameters into a unique name.
        % This also sets filename_planar and filename_axi
        function createUniqueName(obj, customText, simParam)
            obj.uniqueName = sprintf("%s_%s_%s_whd_%.2f_%.2f_%.2f", ...
                customText, obj.description, obj.material.name, obj.dimension.width, obj.dimension.height, obj.dimension.depth);
            obj.filename_planar = sprintf("%s/planar_%s", simParam.femm_folder, obj.uniqueName);
            obj.filename_axi = sprintf("%s/axi_%s", simParam.femm_folder, obj.uniqueName);
        end

        % Show the design
        % result: Array with the result objects
        % sim == 1: Planar, sim == 2: Axi
        % harmonic: Number of the harmonic (0=DC)
        % type: Type of the plot. Valid options are directly from
        % mo_showdensityplot. Common: 'mag' for B, 'jmag' for J, hmag for H
        % max: Upper limit of the scale
        function showDesign(obj, result, sim, harmonic, type, maxScale)
            openfemm;
            if sim==1
                freqfile = sprintf("%s_f%.2fMHz", obj.filename_planar, result(1).fs/1e6*harmonic);
                rects = obj.rects_planar;
            else
                freqfile = sprintf("%s_f%.2fMHz", obj.filename_axi, result(2).fs/1e6*harmonic);
                rects = obj.rects_axi;
            end
            opendocument(char(freqfile+'.fem'));
            mi_loadsolution
    
            mo_zoom(min(rects(1,:,:),[], "all")*1.1, ...
                min(rects(2,:,:),[], "all")*1.1, ...
                max(rects(1,:,:),[], "all")*1.1, ...
                max(rects(2,:,:),[], "all")*1.1)
            % Show flux-density
            mo_showdensityplot(1, 0, maxScale, 0, type)
        end

    end
end

