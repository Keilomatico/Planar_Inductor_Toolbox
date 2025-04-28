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

% This scripts reads all designs from the "data" folder and summarizes them in a nice table.
clc;
clear;
close all;

% Specify the column names that should be printed in the table. This needs
% to match with the creation of a row further down
mynames = ["description", "num", "A [mm^2]", "h [mm]", "V [mm^3]", "L_s_pln [nH]", "L_s_axi [nH]", "k", "fs [MHz]", "Pco_pln [W]", "Pco_axi [W]", "Hdc_max_pln [A/m]"];
% Specify the datatypes
varTypes = repmat({'double'},size(mynames));
varTypes(1) = {'string'};
% Create an empty table with the right names and types
rawtable = table('Size',[0 length(mynames)],'VariableTypes',varTypes,'VariableNames',mynames);

% Get all the filenames from the data directory
filenames = dir(simulationParameters().datafolder);
index = 1;
for i=1:length(filenames)
    % Check if filenames(i).name is actually a file. The first two entries 
    % are always . and .. so one could start i at 3 but this is safer
    if isfile(fullfile('data', filenames(i).name))
        % Clear old variables to make sure nothing is left
        clearvars -except rawtable filenames i index
        % Load the relevant data into the workspace
        myVars = {"mywinding","myind","result"};
        load(fullfile('data', filenames(i).name),"-mat",myVars{:});
        % Multiply area by 2 for single designs for a better comparability
        if myind.coupled==0
            area = myind.dimension.width*myind.dimension.depth*2;
        else
            area = myind.dimension.width*myind.dimension.depth;
        end
        % Create a new row
        rawtable(index,:) = {myind.description, ...
            mywinding, ...
            area, ...
            myind.dimension.height, ...
            area*myind.dimension.height, ...
            result(1).L_self*1e9, ...
            result(2).L_self*1e9, ...
            result(1).k,  ...
            result(1).fs/1e6, ...
            result(1).loss_copper, ...
            result(2).loss_copper, ...
            max(result(1).Hdc)};
        index = index+1;
    end
end
% Sort by some desired property, in this case copper loss
rawtable = sortrows(rawtable, find(strcmp(rawtable.Properties.VariableNames, 'Pcopper_planar'), 1), 'ascend');
disp(rawtable)
return