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

function drawPlanarInductor(myind, simParam)
    % Draws the inductor for the planar simulation in FEMM and saves the
    % result in myind.filename_planar+'.fem'

    arguments
        myind Inductor
        simParam simulationParameters
    end

    if ~(isfile(char(myind.filename_planar+'.fem')) && simParam.reuse_file)
        openfemm;
        if simParam.MINIMIZE_FEMM
            main_minimize;
        end
        newdocument(0);
        mi_showgrid;
        
        %% Setup FEMM
        % Define the problem type.
        mi_probdef(simParam.target_fs, 'millimeters', 'planar', 1.e-8, myind.depth_planar, 30);
        
        % Add some material-properties
        mi_getmaterial('Air');
        mi_getmaterial('Copper');
        if simParam.USE_BHCURVE
            % Create the core material.
            % First, we create a material in the same way as if we 
            % were creating a linear material, except the values used for 
            % permeability are merely placeholders.
            mi_addmaterial('Core', 2100, 2100, 0, 0, 0, 0, 0, 1, 0, 0, 0);
        
            % Data which was extracted was in mT, so rescale to T
            mybhcurve = myind.material.bhcurve;
            mybhcurve(:,1) = mybhcurve(:,1)*1e-3;
        
            % Associate this BH curve with the Core material:
            mi_addbhpoints('Core', mybhcurve);
        else
            % Add a linear BH-Curve 
            mi_addmaterial('Core', myind.material.mu, myind.material.mu, 0, 0, 0, 0, 0, 1);
        end
        
        % Create parallel circuit properties for each turn
        % Because parallel windings cannot be associated with a negative
        % direction, we need a separate property for the part which is
        % entering and the part which is exiting (i.e. left of the pillar
        % and right of the pillar)
        for i=1:myind.turns
            mi_addcircprop(sprintf('Al%i', i), simParam.iout_avg/2, 0);
            mi_addcircprop(sprintf('Ar%i', i), -simParam.iout_avg/2, 0);
            % Turn B is only used for coupled inductors
            % For some reason there is an error when using zero current
            mi_addcircprop(sprintf('Bl%i', i), 0.0001, 0);
            mi_addcircprop(sprintf('Br%i', i), 0.0001, 0);
        end

        %% Draw the core and add block labels
        for i=1:length(myind.rects_planar)
            mi_drawrectangle(myind.rects_planar(:,1,i), myind.rects_planar(:,2,i));
            mi_addblocklabel(myind.centers_planar(:,i));     
            mi_selectlabel(myind.centers_planar(:,i));
            mi_setblockprop('Core', simParam.CORE_AUTOMESH, simParam.CORE_MESHSIZE,  '<None>', 0, 0, 0);
            mi_clearselected;
        end

        %% Add air-properties
        for i=1:size(myind.air_planar,2)
            mi_addblocklabel(myind.air_planar(1,i), myind.air_planar(2,i));
            mi_selectlabel(myind.air_planar(1,i), myind.air_planar(2,i));
            mi_setblockprop('Air', simParam.AIR_AUTOMESH, simParam.AIR_MESHSIZE,  '<None>', 0, 0, 0);
            mi_clearselected;
        end

        % Draw the windings
        myind.winding.function(myind, 'Al', myind.winding.planar_start(:,1), 'l', simParam)
        myind.winding.function(myind, 'Ar', myind.winding.planar_start(:,2), 'r', simParam)
        if myind.coupled < 0
            myind.winding.function(myind, 'Bl', myind.winding.planar_start(:,3), 'l', simParam)
            myind.winding.function(myind, 'Br', myind.winding.planar_start(:,4), 'r', simParam)
        elseif myind.coupled > 0
            myind.winding.function(myind, 'Br', myind.winding.planar_start(:,3), 'l', simParam)
            myind.winding.function(myind, 'Bl', myind.winding.planar_start(:,4), 'r', simParam)
        end

        % Make the Dirichlet Boundary at the end because for some reason this
        % speeds up the process a lot. Automatically zooms to natural at the end.
        mi_makeABC(3, max(abs(myind.rects_planar(1,:,:)),[], "all")*2,0,0,0);
        
        % Save the file
        mi_saveas(char(myind.filename_planar+'.fem'));
    
        closefemm;
    end
end

