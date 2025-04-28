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

% Calculates the rms value of ydata with datapoints at times specified in
% time. The distance between elements does not need to be constant as
% opposed to the built_in rms function
function result = myrms(time, ydata)
    sum = 0;
    % Iterate over the array and integrate the square of the waveform. 
    % See report for a detailed explanation.
    for i = 1:(length(time)-1)
        dt = time(i+1)-time(i);
        % This if is necessary to avoid a division by zero in case of a
        % constant waveform.
        if ydata(i+1)-ydata(i) ~= 0
            sum = sum + 1/3 * dt / (ydata(i+1)-ydata(i)) * (ydata(i+1)^3-ydata(i)^3);
        end
    end

    % Compute the duration of the interval
    T = time(length(time)) - time(1);

    % Compute the rms value
    result = sqrt(sum/T);
end