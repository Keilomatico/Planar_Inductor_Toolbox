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

% Specify which windings should be simulated
simDesign = 4;

% Create a new instance of the simulation parameters
simParam = simulationParameters();

%% Iterate over all windings specified in simWindings
for simCounter=1:length(simDesign)
    %% Prepare a fresh start
    clc;
    clearvars -except simCounter simDesign datafolder simParam
    close all;
    fclose('all');
    tic;

    % Get the current winding
    mywinding = simDesign(simCounter);

    % Create new inductor object with the design
    myind = designs(mywinding, simParam);

    % Define a new message object which is used to store all messages into a logfile and print messages to the console which are above a specified priority
    msg = Message(sprintf("%s/%s.txt", simParam.log_folder, myind.uniqueName));
    msg.print(1, sprintf("------------ %s ------------\n", myind.description), simParam);
    msg.print(1, sprintf("simDesign=%i\n", mywinding), simParam);

    %% Draw the inductor and get the inductance
    % For coupled designs, the inductance is always determined from
    % planar simulation because axisymmetric cannot reflect coupling
    % (except for designs with both windigs on one limb but that is 
    % too special to make an exception)
    if simParam.SIMULATIONS(1) == 1 || ~(myind.coupled == 0)
        % Prepare a result object
        result(1) = Result();
        drawPlanarInductor(myind, simParam);
        result(1) = getInductancePlanar(myind, result(1), msg, simParam);
    end

    %% Draw the axisymmetric inductor if the user wants to do an axisymmetric simulation
    if simParam.SIMULATIONS(2) == 1
        drawAxisymmetricInductor(myind, simParam);
        % Reuse the contents of result(1) and only modify L_self
        % The reason is, that the other parameters cannot be determined
        % from axisymmetric simulation for coupled inductors
        if simParam.SIMULATIONS(1) == 1 || ~(myind.coupled == 0)
            result(2) = result(1);
        else
            result(2) = Result();
            result(2).k = 0;
            result(2).L_coupled = 0;
        end
        result(2) = getInductanceAxi(myind, result(2), msg, simParam);
    end

    %% Main simulation loop
    for simnum=1:2
        if simParam.SIMULATIONS(simnum) == 1
            if simnum == 1
                msg.print(1, sprintf("------ Planar Simulation ------\n"), simParam);
            else
                msg.print(1, sprintf("\n------ Axisymmetric Simulation ------\n"), simParam);
            end

            %% Calculate the required frequency for soft-switching
            % Approximate the required negative current from the desired dead time
            Ineg = simParam.Vin*simParam.Cds/simParam.deadTime;
            leg_ripple = 2*simParam.iout_avg/2+2*Ineg;
        
            % Calculate the switching frequency to achieve the negative current
            if simParam.D < 0.5
                result(simnum).fs = simParam.Vin*simParam.D/(2*result(simnum).L_self*leg_ripple) * (2/(1+result(simnum).k)*(0.5-simParam.D)+1/(1-result(simnum).k));
            else
                result(simnum).fs = simParam.Vin*Ts*(1-simParam.D)/(2*result(simnum).L_self*leg_ripple) * (2/(1+result(simnum).k)*(simParam.D-0.5)+1/(1-result(simnum).k));
            end
            msg.print(2, sprintf("fs = %.2f MHz\n", result(simnum).fs*1e-6), simParam);
            %result(simnum).fs = 2e6;
            %msg.print(2, sprintf("fs overwritten to %.2f MHz\n", result(simnum).fs*1e-6), simParam);
        
            %% Get the waveform
            [current, time] = getWaveformMath(simParam, result(simnum).fs, result(simnum));
            if simParam.SHOWPLOTS
                figure;
                hold on
                plot(time, current.i1, 'DisplayName', 'I_1')
                plot(time, current.i2, 'DisplayName', 'I_2')
                hold off
                grid('on')
                xlabel("Time [s]")
                ylabel("Current [A]")
                legend('Location','northwest')
                xlim([0, 1/result(simnum).fs]);
            end
        
            %% Calculate required input and output capacitance
            if simParam.CALC_CAP
                result(simnum) = calcCapacitance(time, current, result(simnum), simParam);
                msg.print(2, sprintf("Required input capacitance: %.1f uF\n", result(simnum).Cin*1e6), simParam);
                msg.print(2, sprintf("Required output capacitance: %.1f uF\n", result(simnum).Cout*1e6), simParam);
            end
        
            %% MOSFET conduction-loss
            result(simnum).conduction_loss = simParam.Rds_on * myrms(time, current.i1)^2 * 2;    % *2 because of two legs
            msg.print(1, sprintf("Transistor conduction loss: %.1fW\n", result(simnum).conduction_loss), simParam);
    
            %% Perform an FFT of the current and analyze the largest harmonics
            % Get Spectrum of the current
            [amplitude_1, f] = getSpectrum(current.i1, time, 100);
            [amplitude_2, ~] = getSpectrum(current.i2, time, 100);
        
            % Sort spectrum by amplitude
            % Currents are identical, just phase-shifted so they contain the same
            % absolute frequency components. Therefore both calls to sortData return
            % the same order of frequencies.
            [amp1_sorted, f_sorted] = sortData(amplitude_1, f);
            [amp2_sorted, ~] = sortData(amplitude_2, f);
        
            % Initialize some variables depending on which simulation is
            % currently running
            if simnum==1
                areaCenters = myind.centers_planar;
                areaNames = myind.names_planar;
                rawFile = myind.filename_planar;
            elseif simnum==2
                areaCenters = myind.centers_axi;
                areaNames = myind.names_axi;
                rawFile = myind.filename_axi;
            end
    
            % Initialize the waveform variables
            time_interpol = linspace(0, time(end), 1000);
            result(simnum).bx_waveform = zeros(length(areaCenters), length(time_interpol));
            result(simnum).by_waveform = zeros(length(areaCenters), length(time_interpol));
            % Index of the DC simulation
            dc_index = -1;
            % Analyze the larges NUM_HARMONICS harmonics plus DC
            for harmonic = 1:simParam.NUM_HARMONICS+1
                % If the amplitude of the harmonic is much smaller than the
                % biggest one, break
                if abs(amp1_sorted(harmonic)) < abs(simParam.HARMONIC_FACTOR*amp1_sorted(1))
                    break;
                end

                % Create/open a simulation file for the current frequency
                openfemm;
                if simParam.MINIMIZE_FEMM
                    main_minimize;
                end
                freqfile = sprintf("%s_f%.2fMHz", rawFile, f_sorted(harmonic)/1e6);
    
                if isfile(char(freqfile+'.fem')) && simParam.reuse_file
                    opendocument(char(freqfile+'.fem'));
                else
                    % Adjust the current
                    opendocument(char(rawFile+'.fem'));
                    if simnum==1
                        mi_probdef(f_sorted(harmonic), 'millimeters', 'planar', 1.e-8,  myind.depth_planar, 30);
                        for idx=1:myind.turns
                            mi_setcurrent(sprintf('Al%i', idx), amp1_sorted(harmonic))
                            mi_setcurrent(sprintf('Ar%i', idx), -amp1_sorted(harmonic))
                            if ~(myind.coupled==0)
                                mi_setcurrent(sprintf('Bl%i', idx), amp2_sorted(harmonic))
                                mi_setcurrent(sprintf('Br%i', idx), -amp2_sorted(harmonic))
                            end
                        end  
                    elseif simnum==2
                        mi_probdef(f_sorted(harmonic), 'millimeters', 'axi', 1.e-8, 0, 30);
                        for idx=1:myind.turns
                            mi_setcurrent(int2str(idx), amp1_sorted(harmonic));
                        end
                    end
                    mi_saveas(char(freqfile+'.fem'));
                end
                if isfile(char(freqfile+'.ans')) == 0 || simParam.reuse_file == 0
                    mi_analyze
                end
                mi_loadsolution
            
                % Because the frequencies are sorted by amplitude, the
                % first one isn't necessarily DC, so this variable
                % indicates when a simulation is DC
                isDC = 0;
                if simnum==1
                    % Get Copperloss (lossA is identical to lossB)
                    for idx=1:myind.turns
                        valsAl(idx, :) = mo_getcircuitproperties(sprintf('Al%i', idx));
                        valsAr(idx, :) = mo_getcircuitproperties(sprintf('Ar%i', idx));
                    end
                    % Calculate the loss differently for DC
                    if imag(valsAl(1, 1)) == 0
                        isDC = 1;
                        result(simnum).loss_copper_harmonic(harmonic) = (sum(valsAl(:, 2))-sum(valsAr(:, 2)))*valsAl(1, 1);
                    else
                        result(simnum).loss_copper_harmonic(harmonic) = real(0.5*(sum(valsAl(:, 2))-sum(valsAr(:, 2)))*conj(valsAl(1, 1)));
                    end
                    % Add to total loss
                    result(simnum).loss_copper = result(simnum).loss_copper + result(simnum).loss_copper_harmonic(harmonic);
                elseif simnum==2
                    % Get Copperloss
                    for idx=1:myind.turns
                        vals(idx, :) = mo_getcircuitproperties(int2str(idx));
                    end
                    % Calculate the loss differently for DC
                    if imag(vals(1, 1)) == 0
                        isDC = 1;
                        result(simnum).loss_copper_harmonic(harmonic) = sum(vals(:, 2))*vals(1, 1);
                    else
                        result(simnum).loss_copper_harmonic(harmonic) = real(0.5*sum(vals(:, 2))*conj(vals(1, 1)));
                    end
                    % Add to total loss
                    result(simnum).loss_copper = result(simnum).loss_copper + result(simnum).loss_copper_harmonic(harmonic);
                end
            
                % Get the flux-density from each area
                % Only check the areas that have a name because for 
                % symmetrical designs, not all areas need to be checked
                for i=1:length(areaNames)
                    mo_selectblock(areaCenters(1, i), areaCenters(2, i))
                    vol(i) = mo_blockintegral(10);
                    % Get the average flux densities
                    bx = mo_blockintegral(8)/vol(i);
                    by = mo_blockintegral(9)/vol(i);
                    mo_clearblock;
            
                    % Add the time-domain waveform of the current frequency
                    % to the overall waveform (stored independently for each area)
                    result(simnum).bx_waveform(i, :) = result(simnum).bx_waveform(i, :) + real(bx)*cos(2*pi*f_sorted(harmonic)*time_interpol) + imag(bx)*sin(2*pi*f_sorted(harmonic)*time_interpol);
                    result(simnum).by_waveform(i, :) = result(simnum).by_waveform(i, :) + real(by)*cos(2*pi*f_sorted(harmonic)*time_interpol) + imag(by)*sin(2*pi*f_sorted(harmonic)*time_interpol);
                    % Get Hdc
                    if isDC
                        % Save dc_index for later
                        dc_index = harmonic;
                        result(simnum).Hdc(i) = sqrt(bx^2+by^2) / (simParam.mu0*myind.material.mu);
                        msg.print(5, sprintf("Hdc %s: %.1f A/m\n", areaNames(i), result(simnum).Hdc(i)), simParam);
                    end
                end
                closefemm;   
            end

            % Multiply total copper loss by two for the two coils
            result(simnum).loss_copper = result(simnum).loss_copper*2;
            msg.print(0, sprintf("Copper Loss: %.1f W\n", result(simnum).loss_copper), simParam);
            % Calculate DC-resistance 
            if dc_index >= 0
                res_dc = result(simnum).loss_copper_harmonic(dc_index) / (simParam.iout_avg/2)^2;
            else
                res_dc = 0;
            end
            % Compare the loss with the loss that would occur for a
            % constant resistivity
            loss_const = res_dc * (myrms(time, current.i1)^2 + myrms(time, current.i2)^2);
            msg.print(1, sprintf("Increase in resisitivy: %.0f %% \n", 100*(result(simnum).loss_copper/loss_const-1)), simParam);
    
            % Compute the loss-density for each area using iGSE
            result(simnum).loss_core = 0;
            msg.print(3, sprintf("Loss densities [mW/cm^3]: \n"), simParam);
            if simParam.SHOWPLOTS
                figure;
                hold on
            end
            for i=1:length(areaNames)
                % Calculate loss in x and y direction independently
                result(simnum).bx_waveform(i, end) = result(simnum).bx_waveform(i, 1);    % Somehow needed for the coreloss script to work
                result(simnum).by_waveform(i, end) = result(simnum).by_waveform(i, 1);    % Somehow needed for the coreloss script to work
                % loss density in mW/cm^3 = kW/m^3
                result(simnum).loss_core_area(i) = corelossSullivan(time_interpol, result(simnum).bx_waveform(i, :), myind.material, 1) + ...
                    corelossSullivan(time_interpol, result(simnum).by_waveform(i, :), myind.material, 1);
                msg.print(5, sprintf("    %s: %.0f mW/cm^3\n", areaNames(i), result(simnum).loss_core_area(i)), simParam);
                % Total loss in W
                result(simnum).loss_core = result(simnum).loss_core+result(simnum).loss_core_area(i)*vol(i)*1e3;
                % Max flux
                babs_waveform = sqrt(result(simnum).bx_waveform(i, :).^2+result(simnum).by_waveform(i, :).^2);
                % Calculate using standard Steinmetz:
                %result(simnum).loss_core_area(i) = myind.material.k * result(simnum).fs^myind.material.fexp * max(babs_waveform)^myind.material.bexp;
                %msg.print(2, sprintf("    %s: %.0f mT\n", areaNames(i), max(abs(babs_waveform))*1e3), simParam);
                if simParam.SHOWPLOTS
                    %plot(time_interpol*1e6, babs_waveform*1e3, 'DisplayName', areaNames(i))
                    plot(time_interpol*1e6, result(simnum).bx_waveform(i, :)*1e3, 'DisplayName', areaNames(i))
                end
            end
            if simParam.SHOWPLOTS
                hold off
                grid('on')
                xlabel("Time [us]")
                ylabel("Flux-Density [mT]")
                legend('Location','northwest')
                xlim([0, time_interpol(end)*1e6]);
            end

            % Export the results in a nice sorted table which is much easier to
            % read than the normal print
            myPtable = table(areaNames', result(simnum).loss_core_area(1:length(areaNames))');
            myPtable = sortrows(myPtable,2,'descend');
            disp(array2table(table2array(myPtable(:,2))',"VariableNames",table2array(myPtable(:,1))'))
            if dc_index >= 0
                fprintf("Hdc [A/m]: \n");
                myHtable = table(areaNames', result(simnum).Hdc');
                myHtable = sortrows(myHtable,2,'descend');
                disp(array2table(table2array(myHtable(:,2))',"VariableNames",table2array(myHtable(:,1))'))
            end

            % Multiply overall core loss depending on the amout of symmetry
            if simnum == 1
                result(simnum).loss_core = result(simnum).loss_core * (sum(myind.symm)+1);
                if myind.coupled
                    result(simnum).loss_core = result(simnum).loss_core * 2;
                end
            else
                % For axisymmetric simulation, only the y-direction matters
                % *2 because only one core is simulated
                result(simnum).loss_core = result(simnum).loss_core * 2 * (myind.symm(2)+1);
            end
            msg.print(0, sprintf("Core Loss: %.1f W\n", result(simnum).loss_core), simParam);
    
            % Total loss
            result(simnum).loss_total = result(simnum).loss_core + result(simnum).loss_copper + result(simnum).conduction_loss;
            msg.print(0, sprintf("Total Loss: %.2fW\n", result(simnum).loss_total), simParam);
            msg.print(0, sprintf("Total Efficiency: %.2f %%\n", (1-result(simnum).loss_total/simParam.pout)*100), simParam);
        end
    end

    % Save all the data
    save(sprintf("%s/%s.mat", simParam.datafolder, myind.description));

    % Finish
    elapsedTime = toc;
    msg.print(0, sprintf("\n\n--------------------Finished in %.0f s--------------------\n", elapsedTime), simParam);

    % Open FEMM again and show the flux-density of the fundamental
    if simParam.SHOWDESIGN
        if simParam.SIMULATIONS(1)
            myind.showDesign(result, 1, 1, 'mag', 50e-3);
        else
            myind.showDesign(result, 2, 1, 'mag', 50e-3);
        end
    end

    % Delete the msg handle to close the logfile (might not be necessary but doesn't hurt)
    delete(msg)

    % Close all files that may still be open
    fclose('all');
end

% Losses per area (absolute)
loss_core_area_absolute = result(1).loss_core_area .* vol * 1e3;
loss_core_area_absolute = loss_core_area_absolute * (sum(myind.symm)+1);
% This is too much I think because core isn't mirrored anymore
%if myind.coupled
%    result(simnum).loss_core = result(simnum).loss_core * 2;
%end

% Logical index for Bot_ areas
idxBot = startsWith(areaNames, "Bot_");
% Logical index for exact match with "Side"
idxSide = (areaNames == "Side");
% Combine conditions
idxSelected = idxBot | idxSide;
% Sum the corresponding losses
totalBotLoss = sum(loss_core_area_absolute(idxSelected));
% Display result
fprintf('U-Corepiece loss (Bot): %.2f W \n', totalBotLoss);
totalTopLoss = sum(loss_core_area_absolute(startsWith(areaNames, "Top_")));
fprintf('I-Corepiece loss (Top): %.2f W \n', totalTopLoss);
totalPillarLoss = sum(loss_core_area_absolute(startsWith(areaNames, "Pillar_")));
fprintf('Pillar loss (both): %.2f W \n', totalPillarLoss);