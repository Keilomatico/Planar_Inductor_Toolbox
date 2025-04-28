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

function res = getInductancePlanar(myind, res, msg, simParam)
    % Determines the inductance for myind using a planar FEMM simulation
        
    openfemm;
    if simParam.MINIMIZE_FEMM
        main_minimize;
    end
    opendocument(char(myind.filename_planar+'.fem'));

    if ~(isfile(char(myind.filename_planar+'.ans')) && simParam.reuse_file)
        mi_analyze
    end
    mi_loadsolution

    % Analze results
    for i=1:myind.turns
        valsAl(i, :) = mo_getcircuitproperties(sprintf('Al%i', i));
        valsAr(i, :) = mo_getcircuitproperties(sprintf('Ar%i', i));
        if ~(myind.coupled == 0)
            valsBl(i, :) = mo_getcircuitproperties(sprintf('Bl%i', i));
            valsBr(i, :) = mo_getcircuitproperties(sprintf('Br%i', i));
        end
    end
    
    % Get the self inductance by dividing flux linkage by current. 
    % All series turns have the same current, so no need to add them up.
    % Due to rounding errors the value sometimes has a very small imaginary
    % component that needs to be removed
    res.L_self = (sum(real(valsAl(:, 3)))-sum(real(valsAr(:, 3))))/valsAl(1, 1);     
    if ~(myind.coupled == 0)
        res.L_coupled = (sum(real(valsBl(:, 3)))-sum(real(valsBr(:, 3))))/valsAl(1, 1);
        % Not sure why this was put here 
        % if sign(winding(1)) ~= sign(winding(2))
        %    res.L_coupled = -res.L_coupled;
        %end
    else
        res.L_coupled = 0;
    end
    
    res.k = res.L_coupled/res.L_self;
    res=res.calcTrafoModel();
    
    msg.print(2, sprintf('Simulated inductance planar: Lself=%.1f nH, k=%.2f\n', res.L_self*1e9, res.k), simParam);
    msg.print(5, sprintf('L_mutual=%.1f nH; L_out=%.1f nH; L_m=%.1f nH\n',res.L_coupled*1e9, res.L_out*1e9, res.L_m*1e9), simParam);
    
    closefemm;
end