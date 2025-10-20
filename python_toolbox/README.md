# Python Toolbox for Planar Inductor Simulation

This folder contains the Python conversion of the MATLAB Planar Inductor Toolbox.

## Conversion Status

### ✅ Completed Files:

**Main Simulation:**
- simCustomCore.py - Main simulation script

**Utility Functions:**
- getRectangle.py - Create rectangle arrays
- moveRects.py - Move rectangles
- mirrorRects.py - Mirror rectangles
- sortData.py - Sort complex data by absolute value
- myintegral.py - Custom integration function
- mymean.py - Custom mean calculation
- myrms.py - Custom RMS calculation
- getSpectrum.py - FFT spectrum analysis

**Class Definitions:**
- Material.py - Material properties class
- PCB.py - PCB parameters class
- Result.py - Simulation results class
- Message.py - Logging/messaging class
- simulationParameters.py - Simulation parameters class
- Inductor.py - Inductor design class

**Drawing Functions:**
- drawPlanarInductor.py - Draw planar simulation geometry
- drawAxisymmetricInductor.py - Draw axisymmetric simulation geometry

**Winding Functions:**
- standardWinding.py - Standard winding layout
- standardWindingEdge.py - Standard winding with edge plating
- curvedWinding.py - Curved winding layout

**Analysis Functions:**
- getInductancePlanar.py - Planar inductance calculation
- getInductanceAxi.py - Axisymmetric inductance calculation
- getWaveformMath.py - Converter waveform calculations from differential equations
- corelossSullivan.py - iGSE core loss calculation (Sullivan method, ~500 lines)
- calcCapacitance.py - Capacitor sizing calculations

**Core Design Functions:**
- coreSingleInductor.py - Single inductor core geometry
- coreFourPole.py - Four-pole coupled inductor geometry

**Design Management:**
- designs.py - Design library/selector function with 5 example designs
- evaluateDesigns.py - Batch design evaluation and comparison script

### ✅ ALL CONVERSIONS COMPLETE!

All MATLAB files have been successfully converted to Python using the pyfemm library.

**Design Functions:**
- designs.m → designs.py

**Evaluation:**
- evaluateDesigns.m → evaluateDesigns.py

## Usage

```python
from python_toolbox.simCustomCore import *

# The main simulation script will run when executed
```

## Key Differences from MATLAB:

1. **Arrays**: MATLAB 1-based indexing → Python 0-based indexing
2. **Matrices**: MATLAB matrices → NumPy arrays
3. **Strings**: MATLAB sprintf → Python f-strings
4. **File I/O**: MATLAB save/load → Python pickle
5. **FEMM**: OctaveFEMM → pyfemm library
6. **Classes**: MATLAB handle classes → Python classes (already reference types)

## Dependencies

Install required packages:
```bash
pip install numpy scipy pandas femm
```

## Notes

- All original comments and features have been preserved
- Inactive features remain in the code for future use
- The code structure follows the MATLAB version as closely as possible
