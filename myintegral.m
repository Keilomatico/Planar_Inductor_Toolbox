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

% Calculates the curve of integrating ydata with datapoints at times specified in
% time. The distance between elements does not need to be constant.
function [x, y] = myintegral(time, ydata)
    x = linspace(time(1), time(end), 1001);
    y = zeros(length(x),1);
    % Iterate over the array and integrate the the waveform. 
    j = 1;
    init = 0;
    for i = 1:(length(time)-1)
        while(j<=length(x) && x(j) <= time(i+1))
            if time(i+1)-time(i) == 0
                y(j) = 0;
            else
                y(j) = 0.5*(ydata(i+1)-ydata(i))/(time(i+1)-time(i))*(x(j)-time(i))^2+ydata(i)*(x(j)-time(i))+init;
            end
            j = j+1;
        end
        init = y(j-1);
    end
end