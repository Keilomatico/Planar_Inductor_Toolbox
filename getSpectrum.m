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

function [amplitude, frequency] = getSpectrum(data, timestamps, N)
    % Computes an fft with N sampling points. Returns complex amplitude and frequency sorted by absolute amplitude

    % "Sample" the signal
    period = timestamps(end);
    f_sample = N/period;            % Sampling frequency
    time_interpol = 0:1/f_sample:timestamps(end)-1/f_sample;                 % Vector with sampling timestamps
    curr_interpol = interp1(timestamps, data, time_interpol);  % Vector with sampled data
    
    % Run FFT
    xk = fft(curr_interpol);
    % Adjust for one-sided amplitude FFT
    fft_two_amp = xk/N;   % Two sided amplitude
    if mod(N, 2) == 0   % Even number of samples -> Nyquist frequency exists as a bin
        amplitude = fft_two_amp(1:N/2+1);   % One-sided
        amplitude(2:end-1) = 2*amplitude(2:end-1);   % Double all values except 0 and nyquist
    else
        amplitude = fft_two_amp(1:ceil(N/2));      % One-sided
        amplitude(2:end) = 2*amplitude(2:end);   % Double all values except 0
    end
    frequency = f_sample/N*(0:(N/2));
end