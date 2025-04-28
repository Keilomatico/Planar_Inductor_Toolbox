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

function res = getInductanceAxi(myind, res, msg, simParam)
    % Determines the inductance for myind using an axisymmetric FEMM simulation
        
    openfemm;
    if simParam.MINIMIZE_FEMM
        main_minimize;
    end
    opendocument(char(myind.filename_axi+'.fem'));

    if ~(isfile(char(myind.filename_axi+'.ans')) && simParam.reuse_file)
        mi_analyze
    end
    mi_loadsolution

    % Analze results
    for i=1:myind.turns
        vals(i, :) = mo_getcircuitproperties(int2str(i));
    end

    % Analze results
    % Get the self inductance by dividing flux linkage by current
    % Due to rounding errors the value sometimes has a very small imaginary
    % component that needs to be removed
    res.L_self = real(sum(vals(:, 3))/vals(1, 1));
    res = res.calcTrafoModel();
    msg.print(2, sprintf('Simulated inductance axi: Lself=%.1f nH\n', res.L_self*1e9), simParam);
    
    closefemm;
end