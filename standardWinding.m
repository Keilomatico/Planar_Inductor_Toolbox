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

function standardWinding(myind, windingName, start, positionToCore, simParam)
    % Draws standard windings
    % windingName: Name of the circuit that shoud be used. A number is
    % automatically added depending on the turn
    % start: Coordinates where the winding starts: [startx; centery]
    % positionToCore: Either 'r' if it is on the right side of the core or
    % 'l' if it is on the left side of the core
    
    % Always draw from left to right
    if positionToCore == 'l'
        startx = start(1)-myind.winding.width;
    else
        startx = start(1);
    end
    % Start at the bottom of the pcb, then draw upwards
    posy = start(2) - myind.pcb.thickness/2;

    for i=1:myind.turns
        % Put the maximum number of layers in parallel. 
        % No interleaving here.
        parLayers = floor(myind.pcb.layers/myind.turns);
        for j=1:parLayers
            % Change the thickness for the outer layers
            if (i-1)*parLayers+j == 1 || (i-1)*parLayers+j == myind.pcb.layers
                thickness = myind.pcb.copper_thickness_outer;
            else
                thickness = myind.pcb.copper_thickness;
            end
            
            mi_drawrectangle(startx, posy, startx+myind.winding.width, posy+thickness);
            mi_addblocklabel(startx+myind.winding.width/2, posy+thickness/2);
            mi_selectlabel(startx+myind.winding.width/2, posy+thickness/2);
            mi_setblockprop('Copper', simParam.COPPER_AUTOMESH, simParam.COPPER_MESHSIZE, sprintf('%s%i', windingName, i), 0, 0, 1);
            mi_clearselected;

            posy = posy+thickness+myind.pcb.insulator_thickness;
        end
    end
end

