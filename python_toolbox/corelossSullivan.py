# This file is not licensed under GNU General Public License!
# 
# This script is based on the paper "Improved calculation of core loss with nonsinusoidal waveforms"
# by Jieli Li; T. Abdallah; C.R. Sullivan
# It was downloaded from http://engineering.dartmouth.edu/inductor

# CORELOSS Calculate power loss in a ferrite core.
#   
#   CORELOSS(time, B, alpha, beta, k, suppressFlag)
#
#   time and B are a piecewise linear series of data points
#   time = vector of successive time values corresponding to flux values, in seconds.
#   B = vector of flux densities corresponding to time vector values, in tesla.
#   alpha, beta, k = Steinmetz parameters.  Must be for use with MKS units
#   suppressFlag: 0 to display input plot, loss  and error information in the
#                   command window.
#                 1 to suppress all output and only return the loss value.
#                   If an error occurs, CORELOSS will return -1.
#             
#   CORELOSS will calculate the power loss in your specified ferrite core.
#   The loss value is in W/m^3. 

# Created by Charles Sullivan, Kapil Venkatachalam, Jens Czogalla
# at Thayer School of Engineering, Dartmouth College.
# Modified by Kip Benson 3/03 (error checking on input data and improved
# command line interface).
# Corrected 11/05 C. Sullivan:  fixed minor loop handling bug ("minortime" was mistyped as minorime")

import numpy as np
import matplotlib.pyplot as plt

def corelossSullivan(tvs, B, param, suppressFlag):
    alpha = param.fexp
    beta = param.bexp
    k = param.k

    # tvs is what was called "time" in help info above.
    # check data for errors
    error = 'None'
    
    # makes sure times are successive
    for i in range(1, len(tvs)):
        if tvs[i-1] >= tvs[i]:
            error = 'Time data points must be successive.'
    
    # make sure vectors are same length
    if len(tvs) != len(B):
        error = 'Time and flux vectors must have same length'
    
    if B[0] != B[len(B)-1]:
        error = 'Since the PWL input is periodic, the first flux value must equal the last'
    # done checking for errors

    # calculate core loss if there is no error with the input data
    if suppressFlag == 0:
        if error == 'None':
            Pcore = gsepwl(tvs, B, alpha, beta, k)
            print(f'Core Loss: {Pcore} (unit depends on parameters, usually mW/cm^3)')
            y = Pcore
            
            # plot the user's input
            plt.figure()
            plt.plot(tvs, B, 'b.-')
            plt.xlabel('Time (s)')
            plt.ylabel('Flux Density (T)')
            plt.title('Plot of Input Data')
            plt.show()
        else:
            print(f'Error: {error}')
            y = -1
    
    elif suppressFlag == 1:  # suppress output
        if error == 'None':
            y = gsepwl(tvs, B, alpha, beta, k)
        else:
            y = -1  # error occurred
    
    return y


# ====================================================================
# to calculate core loss per unit volume using GSE for PWL signal form
# ====================================================================
def gsepwl(t, B, alpha, beta, k):
    # a is fraction of Bpp used, 1-a is fraction of original
    a = 1.0  # a=1 for iGSE
             # a=0 for GSE

    T = t[len(t)-1] - t[0]  # total time of PWL period

    ki = k / ((2**(beta+1)) * np.pi**(alpha-1) * (0.2761 + 1.7061/(alpha+1.354)))

    B, t, Bs, ts = splitloop(B, t)  # split waveform into major and minor loops

    pseg = np.zeros(len(ts) + 1)
    dt = np.zeros(len(ts) + 1)
    
    pseg[0] = calcseg(t, B, alpha, beta, ki, a)
    dt[0] = t[len(t)-1] - t[0]

    for j in range(len(ts)):
        pseg[j+1] = calcseg(ts[j], Bs[j], alpha, beta, ki, a)
        tseg = ts[j]
        dt[j+1] = tseg[len(tseg)-1] - tseg[0]

    p = np.sum(pseg * dt) / T
    return p


# ==============
# Loop Splitter
# ==============
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Loop Spliter%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%By %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Kapil Venkatachalam%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Modified on June 2nd, 2002%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# This program takes a piecewise linear
# current waveform corresponding to a B-H loop 
# and splits it into smaller waveforms 
# which have the same starting and ending value.
#
# Inputs:
#
# 'a': B vector corresponding to the B-H loop.
# 'b': Time vector of currents corresponding to the B-H loop. 
#
# Outputs:
#
# 'Majorloop': B values corresponding to the major B-H loop.
# 'Majortime': time vector of currents corresponding to the major B-H loop.
# 'Minorloop': B values corresponding to the different minor B-H loop.
# 'Minorloop': time vector of currents corresponding to the different minor B-H loop.

def splitloop(a, b):
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #                Reshaping the waveforms and identifying the peak point
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Identifies the lowest point in 'a'.
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    e = 0  # Constant defined to identify the position of the lowest value.
    sa = 1  # Counter to check if lowest point is reached.
    for d in range(len(a)):  # Check for the size of vector.
        if (a[d] == np.min(a) and sa == 1):  # Checking condition if lowest point has been reached.
            e = d  # Identifies the lowest point in the waveform.
            sa = sa + 1  # Counter incremented if lowest point is reached.

    # v is a vector which stores the shifted values of 'a'.
    # t is a vector which stores the shifted values of 'b'.

    v = [a[e]]  # adds the lowest point as the first value.
    t = [0]  # adds the corresponding time value the first value.

    bdiff = np.diff(b)  # adjusts for the times corresponding to the values.
    cumdiff = 0

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Loop stores all value of 'a' (from the lowest point till the end point) in 'v'.
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    for q in range(e+1, len(a)):  # 'q' counts the remaining vectors before the lowest point is reached.
        v.append(a[q])  # Values of 'a' stored in 'v'.
        cumdiff = cumdiff + bdiff[q-1]  # Time adjustment
        t.append(cumdiff)  # Values of 'b' stored in 't'.

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Loop stores all value of 'a' (from the starting point till the lowest point) in 'v'.
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    for zx in range(1, e):  # Appends the part before the lowest point.
        v.append(a[zx])  # Values of 'a' stored in 'v'.
        cumdiff = cumdiff + bdiff[zx-1]  # Time adjustment    
        t.append(cumdiff)  # Values of 'b' stored in 't'.

    v = np.array(v)
    t = np.array(t)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #                         Finds the position of the peak value
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    z = 0  # Constant defined to identify the position of the peak value.
    sa = 1  # Counter to check if peak point is reached.
    for x in range(len(v)):  # Check for the size of vector.
        if (v[x] == np.max(v) and sa == 1):  # Checking condition if peak has been reached.
            z = x  # Identifies the peak point in the waveform.
            sa = sa + 1  # Counter incremented if peak point is reached.

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #             End of reshaping the waveforms and identifying the peak point
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # Defining variables to keep track of values in the vectors
    i = 1  # Python: changed from 2 to 1 (0-based indexing)
    j = 0  # Python: changed from 1 to 0 (0-based indexing)
    k = 0  # Python: changed from 1 to 0 (0-based indexing)

    s = [[] for _ in range(1300)]  # Defining cells for minorloop.
    p = [[] for _ in range(1300)]  # Defining cells for minortime.

    # 'm' stores the majorloop values extracted from 'v'.
    # 'n' stores the corresponding time values extracted from 't'.

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #                     Splits the rising portion of the waveform
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    m = [v[0]]  # Adds the first element of 'v' to 'm'.
    n = [t[0]]  # Adds the first element of 't' to 'n'.

    while i <= z:  # Checks for all values before the peak point
        
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #                     Check to see if the waveform is rising
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        if v[i] >= v[i-1]:  # Compares adjacent values of 'v'.
            m.append(v[i])  # Adds an element of 'v' to 'm'.
            n.append(t[i])  # Adds an element of 't' to 'n'.
            count = 1  # Counter to keep track of end of the rising part.
        else:
            # Check for minor loop in the rising part
            s[j].append(v[i-1])  # Adds an element of 'v' to 's'.
            p[j].append(t[i-1])  # Adds an element of 't' to 'p'.
            
            # by jens czogalla
            k = k + 1
            
            # Repeating the process till the minor loop ends
            while v[i] < max(m):
                s[j].append(v[i])  # Adds an element of 'v' to 's'.
                p[j].append(t[i])  # Adds an element of 't' to 'p'.
                # by jens czogalla            
                k = k + 1
                i = i + 1  # Increments the counter keeping track of the elements in 'v'.
            
            # Calculating the slope of the rising edge of the minor loop.
            slope = (v[i-1] - v[i]) / (t[i-1] - t[i])

            # Makes the last element of the minor loop same as the maximum value of 'm'.
            s[j].append(max(m))
            
            # Computes the value of time of the point which was stored last in 's'.
            stemp = ((max(m) - v[i-1]) / slope) + t[i-1]  # Calculating the time value.
            p[j].append(stemp)  # Value is stored in p.
            m.append(max(m))  # The last point in 'm' is repeated for continuity.
            n.append(stemp)  # The time value is also repeated.
            count = count + 1  # Counter is incremented to indicate end of minor loop.
            j = j + 1  # Index of 's' is incremented.
            # by jens czogalla        
            k = 0  # Python: reset to 0
        
        if count <= 1:  # Check condition keeping track of end of rising part.
            i = i + 1  # Increment counter keeping track of the elements in 'v'.

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #                   End of splitting of the rising portion of the waveform
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # 'm' now stores part the rising part of the major loop.
    # 'n' stores the corresponding time values of the major loop.
    # 's' stores the minor loops in the rising part of the waveform.
    # 'p' stores the corresponding time values of the minor loops.

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #                     Splits the falling portion of the waveform
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    while i < len(v):  # Checks for all values after the peak point
        if v[i] <= v[i-1]:  # Compares adjacent values of 'v'.
            m.append(v[i])  # Adds an element of 'v' to 'm'.
            n.append(t[i])  # Adds an element of 't' to 'n'.
            count = 1  # Counter to keep track of end of the rising part.
        else:
            # Check for minor loop in the falling part.
            temp = v[i-1]  # Temporary variable to store last value in 'v'.
            s[j].append(v[i-1])  # Adds an element of 'v' to 's'. 
            p[j].append(t[i-1])  # Adds an element of 't' to 'p'. 
            # by jens czogalla        
            k = k + 1
            
            while i < len(v) and v[i] > temp:  # Compares adjacent values of 'v' for all the remaining 'v' values.
                s[j].append(v[i])  # Adds an element of 'v' to 's'.
                p[j].append(t[i])  # Adds an element of 't' to 'p'.
                # by jens czogalla            
                k = k + 1
                i = i + 1  # Increments the counter keeping track of the elements in 'v'.
            
            # Repeating the process till the minor loop ends
            # by jens czogalla
            while i < len(v) and k > 1:
                # Calculating the slope of the rising edge of the minor loop.
                slope = (v[i-1] - v[i]) / (t[i-1] - t[i])
                
                # Makes the first element of the minor loop same as the last element in 'm'.
                s[j].append(temp)
                
                # Computes the value of time of the point which was stored last in 's'.
                qtemp = ((temp - v[i-1]) / slope) + t[i-1]  # Calculating the time value.
                p[j].append(qtemp)  # Value is stored in p.
                r = 1  # Counter to make the pass through the loop only once.
                while v[i] != temp and r == 1:
                    m.append(temp)  # The last point in 'm' is repeated for continuity.
                    n.append(qtemp)  # The time value is also repeated.
                    r = r + 1  # Counter incremented to indicate the pass has been made.
                count = count + 1  # Counter is incremented to indicate end of minor loop.
                j = j + 1  # Index of 's' is incremented.
                # by jens czogalla            
                k = 0  # Python: reset to 0
        
        if count <= 1:  # Check condition keeping track of end of falling part.
            i = i + 1  # Increment counter keeping track of the elements in 'v'.

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #                   End of splitting of the falling portion of the waveform
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #              Removal of repetition of points in 'm' and adjusting the values
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    x = len(m)  # Variable to store the length of 'm'.
    majorloop = [m[0]]  # Stores the first element of 'm' in 'majorloop'                 
    majortime = [n[0]]  # Stores the first element of 'n' in 'majortime'      
    g = 0  # Initializing variable which adjust time for points following the point of repetition.

    # by jens czogalla
    for h in range(1, x):
        if m[h-1] != m[h]:  # Checking for repeated points.
            majortime.append(n[h] - g)  # Add time value to 'majortime'.
            majorloop.append(m[h])  # Add corresponding value of 'm' in 'majorloop'.    
        else:
            g = g + n[h] - n[h-1]  # Adjusts the time to compensate for repetitions.

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #           End of removal of repetition of points in 'm' and adjusting the values
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #       Finding the number of minor loops to be used for checking sub loops later
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    uo = 0  # Python: changed from 1 to 0
    pt = 0  # Variable to keep track of the number of minor loops.
    ss = 1
    while ss == 1 and uo < len(s):
        while len(s[uo]) > 0:
            uo = uo + 1
            if uo >= len(s):
                break
        ss = ss + 1
        pt = uo

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #                                        Recursion
    #              Checks if any portion of the  split waveform has subloops.
    #              If so repeats the above process to make it a single loop.
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    minorloop = []
    minortime = []
    for qq in range(pt):
        sinp = s[qq]  # flux
        pinp = p[qq]  # time
        
        if minorloop1(sinp, pinp):
            fn, ln, sn, pn = splitloop(np.array(sinp), np.array(pinp))
            if len(fn) != 0:
                minorloop.append(fn)
                minorloop.append(sn[0])
                minortime.append(ln)
                minortime.append(pn[0])
        else:
            if len(sinp) != 0:
                minorloop.append(np.array(sinp))
                minortime.append(np.array(pinp))

    majorloop = np.array(majorloop)
    majortime = np.array(majortime)
    
    return majorloop, majortime, minorloop, minortime


# =======================================================
# calculate loss for loop segment using improved equation
# =======================================================
def calcseg(t, B, alpha, beta, k1, a):
    # a is fraction of Bpp used, 1-a is fraction of original
    bma1a = (beta - alpha) * (1 - a)  # exponent of B(t)
    bmaa = (beta - alpha) * a  # exponent of Bpp

    Bpp = max(B) - min(B)
    
    # Handle case where Bpp is zero or very small (no flux variation)
    if Bpp < 1e-12:
        return 0.0

    # Always call makepositive to ensure proper handling of zero crossings
    # This splits the waveform at zero crossings
    if np.any(B < 0):
        t, B = makepositive(t, B)

    length = len(t)
    T = t[length-1] - t[0]
    
    # Handle case where T is zero or very small
    if T < 1e-15:
        return 0.0
    
    deltaB = np.abs(B[1:length] - B[0:length-1])
    deltat = t[1:length] - t[0:length-1]
    
    # Avoid division by zero in dBdt
    deltat = np.maximum(deltat, 1e-15)
    dBdt = deltaB / deltat
    
    # Handle the case where dBdt is zero (no flux change)
    # When alpha-1 is negative and dBdt is zero, we get infinity
    # In this case, the contribution to loss should be zero
    m1 = np.where(dBdt > 1e-15, dBdt ** (alpha - 1), 0.0)
    
    # For the B term, ensure all B values are positive before taking fractional power
    B_pos = np.abs(B)  # Ensure positive values
    
    # Calculate m2 with proper handling of zero values
    B1_term = np.where(B_pos[1:length] > 1e-15, B_pos[1:length] ** (bma1a + 1), 0.0)
    B0_term = np.where(B_pos[0:length-1] > 1e-15, B_pos[0:length-1] ** (bma1a + 1), 0.0)
    m2 = np.abs(B1_term - B0_term)
    
    pseg = k1 / T / (bma1a + 1) * np.sum(m1 * m2) * Bpp ** bmaa
    
    return pseg


# ==========================================================================
# Convert a piecewise-linear waveform w (which must be a vector)
# represented by the points w at times t, to a piecewise-linear waveform with 
# points at any zero crossings.  Thus, any segment of the returned waveform is all 
# positive or all negative.  If w is a matrix, use makepositiveM.
# ==========================================================================
def makepositive(t, w):
    t = list(t)
    w = list(w)
    length = len(t)
    cross = [(w[i] * w[i+1]) < 0 for i in range(length-1)]
    loopnumber = length - 1 + sum(cross)
    i = 0
    while i < loopnumber and i < len(cross):
        if cross[i]:
            length = len(w)
            tcross = w[i] * (t[i+1] - t[i]) / (w[i] - w[i+1]) + t[i]
            t = t[0:i+1] + [tcross] + t[i+1:length]
            w = w[0:i+1] + [0] + w[i+1:length]
            cross = cross[0:i+1] + [0] + cross[i+1:length-1]
        i = i + 1
    
    w = np.abs(np.array(w))
    t = np.array(t)
    return t, w


# ==================
# minorloop function
# ==================
def minorloop1(s, p):
    qr = len(s)
    peak = -1
    prevslope = 0
    for i in range(1, qr):
        slope = (s[i-1] - s[i]) / (p[i-1] - p[i])
        if slope <= 0 and prevslope >= 0:
            peak = peak + 1
        if prevslope <= 0 and slope >= 0:
            peak = peak + 1
        prevslope = slope
    
    if peak > 2:
        ml = 1
    else:
        ml = 0
    
    return ml
