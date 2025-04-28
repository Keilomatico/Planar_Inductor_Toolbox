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

function myind = coreFourPole(myind, core, simParam)
    % Calculates rectangles for a four-pole core. 
    % X=0 is in between the two windings
    % Y=0 is right below the top piece

    %% General settings
    % The design is symmetrical in x direction
    myind.symm = [1, 0];

    %% Calculate parameters of the real core (for size comparisons)
    % Radius inside the winding
    r_pillar = sqrt(core.A_pillar/pi);
    % Depth = ouside of the winding
    myind.dimension.depth = 2*(r_pillar + myind.winding.width + myind.pcb.spacing_hor*2);
    w_side_real = core.A_side / myind.dimension.depth;
    h_top_real = core.A_top / myind.dimension.depth;
    h_bot_real = core.A_bot / myind.dimension.depth;
    myind.dimension.width = 2*(2*(r_pillar+myind.winding.width+2*myind.pcb.spacing_hor)+w_side_real);
    myind.dimension.height = h_top_real+h_bot_real+myind.pcb.thickness+core.PCB_Spacing_top+core.PCB_Spacing_bot;

    %% Calculate dimensions for planar simulation
    % Stretch the winding into a linear shape for simulation
    % Half of the equivalent winding length is the depth we use in simulation
    myind.depth_planar = pi*(r_pillar + simParam.weighted_center*myind.winding.width);
    % Calculate the width of the pillar
    w_pillar_planar = core.A_pillar / myind.depth_planar;
    % Calculate the width of the side
    w_side_planar = core.A_side / myind.depth_planar;
    % Top and bottom
    h_top_planar = core.A_top / myind.depth_planar;
    h_bot_planar = core.A_bot / myind.depth_planar;
    % Distance between top and bottom (i.e. height of the window)
    h_window_planar = core.PCB_Spacing_top + core.PCB_Spacing_bot + myind.pcb.thickness;
    % Width of the window
    w_window_planar = myind.winding.width + 2*myind.pcb.spacing_hor;
    % Specify where the winding should start
    myind.winding.planar_start = [[-w_pillar_planar/2-myind.pcb.spacing_hor; -core.PCB_Spacing_top-myind.pcb.thickness/2], ...
        [w_pillar_planar/2+myind.pcb.spacing_hor; -core.PCB_Spacing_top-myind.pcb.thickness/2]]; 

    %% Calculate dimensions for axisymmetric simulation
    % Calculate the total radius. We can use:
    % A_side*2 = pi*(r_total_axi^2-r_outsideWinding^2)
    % *2 because in the original design the area is only specified for one side
    r_outsideWinding = r_pillar+myind.winding.width+myind.pcb.spacing_hor*2;
    r_total_axi = sqrt(core.A_side*2/pi+r_outsideWinding^2);
    % Width of the outer ring is the difference between outer and inner radius
    w_side_axi = r_total_axi-r_outsideWinding;
    % Use the same volume for the top-part as in the original design
    %h_top_axi = myind.dimension.width*core.A_top / (pi*r_total_axi^2);
    %h_bot_axi = myind.dimension.width*core.A_bot / (pi*r_total_axi^2);
    % Use the circumference above the inside of the winding for A_top
    h_top_axi = core.A_top / (2*pi*r_pillar/2);
    h_bot_axi = core.A_bot / (2*pi*r_pillar/2);
    % Specify where the winding should start
    myind.winding.axi_start = [r_pillar+myind.pcb.spacing_hor; -core.PCB_Spacing_top-myind.pcb.thickness/2];

    %% Specify where the "air"-property should be placed
    % For planar, place "air" above the core
    myind.air_planar = [0; (myind.pcb.thickness/2+core.PCB_Spacing_top+h_top_planar)*1.5];
    % For axi, place air above the core
    myind.air_axi = [r_pillar/2; (myind.pcb.thickness/2+core.PCB_Spacing_top+h_top_axi)*1.5];


    %% Calculate rectangles for planar simulation
    % The core is symmetric, so only one half needs to be drawn. Then it
    % can be mirrored.
    % At the beginning, only the right half of a winding is drawn. Then
    % everything is mirrored to the left and moved right.
    
    % Draw the right half of the right coil
    myind.names_planar = ["Bot_Pillar_Right", "Bot_Winding_Right", "Pillar_Right", "Top_Pillar_Right", "Top_Winding_Right"];
    myind.rects_planar = [[0; -h_window_planar-h_bot_planar], [w_pillar_planar/2; -h_window_planar]];
    myind.rects_planar(:,:,2) = [[w_pillar_planar/2; -h_window_planar-h_bot_planar], [w_pillar_planar/2+w_window_planar; -h_window_planar]];
    if core.centerPillar
        myind.rects_planar(:,:,3) = [[0; -h_window_planar+core.gap_pillar/2], [w_pillar_planar/2; -core.gap_pillar/2]];
    else
        myind.rects_planar(:,:,3) = [[0; -h_window_planar], [w_pillar_planar/2; -core.gap_pillar]];
    end
    myind.rects_planar(:,:,4) = [[0; 0], [w_pillar_planar/2; h_top_planar]];
    myind.rects_planar(:,:,5) = [[w_pillar_planar/2; 0], [w_pillar_planar/2+w_window_planar; h_top_planar]];
    % Mirror everything to the left
    myind.rects_planar(:,:,6:10) = mirrorRects(myind.rects_planar, 'x');
    myind.names_planar(6:10) = ["Bot_Pillar_Left", "Bot_Winding_Left", "Pillar_Left", "Top_Pillar_Left", "Top_Winding_Left"];
    % Create the side (only on the right side):
    myind.names_planar(11) = "Side";
    myind.rects_planar(:,:,11) = [[w_pillar_planar/2+w_window_planar; -h_window_planar], [w_pillar_planar/2+w_window_planar+w_side_planar; -core.gap_side]];
    myind.names_planar(12) = "Top_Side";
    myind.rects_planar(:,:,12) = [[w_pillar_planar/2+w_window_planar; 0], [w_pillar_planar/2+w_window_planar+w_side_planar; h_top_planar]];
    myind.names_planar(13) = "Bot_Side";
    myind.rects_planar(:,:,13) = [[w_pillar_planar/2+w_window_planar; -h_window_planar-h_bot_planar], [w_pillar_planar/2+w_window_planar+w_side_planar; -h_window_planar]];
    % Move everthing to the right
    % Get the minimum x-coordinate and move by that (xmin will be negative)
    xmin = min(myind.rects_planar(1,:,:),[], "all");
    myind.rects_planar = moveRects(myind.rects_planar, -xmin, 0);
    % Move the starting x-coordinates
    myind.winding.planar_start(1,:) = myind.winding.planar_start(1,:) - xmin;
    % Mirror everything
    myind.rects_planar(:,:,14:26) = mirrorRects(myind.rects_planar, 'x');
    % Use mirrorRects to create the second starting coordinates even though
    % these are not rects
    % This needs to be done individually, because the order needs to be
    % flipped to stay l-r-l-r
    myind.winding.planar_start(:,3) = mirrorRects(myind.winding.planar_start(:,2), 'x');
    myind.winding.planar_start(:,4) = mirrorRects(myind.winding.planar_start(:,1), 'x');

    % Mirror the starting coordinates of the winding
    %myind.winding.planar_start(:,3:4) = myind.winding.planar_start;
    %myind.winding.planar_start(1,3:4) = -myind.winding.planar_start(1,3:4);

    %% Calculate rectangles for axisymmetric simulation
    % Height and width of the window stay the same, so that can be reused from
    % planar simulation
    myind.names_axi = ["Bot_Pillar", "Bot_Winding", "Pillar", "Top_Pillar", "Top_Winding", "Side", "Top_Side", "Bot_Side"];
    myind.rects_axi = [[0; -h_window_planar-h_bot_axi], [r_pillar; -h_window_planar]];
    myind.rects_axi(:,:,2) = [[r_pillar; -h_window_planar-h_bot_axi], [r_pillar+w_window_planar; -h_window_planar]];
    if isfield(core, 'centerPillar') && core.centerPillar
        myind.rects_axi(:,:,3) = [[0; -h_window_planar+core.gap_pillar/2], [r_pillar; -core.gap_pillar/2]];
    else
        myind.rects_axi(:,:,3) = [[0; -h_window_planar], [r_pillar; -core.gap_pillar]];
    end
    myind.rects_axi(:,:,4) = [[0; 0], [r_pillar; h_top_axi]];
    myind.rects_axi(:,:,5) = [[r_pillar; 0], [r_pillar+w_window_planar; h_top_axi]];
    myind.rects_axi(:,:,6) = [[r_pillar+w_window_planar; -h_window_planar], [r_total_axi; -core.gap_side]];
    myind.rects_axi(:,:,7) = [[r_pillar+w_window_planar; 0], [r_total_axi; h_top_axi]];
    myind.rects_axi(:,:,8) = [[r_pillar+w_window_planar; -h_window_planar-h_bot_axi], [r_total_axi; -h_window_planar]]; 
end