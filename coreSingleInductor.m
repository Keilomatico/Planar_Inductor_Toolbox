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

function myind = coreSingleInductor(myind, core, simParam)
    % Caculates the rectangles of an inductor which is symmetric 
    % in x and y with no outer gaps
    % (0,0) is in the center of the core

    %% General settings
    % This design is just a single inductor, i.e. no coupling
    myind.coupled = 0;
    % The design is symmetrical in x and y direction
    myind.symm = [1, 1];

    %% Calculate parameters of the real core (for size comparisons)
    % Radius inside the winding
    r_windingInner = sqrt(core.A_winding/pi);
    % Depth = ouside of the winding
    myind.dimension.depth = 2*(r_windingInner + myind.winding.width + myind.pcb.spacing_hor);
    w_side_real = core.A_side / myind.dimension.depth;
    h_top_real = core.A_top / myind.dimension.depth;
    myind.dimension.width = 2*(r_windingInner+myind.winding.width+myind.pcb.spacing_hor+w_side_real);
    myind.dimension.height = 2*h_top_real+myind.pcb.thickness+2*core.PCB_Spacing;

    %% Calculate dimensions for planar simulation
    % Stretch the winding into a linear shape for simulation
    % Half of the equivalent winding length is the depth we use in simulation
    myind.depth_planar = pi*(r_windingInner + simParam.weighted_center*myind.winding.width);
    % Calculate the width to the coil
    w_center = core.A_winding / myind.depth_planar / 2;
    % Calculate the width of the side
    w_side_planar = core.A_side / myind.depth_planar;
    % Top area is just an aproximation because in the real design the
    % flux-density is larger towards the center because then the
    % cross-sectional area is smaller then at the outside
    h_top_planar = core.A_top / myind.depth_planar;
    % Specify where the winding should start
    myind.winding.planar_start = [[-w_center; 0], [w_center; 0]]; 

    %% Calculate dimensions for axisymmetric simulation
    % Area inside the winding, and winding width are the same as in the
    % original design.
    % Calculate the total radius. We can use:
    % A_side*2 = pi*(r_total_axi^2-r_outsideWinding^2)
    % *2 because in the original design the area is only specified for one side
    r_outsideWinding = r_windingInner+myind.winding.width+myind.pcb.spacing_hor;
    r_total_axi = sqrt(core.A_side*2/pi+r_outsideWinding^2);
    % Width of the outer ring is the difference between outer and inner radius
    w_side_axi = r_total_axi-r_outsideWinding;
    % Use the same volume for the top-part as in the original design
    %h_top_axi = myind.dimension.width*core.A_top / (pi*r_total_axi^2);
    % Use the circumference above the inside of the winding for A_top
    h_top_axi = core.A_top / (2*pi*r_windingInner/2);
    % Specify where the winding should start
    myind.winding.axi_start = [r_windingInner; 0];

    %% Specify where the "air"-property should be placed
    % For planar, place "air" in the center and above the core
    myind.air_planar = [[0; 0], [0; (myind.pcb.thickness/2+core.PCB_Spacing+h_top_planar)*1.5]];
    % For axi, place air slightly right of center and above the core
    myind.air_axi = [[r_windingInner/2; 0], [r_windingInner/2; (myind.pcb.thickness/2+core.PCB_Spacing+h_top_axi)*1.5]];

    %% Calculate the rectangles
    % When specifying the rectangles make sure to use areas with relatively
    % uniform flux distribution. You can start with just the minimum number
    % of rectangles that is required to draw the design and then add more
    % if a more precise Hdc and core-loss is desired.
    myind.names_planar = ["Center", "OverWinding",  "Outer"];
    myind.rects_planar = getRectangle(0, myind.pcb.thickness/2+core.PCB_Spacing, ...
        w_center, h_top_planar);
    myind.rects_planar(:,:,2) = getRectangle(w_center, myind.pcb.thickness/2+core.PCB_Spacing, ...
        myind.winding.width+myind.pcb.spacing_hor, h_top_planar);
    myind.rects_planar(:,:,3) = getRectangle(w_center+myind.winding.width+myind.pcb.spacing_hor, 0, ...
        w_side_planar, myind.pcb.thickness/2+core.PCB_Spacing+h_top_planar);

    myind.names_axi = myind.names_planar;
    myind.rects_axi = getRectangle(0, myind.pcb.thickness/2+core.PCB_Spacing, ...
        r_windingInner, h_top_axi);
    myind.rects_axi(:,:,2) = getRectangle(r_windingInner, myind.pcb.thickness/2+core.PCB_Spacing, ...
        myind.winding.width+myind.pcb.spacing_hor, h_top_axi);
    myind.rects_axi(:,:,3) = getRectangle(r_windingInner+myind.winding.width+myind.pcb.spacing_hor, 0, ...
        w_side_axi, myind.pcb.thickness/2+core.PCB_Spacing+h_top_axi);

    %% Mirror the rectangles to create a full design
    % Planar: Mirror to the left and down
    myind.rects_planar(:,:,4:6) = mirrorRects(myind.rects_planar, 'x');
    myind.rects_planar(:,:,7:12) = mirrorRects(myind.rects_planar, 'y');
    % Axi: Only mirror down
    myind.rects_axi(:,:,4:6) = mirrorRects(myind.rects_axi, 'y');
end