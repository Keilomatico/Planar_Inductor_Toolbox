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

function res = calcCapacitance(time, current, res, simParam)
    % Calculates the required capacitance to achieve a certain input and
    % output ripple based on the phase-current waveforms
    
    del = 1e-12;
    timestamps = [time(1), time(2), time(2)+del, time(3), time(3)+del, time(4), time(4)+del, time(5)];
    if simParam.D < 0.5
        i_in(1:2) = current.i1(1:2);
        i_in(3:4) = 0;
        i_in(5:6) = current.i2(3:4);
        i_in(7:8) = 0;
    else
        i_in(1:2) = current.i1(1:2)+current.i2(1:2);
        i_in(3:4) = current.i1(2:3);
        i_in(5:6) = current.i1(3:4)+current.i2(3:4);
        i_in(7:8) = current.i2(4:5);
    end 
    
    [time_interpol1, inChrg] = myintegral(timestamps, mymean(timestamps, i_in)-i_in);
    inChrg_ripple = max(inChrg)-min(inChrg);
    % C = Q / V
    res.Cin = inChrg_ripple / simParam.DeltaVinMax;
    fprintf("Iin,rms = %.1f \n", myrms(timestamps, i_in));

    iout = current.i1 + current.i2;
    [time_interpol2, outChrg] = myintegral(time, simParam.iout_avg-iout);
    outChrg_ripple = max(outChrg) - min(outChrg);
    res.Cout = outChrg_ripple / simParam.DeltaVoutMax;
    fprintf("Iout,rms = %.1f \n", myrms(time, iout));

    if simParam.SHOWPLOTS
        figure;
        subplot(2,1,1);
        hold on
        plot(timestamps*1e6, i_in, 'DisplayName', "I_{in}");
        plot(time*1e6, iout, 'DisplayName', "I_{out}");
        grid('on')
        xlabel("Time [us]")
        ylabel("Current [A]")
        legend('Location','northwest')
        
        subplot(2,1,2);
        hold on
        plot(time_interpol1*1e6, (inChrg-mean(inChrg))*1e6, 'DisplayName', "Q_{in}");
        plot(time_interpol2*1e6, (outChrg-mean(outChrg))*1e6, 'DisplayName', "Q_{out}");
        grid('on')
        xlabel("Time [us]")
        ylabel("Charge [uC]")
        legend('Location','northwest')
    end
end