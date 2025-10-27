# This file is part of the Planar Inductor Toolbox
# Copyright (C) 2025 Adrian Keil
# 
# The Planar Inductor Toolbox is free software: you can redistribute it 
# and/or modify it under the terms of the GNU General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
# 
# The Planar Inductor Toolbox is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  
# If not, see https://www.gnu.org/licenses/gpl-3.0.html

import numpy as np
import time
import os
from pathlib import Path
import femm
import pickle
import pandas as pd

# Import the required modules (these need to be created/converted from MATLAB)
from simulationParameters import SimulationParameters
from designs import designs
from Message import Message
from Result import Result
from drawPlanarInductor import drawPlanarInductor
from drawAxisymmetricInductor import drawAxisymmetricInductor
from getInductancePlanar import getInductancePlanar
from getInductanceAxi import getInductanceAxi
from helperFunctions import getWaveformMath, calcCapacitance, myrms, getSpectrum, sortData, displayLossDensityTable, plotFluxDensityComponent
from corelossSullivan import corelossSullivan

# Specify which windings should be simulated
simDesign = [4]

# Create a new instance of the simulation parameters
simParam = SimulationParameters()

## Iterate over all windings specified in simWindings
for simCounter in range(len(simDesign)):
    ## Prepare a fresh start
    # Note: Python doesn't need explicit variable clearing like MATLAB
    # Variables are automatically garbage collected
    start_time = time.time()

    # Get the current winding
    mywinding = simDesign[simCounter]

    # Create new inductor object with the design
    myind = designs(mywinding, simParam)

    # Define a new message object which is used to store all messages into a logfile and print messages to the console which are above a specified priority
    msg = Message(f"{simParam.log_folder}/{myind.uniqueName}.txt")
    msg.print_msg(1, f"------------ {myind.description} ------------\n", simParam)
    msg.print_msg(1, f"simDesign={mywinding}\n", simParam)

    ## Draw the inductor and get the inductance
    # For coupled designs, the inductance is always determined from
    # planar simulation because axisymmetric cannot reflect coupling
    # (except for designs with both windigs on one limb but that is 
    # too special to make an exception)
    result = [None, None]  # result[0] for planar, result[1] for axi
    
    if simParam.SIMULATIONS[0] == 1 or not (myind.coupled == 0):
        # Prepare a result object
        result[0] = Result()
        drawPlanarInductor(myind, simParam)
        msg.print_msg(5, f"Saved to: {myind.filename_planar}.fem\n", simParam)
        result[0] = getInductancePlanar(myind, result[0], msg, simParam)

    ## Draw the axisymmetric inductor if the user wants to do an axisymmetric simulation
    if simParam.SIMULATIONS[1] == 1:
        drawAxisymmetricInductor(myind, simParam)
        msg.print_msg(5, f"Saved to: {myind.filename_axi}.fem\n", simParam)
        # Reuse the contents of result[0] and only modify L_self
        # The reason is, that the other parameters cannot be determined
        # from axisymmetric simulation for coupled inductors
        if simParam.SIMULATIONS[0] == 1 or not (myind.coupled == 0):
            result[1] = Result()
            # Copy relevant attributes from result[0]
            result[1].__dict__.update(result[0].__dict__)
        else:
            result[1] = Result()
            result[1].k = 0
            result[1].L_coupled = 0
        result[1] = getInductanceAxi(myind, result[1], msg, simParam)

    ## Main simulation loop
    for simnum in range(2):  # 0 for planar, 1 for axi
        if simParam.SIMULATIONS[simnum] == 1:
            if simnum == 0:
                msg.print_msg(1, "------ Planar Simulation ------\n", simParam)
            else:
                msg.print_msg(1, "\n------ Axisymmetric Simulation ------\n", simParam)

            ## Calculate the required frequency for soft-switching
            # Approximate the required negative current from the desired dead time
            Ineg = simParam.Vin * simParam.Cds / simParam.deadTime
            leg_ripple = 2 * simParam.iout_avg / 2 + 2 * Ineg
        
            # Calculate the switching frequency to achieve the negative current
            if simParam.D < 0.5:
                result[simnum].fs = float(simParam.Vin * simParam.D / (2 * result[simnum].L_self * leg_ripple) * \
                    (2 / (1 + result[simnum].k) * (0.5 - simParam.D) + 1 / (1 - result[simnum].k)))
            else:
                result[simnum].fs = float(simParam.Vin * simParam.Ts * (1 - simParam.D) / (2 * result[simnum].L_self * leg_ripple) * \
                    (2 / (1 + result[simnum].k) * (simParam.D - 0.5) + 1 / (1 - result[simnum].k)))
            msg.print_msg(2, f"fs = {result[simnum].fs*1e-6:.2f} MHz\n", simParam)
        
            ## Get the waveform
            current, time_array = getWaveformMath(simParam, result[simnum].fs, result[simnum])
            if simParam.SHOWPLOTS:
                import matplotlib.pyplot as plt
                plt.figure()
                plt.plot(time_array, current['i1'], label='I_1')
                plt.plot(time_array, current['i2'], label='I_2')
                plt.grid(True)
                plt.xlabel("Time [s]")
                plt.ylabel("Current [A]")
                plt.legend(loc='upper left')
                plt.xlim([0, 1/result[simnum].fs])
                plt.show()
        
            ## Calculate required input and output capacitance
            if simParam.CALC_CAP:
                result[simnum] = calcCapacitance(time_array, current, result[simnum], simParam)
                msg.print_msg(2, f"Required input capacitance: {result[simnum].Cin*1e6:.1f} uF\n", simParam)
                msg.print_msg(2, f"Required output capacitance: {result[simnum].Cout*1e6:.1f} uF\n", simParam)
        
            ## MOSFET conduction-loss
            result[simnum].conduction_loss = simParam.Rds_on * myrms(time_array, current['i1'])**2 * 2    # *2 because of two legs
            msg.print_msg(1, f"Transistor conduction loss: {result[simnum].conduction_loss:.1f}W\n", simParam)
    
            ## Perform an FFT of the current and analyze the largest harmonics
            # Get Spectrum of the current
            amplitude_1, f = getSpectrum(current['i1'], time_array, 100)
            amplitude_2, _ = getSpectrum(current['i2'], time_array, 100)
        
            # Sort spectrum by amplitude
            # Currents are identical, just phase-shifted so they contain the same
            # absolute frequency components. Therefore both calls to sortData return
            # the same order of frequencies.
            amp1_sorted, f_sorted = sortData(amplitude_1, f)
            amp2_sorted, _ = sortData(amplitude_2, f)
        
            # Initialize some variables depending on which simulation is
            # currently running
            if simnum == 0:
                areaCenters = myind.centers_planar
                areaNames = myind.names_planar
                rawFile = myind.filename_planar
            elif simnum == 1:
                areaCenters = myind.centers_axi
                areaNames = myind.names_axi
                rawFile = myind.filename_axi
    
            # Initialize the waveform variables
            time_interpol = np.linspace(0, time_array[-1], 1000)
            result[simnum].bx_waveform = np.zeros((len(areaCenters[0]), len(time_interpol)))
            result[simnum].by_waveform = np.zeros((len(areaCenters[0]), len(time_interpol)))
            
            # Initialize loss arrays
            result[simnum].loss_copper = 0
            result[simnum].loss_copper_harmonic = []
            result[simnum].Hdc = np.zeros(len(areaCenters[0]))
            result[simnum].loss_core_area = np.zeros(len(areaNames))
            
            # Analyze the larges NUM_HARMONICS harmonics plus DC
            for harmonic in range(simParam.NUM_HARMONICS + 1):
                # If the amplitude of the harmonic is much smaller than the
                # biggest one, break
                if abs(amp1_sorted[harmonic]) < abs(simParam.HARMONIC_FACTOR * amp1_sorted[0]):
                    break

                # Create/open a simulation file for the current frequency
                femm.openfemm(simParam.HIDE_FEMM)
                if simParam.MINIMIZE_FEMM:
                    femm.main_minimize()
                freqfile = f"{rawFile}_f{f_sorted[harmonic]/1e6:.2f}MHz"
    
                if os.path.isfile(f"{freqfile}.fem") and simParam.reuse_file:
                    femm.opendocument(f"{freqfile}.fem")
                else:
                    # Adjust the current
                    femm.opendocument(f"{rawFile}.fem")
                    if simnum == 0:
                        femm.mi_probdef(f_sorted[harmonic], 'millimeters', 'planar', 1.e-8, myind.depth_planar, 30)
                        for idx in range(myind.turns):
                            femm.mi_setcurrent(f'Al{idx+1}', amp1_sorted[harmonic])
                            femm.mi_setcurrent(f'Ar{idx+1}', -amp1_sorted[harmonic])
                            if not (myind.coupled == 0):
                                femm.mi_setcurrent(f'Bl{idx+1}', amp2_sorted[harmonic])
                                femm.mi_setcurrent(f'Br{idx+1}', -amp2_sorted[harmonic])
                    elif simnum == 1:
                        femm.mi_probdef(f_sorted[harmonic], 'millimeters', 'axi', 1.e-8, 0, 30)
                        for idx in range(myind.turns):
                            femm.mi_setcurrent(str(idx+1), amp1_sorted[harmonic])
                    femm.mi_saveas(f"{freqfile}.fem")
                    
                if not os.path.isfile(f"{freqfile}.ans") or simParam.reuse_file == 0:
                    femm.mi_analyze()
                femm.mi_loadsolution()
            
                # Because the frequencies are sorted by amplitude, the
                # first one isn't necessarily DC, so this variable
                # indicates when a simulation is DC
                isDC = 0
                if simnum == 0:
                    # Get Copperloss (lossA is identical to lossB)
                    valsAl = np.zeros((myind.turns, 3), dtype=complex)
                    valsAr = np.zeros((myind.turns, 3), dtype=complex)
                    for idx in range(myind.turns):
                        valsAl[idx, :] = femm.mo_getcircuitproperties(f'Al{idx+1}')
                        valsAr[idx, :] = femm.mo_getcircuitproperties(f'Ar{idx+1}')
                    # Calculate the loss differently for DC
                    if np.imag(valsAl[0, 0]) == 0:
                        isDC = 1
                        loss_harmonic = float(np.real((np.sum(valsAl[:, 1]) - np.sum(valsAr[:, 1])) * valsAl[0, 0]))
                    else:
                        loss_harmonic = float(np.real(0.5 * (np.sum(valsAl[:, 1]) - np.sum(valsAr[:, 1])) * np.conj(valsAl[0, 0])))
                    result[simnum].loss_copper_harmonic.append(loss_harmonic)
                    # Add to total loss
                    result[simnum].loss_copper = result[simnum].loss_copper + loss_harmonic
                elif simnum == 1:
                    # Get Copperloss
                    vals = np.zeros((myind.turns, 3), dtype=complex)
                    for idx in range(myind.turns):
                        vals[idx, :] = femm.mo_getcircuitproperties(str(idx+1))
                    # Calculate the loss differently for DC
                    if np.imag(vals[0, 0]) == 0:
                        isDC = 1
                        loss_harmonic = float(np.real(np.sum(vals[:, 1]) * vals[0, 0]))
                    else:
                        loss_harmonic = float(np.real(0.5 * np.sum(vals[:, 1]) * np.conj(vals[0, 0])))
                    result[simnum].loss_copper_harmonic.append(loss_harmonic)
                    # Add to total loss
                    result[simnum].loss_copper = result[simnum].loss_copper + loss_harmonic
            
                # Get the flux-density from each area
                # Only check the areas that have a name because for 
                # symmetrical designs, not all areas need to be checked
                vol = np.zeros(len(areaNames))
                for i in range(len(areaNames)):
                    femm.mo_selectblock(areaCenters[0, i], areaCenters[1, i])
                    vol[i] = femm.mo_blockintegral(10)
                    # Get the average flux densities
                    bx = femm.mo_blockintegral(8) / vol[i]
                    by = femm.mo_blockintegral(9) / vol[i]
                    femm.mo_clearblock()
            
                    # Add the time-domain waveform of the current frequency
                    # to the overall waveform (stored independently for each area)
                    result[simnum].bx_waveform[i, :] = np.real(result[simnum].bx_waveform[i, :] + 
                        bx.real * np.cos(2 * np.pi * f_sorted[harmonic] * time_interpol) + 
                        bx.imag * np.sin(2 * np.pi * f_sorted[harmonic] * time_interpol))
                    result[simnum].by_waveform[i, :] = np.real(result[simnum].by_waveform[i, :] + 
                        by.real * np.cos(2 * np.pi * f_sorted[harmonic] * time_interpol) + 
                        by.imag * np.sin(2 * np.pi * f_sorted[harmonic] * time_interpol))
                    # Get Hdc
                    if isDC:
                        # Save dc_index for later
                        dc_index = harmonic
                        result[simnum].Hdc[i] = float(np.real(np.sqrt(bx**2 + by**2) / (simParam.mu0 * myind.material.mu)))
                        msg.print_msg(5, f"Hdc {areaNames[i]}: {result[simnum].Hdc[i]:.1f} A/m\n", simParam)
                femm.closefemm()

            # Multiply total copper loss by two for the two coils
            result[simnum].loss_copper = result[simnum].loss_copper * 2
            msg.print_msg(0, f"Copper Loss: {result[simnum].loss_copper:.1f} W\n", simParam)
            # Calculate DC-resistance 
            res_dc = result[simnum].loss_copper_harmonic[dc_index] / (simParam.iout_avg / 2)**2
            # Compare the loss with the loss that would occur for a
            # constant resistivity
            loss_const = res_dc * (myrms(time_array, current['i1'])**2 + myrms(time_array, current['i2'])**2)
            msg.print_msg(1, f"Increase in resisitivy: {100*(result[simnum].loss_copper/loss_const-1):.0f} % \n", simParam)
    
            # Compute the loss-density for each area using iGSE
            result[simnum].loss_core = 0
            for i in range(len(areaNames)):
                # Calculate loss in x and y direction independently
                result[simnum].bx_waveform[i, -1] = result[simnum].bx_waveform[i, 0]    # Somehow needed for the coreloss script to work
                result[simnum].by_waveform[i, -1] = result[simnum].by_waveform[i, 0]    # Somehow needed for the coreloss script to work
                # loss density in mW/cm^3 = kW/m^3
                result[simnum].loss_core_area[i] = corelossSullivan(time_interpol, result[simnum].bx_waveform[i, :], myind.material, 1) + \
                    corelossSullivan(time_interpol, result[simnum].by_waveform[i, :], myind.material, 1)
                msg.print_msg(5, f"    {areaNames[i]}: {result[simnum].loss_core_area[i]:.0f} mW/cm^3\n", simParam)
                # Total loss in W
                result[simnum].loss_core = result[simnum].loss_core + result[simnum].loss_core_area[i] * vol[i] * 1e3
                
            # Display the loss densities and Hdc values in a table
            displayLossDensityTable(areaNames, result[simnum].loss_core_area, result[simnum].Hdc, vol, simnum)
            
            # Plot Bx and By waveforms for each area
            if simParam.SHOWPLOTS:
                plotFluxDensityComponent(areaNames, result[simnum].bx_waveform, time_interpol, 'Bx', simnum)
                plotFluxDensityComponent(areaNames, result[simnum].by_waveform, time_interpol, 'By', simnum)
            
            # Sum losses for different parts as indicated by their by prefix (before first underscore)
            if simnum == 0:
                part_losses = {}
                for i in range(len(areaNames)):
                    # Extract part (everything before the first underscore)
                    part = areaNames[i].split('_')[0] if '_' in areaNames[i] else areaNames[i]
                    # Calculate total loss for this area in mW
                    # Multiply by the number of symmetry axis *2
                    area_loss = result[simnum].loss_core_area[i] * vol[i] * (np.sum(myind.symm)+1) * 1e6
                    # Add to part sum
                    if part in part_losses:
                        part_losses[part] += area_loss
                    else:
                        part_losses[part] = area_loss
                
                # Print summed losses by part
                msg.print_msg(1, "Core loss by region [mW]:\n", simParam)
                for part in sorted(part_losses.keys(), key=lambda x: part_losses[x], reverse=True):
                    msg.print_msg(1, f"  {part}: {part_losses[part]:.1f} mW\n", simParam)

            # Multiply overall core loss depending on the amout of symmetry
            if simnum == 0:
                result[simnum].loss_core = result[simnum].loss_core * (np.sum(myind.symm) + 1)
                if myind.coupled:
                    result[simnum].loss_core = result[simnum].loss_core * 2
            else:
                # For axisymmetric simulation, only the y-direction matters
                # *2 because only one core is simulated
                result[simnum].loss_core = result[simnum].loss_core * 2 * (myind.symm[1] + 1)
            result[simnum].loss_core = result[simnum].loss_core
            msg.print_msg(0, f"Core Loss: {result[simnum].loss_core:.1f} W\n", simParam)
    
            # Total loss
            result[simnum].loss_total = result[simnum].loss_core + result[simnum].loss_copper + result[simnum].conduction_loss
            msg.print_msg(0, f"Total Loss: {result[simnum].loss_total:.2f}W\n", simParam)
            msg.print_msg(0, f"Total Efficiency: {(1-result[simnum].loss_total/simParam.pout)*100:.2f} %\n", simParam)

    # Save all the data
    save_path = Path(simParam.datafolder) / f"{myind.description}.pkl"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'wb') as f:
        pickle.dump({
            'myind': myind,
            'result': result,
            'simParam': simParam
        }, f)

    # Finish
    elapsedTime = time.time() - start_time
    msg.print_msg(0, f"\n\n--------------------Finished in {elapsedTime:.0f} s--------------------\n", simParam)

    # Open FEMM again and show the flux-density of the fundamental
    if simParam.SHOWDESIGN:
        sim_to_show = simParam.SHOWDESIGN_SIMULATION
        # Check if the requested simulation was actually run
        if not simParam.SIMULATIONS[sim_to_show]:
            # If the requested simulation wasn't run, try the other one
            sim_to_show = 1 - sim_to_show
            if not simParam.SIMULATIONS[sim_to_show]:
                print("Warning: No simulation available to show")
            else:
                myind.showDesign(result, sim_to_show, 1, 'mag', 50e-3, simParam)
        else:
            myind.showDesign(result, sim_to_show, 1, 'mag', 50e-3, simParam)

    # Delete the msg handle to close the logfile (might not be necessary but doesn't hurt)
    del msg
