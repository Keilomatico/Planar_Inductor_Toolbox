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
import pandas as pd
from scipy import interpolate
import matplotlib.pyplot as plt

# Sorts the complex data by absolute value
def sortData(data, index):
    myarray = np.column_stack([np.abs(data), index, data])
    mytable = pd.DataFrame(myarray)
    mytable = mytable.sort_values(0, ascending=False)
    index = np.real(mytable.iloc[:, 1].values)
    data = mytable.iloc[:, 2].values
    return data, index

# Mirrors each individual rectangle in x or y direction
# dir specifies the direction
# value specifies the mirror line:
# for dir='x' the mirror-line is y=value
# for dir='y' the mirror-line is x=value
def mirrorRects(rects_original, dir, value=0):
    assert (dir == 'x') or (dir == 'y')
    # Use a new variable because otherwise this function works with call by reference
    rects = rects_original.copy()
    
    # Just one corner
    if rects.ndim == 1:
        if dir == 'x':
            rects[0] = 2 * value - rects[0]
        else:  # dir == 'y'
            rects[1] = 2 * value - rects[1]      
    # Just one rectangle
    elif rects.ndim == 2:
        if dir == 'x':
            rects[:,0] = 2 * value - rects[:,0]
        else:  # dir == 'y'
            rects[:,1] = 2 * value - rects[:,1]
    # An array of rectangles
    elif rects.ndim == 3:
        if dir == 'x':
            rects[:,:,0] = 2 * value - rects[:,:,0]
        else:  # dir == 'y'
            rects[:,:,1] = 2 * value - rects[:,:,1]
    else:
        raise Exception("Wrong dimension of rects")
    
    return rects

# Move the rects x and y
def moveRects(rects_original, x, y):
    # Use a new variable because otherwise this function works with call by reference
    rects = rects_original.copy()
    
    # Just one rectangle
    if rects.ndim == 2:
        rects[:, 0] = rects[:, 0] + x
        rects[:, 1] = rects[:, 1] + y
        
    # An array of rectangles
    elif rects.ndim == 3:
       rects[:, :, 0] = rects[:, :, 0] + x
       rects[:, :, 1] = rects[:, :, 1] + y
    
    else:
        raise Exception("Wrong dimension of rects")
        
    return rects

# Creates a rectangle using one corner and width and height
def getRectangle(bottom_left_x, bottom_left_y, width, height):
    rect = np.array([[bottom_left_x, bottom_left_y],
                     [bottom_left_x + width, bottom_left_y + height]])
    return rect

# Calculates the curve of integrating ydata with datapoints at times specified in
# time. The distance between elements does not need to be constant.
def myintegral(time, ydata):
    x = np.linspace(time[0], time[-1], 1001)
    y = np.zeros(len(x))
    # Iterate over the array and integrate the the waveform. 
    j = 1
    init = 0
    for i in range(len(time) - 1):
        while j < len(x) and x[j] <= time[i + 1]:
            if time[i + 1] - time[i] == 0:
                y[j] = 0
            else:
                y[j] = (0.5 * (ydata[i + 1] - ydata[i]) / (time[i + 1] - time[i]) * (x[j] - time[i])**2 + 
                        ydata[i] * (x[j] - time[i]) + init)
            j += 1
        init = y[j - 1]
    
    return x, y

# Calculates the average of ydata with datapoints at times specified in
# time. The distance between elements does not need to be constant.
def mymean(time, ydata):
    # Compute the rms value
    _, y = myintegral(time, ydata)
    dt = time[-1] - time[0]
    result = 1 / dt * y[-1]
    return result

# Calculates the rms value of ydata with datapoints at times specified in
# time. The distance between elements does not need to be constant as
# opposed to the built_in rms function
def myrms(time, ydata):
    sum_val = 0
    # Iterate over the array and integrate the square of the waveform. 
    # See report for a detailed explanation.
    for i in range(len(time) - 1):
        dt = time[i + 1] - time[i]
        if ydata[i + 1] == ydata[i]:
            # Constant value over the interval
            sum_val += dt * ydata[i]**2
        else:
            # Value changes linearly over the interval
            sum_val += dt * (ydata[i]**2 + ydata[i] * ydata[i + 1] + ydata[i + 1]**2) / 3

    # Compute the duration of the interval
    T = time[-1] - time[0]
    result = np.sqrt(sum_val / T)
    return result

# Computes an fft with N sampling points. Returns complex amplitude and frequency sorted by absolute amplitude
def getSpectrum(data, timestamps, N):
    # "Sample" the signal
    period = timestamps[-1]
    f_sample = N / period            # Sampling frequency
    time_interpol = np.arange(0, timestamps[-1], 1/f_sample)                 # Vector with sampling timestamps
    
    # Interpolate the given data to the sampling points
    f_interp = interpolate.interp1d(timestamps, data, kind='linear')
    data_interpol = f_interp(time_interpol)
    
    # Perform FFT
    fft_result = np.fft.fft(data_interpol)
    amplitude = fft_result[0:N//2+1] / N * 2
    amplitude[0] = amplitude[0] / 2  # DC component should only be divided by N
    
    frequency = f_sample / N * np.arange(0, N//2+1)
    return amplitude, frequency

# Determines the converter waveforms by solving the differential equations
def getWaveformMath(sp, fs, res):
    data = {}
    data['imag'] = np.zeros(5)
    data['iout'] = np.zeros(5)
    data['i1'] = np.zeros(5)
    data['i2'] = np.zeros(5)
    
    Ts = 1/fs
    if sp.D < 0.5:
        timestamps = np.array([0, sp.D*Ts, Ts/2, Ts/2+sp.D*Ts, Ts])
        deltaI_mag = sp.Vin*Ts*sp.D/(2*res.L_m)
        deltaI_out = sp.Vin*Ts/res.L_out*sp.D*(0.5-sp.D)
        # Magnetizing current
        data['imag'][0] = -deltaI_mag/2
        data['imag'][1] = data['imag'][0] + sp.D*Ts/res.L_m*sp.Vin/2
        data['imag'][2] = data['imag'][1]
        data['imag'][3] = data['imag'][2] - sp.D*Ts/res.L_m*sp.Vin/2
        data['imag'][4] = data['imag'][3]
        # Output current
        data['iout'][0] = sp.iout_avg - deltaI_out/2
        data['iout'][1] = data['iout'][0] + sp.D*Ts*1/res.L_out*(sp.Vin/2-sp.Vout)
        data['iout'][2] = data['iout'][1] + (0.5-sp.D)*Ts*(-sp.Vout)/res.L_out
        data['iout'][3] = data['iout'][2] + sp.D*Ts*1/res.L_out*(sp.Vin/2-sp.Vout)
        data['iout'][4] = data['iout'][3] + (0.5-sp.D)*Ts*(-sp.Vout)/res.L_out
    else:
        timestamps = np.array([0, (sp.D-0.5)*Ts, Ts/2, sp.D*Ts, Ts])
        deltaI_mag = sp.Vin*Ts/(2*res.L_m)*(1-sp.D)
        deltaI_out = sp.Vin*Ts/res.L_out*(sp.D-0.5)*(1-sp.D)
        # Magnetizing current
        data['imag'][0] = -deltaI_mag/2
        data['imag'][1] = data['imag'][0]
        data['imag'][2] = data['imag'][1] + (1-sp.D)*Ts/res.L_m*sp.Vin/2
        data['imag'][3] = data['imag'][2]
        data['imag'][4] = data['imag'][3] - (1-sp.D)*Ts/res.L_m*sp.Vin/2
        # Output current
        data['iout'][0] = sp.iout_avg - deltaI_out/2
        data['iout'][1] = data['iout'][0] + (sp.D-0.5)*Ts*1/res.L_out*(sp.Vin-sp.Vout)
        data['iout'][2] = data['iout'][1] + (1-sp.D)*Ts*(sp.Vin/2-sp.Vout)/res.L_out
        data['iout'][3] = data['iout'][2] + (sp.D-0.5)*Ts*1/res.L_out*(sp.Vin-sp.Vout)
        data['iout'][4] = data['iout'][3] + (1-sp.D)*Ts*(sp.Vin/2-sp.Vout)/res.L_out
    
    data['i1'] = (data['iout'] + data['imag']) / 2
    data['i2'] = (data['iout'] - data['imag']) / 2
    
    return data, timestamps

def calcCapacitance(time, current, res, simParam):
    """Calculates the required capacitance to achieve a certain input and
    output ripple based on the phase-current waveforms"""
    
    del_ = 1e-12
    timestamps = np.array([time[0], time[1], time[1]+del_, time[2], time[2]+del_, time[3], time[3]+del_, time[4]])
    i_in = np.zeros(8)
    
    if simParam.D < 0.5:
        i_in[0:2] = current['i1'][0:2]
        i_in[2:4] = 0
        i_in[4:6] = current['i2'][2:4]
        i_in[6:8] = 0
    else:
        i_in[0:2] = current['i1'][0:2] + current['i2'][0:2]
        i_in[2:4] = current['i1'][1:3]
        i_in[4:6] = current['i1'][2:4] + current['i2'][2:4]
        i_in[6:8] = current['i2'][3:5]
    
    time_interpol1, inChrg = myintegral(timestamps, mymean(timestamps, i_in) - i_in)
    inChrg_ripple = max(inChrg) - min(inChrg)
    # C = Q / V
    res.Cin = inChrg_ripple / simParam.DeltaVinMax
    print(f"Iin,rms = {myrms(timestamps, i_in):.1f}")

    iout = current['i1'] + current['i2']
    time_interpol2, outChrg = myintegral(time, simParam.iout_avg - iout)
    outChrg_ripple = max(outChrg) - min(outChrg)
    res.Cout = outChrg_ripple / simParam.DeltaVoutMax
    print(f"Iout,rms = {myrms(time, iout):.1f}")

    if simParam.SHOWPLOTS:
        plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(timestamps*1e6, i_in, label="I_{in}")
        plt.plot(time*1e6, iout, label="I_{out}")
        plt.grid(True)
        plt.xlabel("Time [us]")
        plt.ylabel("Current [A]")
        plt.legend(loc='upper left')
        
        plt.subplot(2, 1, 2)
        plt.plot(time_interpol1*1e6, (inChrg - np.mean(inChrg))*1e6, label="Q_{in}")
        plt.plot(time_interpol2*1e6, (outChrg - np.mean(outChrg))*1e6, label="Q_{out}")
        plt.grid(True)
        plt.xlabel("Time [us]")
        plt.ylabel("Charge [uC]")
        plt.legend(loc='upper left')
        plt.show()
    
    return res

def displayLossDensityTable(areaNames, loss_core_area, Hdc, vol, simnum):
    """Displays a formatted table of core loss densities and DC magnetic field values
    
    Args:
        areaNames: List of area names
        loss_core_area: Array of loss densities [W/cm³]
        Hdc: Array of DC magnetic field values [A/m]
        vol: Array of volumes [mm³]
        simnum: Simulation number (0 for planar, 1 for axisymmetric)
    """
    # Create DataFrames and sort by loss density
    myPtable = pd.DataFrame({
        'Area': areaNames,
        'Loss': loss_core_area[:len(areaNames)],
        'Volume': vol[:len(areaNames)]
    })
    myPtable = myPtable.sort_values('Loss', ascending=False)
    
    myHtable = pd.DataFrame({
        'Area': areaNames,
        'Hdc': Hdc[:len(areaNames)]
    })
    myHtable = myHtable.sort_values('Hdc', ascending=False)
    
    # Create a combined table for visualization
    combined_table = pd.DataFrame({
        'Area': myPtable['Area'].values,
        'Loss Density [W/cm³]': myPtable['Loss'].values,
        'Volume [mm³]': myPtable['Volume'].values
    })
    
    # Calculate total loss per area in mW (loss density [W/cm³] * volume [mm³] * 1e-3 [cm³/mm³])
    combined_table['Loss [mW]'] = combined_table['Loss Density [W/cm³]'] * combined_table['Volume [mm³]'] * 1e6
    
    # Add Hdc values in the same order as loss densities
    hdc_dict = dict(zip(myHtable['Area'], myHtable['Hdc']))
    combined_table['Hdc [A/m]'] = combined_table['Area'].map(hdc_dict)
    
    # Format the data for display
    col_headers = ['Area', 'Loss Density [W/cm³]', 'Loss [mW]', 'Hdc [A/m]']
    table_data = []
    for idx, row in combined_table.iterrows():
        table_data.append([
            row['Area'],
            f"{row['Loss Density [W/cm³]']:.1f}",
            f"{row['Loss [mW]']:.1f}",
            f"{row['Hdc [A/m]']:.1f}"
        ])
    
    # Calculate column widths based on content
    max_area_len = max([len(str(name)) for name in combined_table['Area']])
    max_loss_density_len = len('Loss Density [W/cm³]')
    max_total_loss_len = len('Loss [mW]')
    max_hdc_len = len('Hdc [A/m]')
    
    # Calculate relative widths (add padding factor)
    total_len = max_area_len + max_loss_density_len + max_total_loss_len + max_hdc_len
    col_widths = [
        max_area_len / total_len * 1.1,
        max_loss_density_len / total_len * 1.1,
        max_total_loss_len / total_len * 1.1,
        max_hdc_len / total_len * 1.1
    ]
    
    # Adjust figure width based on content
    fig_width = min(14, max(8, total_len * 0.08))
    
    # Display table in plot window
    fig, ax = plt.subplots(figsize=(fig_width, len(areaNames) * 0.4 + 1))
    ax.axis('tight')
    ax.axis('off')
    
    sim_type = "Planar" if simnum == 0 else "Axisymmetric"
    title = f'Core Loss Densities and DC Magnetic Field - {sim_type} Simulation'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    table = ax.table(cellText=table_data,
                   colLabels=col_headers,
                   cellLoc='left',
                   loc='center',
                   colWidths=col_widths)
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style the header
    for i in range(4):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(4):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#E7E6E6')
            else:
                table[(i, j)].set_facecolor('#F2F2F2')
    
    plt.tight_layout()


