# Planar Inductor Toolbox
Toolbox to simulate high-frequency planar inductors using Matlab and FEMM

## Getting started with the inductor design software
Before using the software you need to install [FEMM](https://www.femm.info/wiki/HomePage). Next, use Matlab's interactive `pathtool` to add the `mfiles` directory (typically located at *C:\Program Files\femm42\mfiles*) to the search path. More information can be found in the OctaveFEMM Manual. It is highly recommended to refer to the manual if you encounter trouble with this script.

## Key Files

<details>
<summary><strong>simCustomCore</strong></summary>
<p>Run this script to simulate a design.</p>
</details>

<details>
<summary><strong>designs</strong></summary>
<p>
All designs are specified here. A design is a fully parametrized core of a certain geometry. Each design, with its unique design number, consists of:
<ul>
<li>A set of parameters that fully describe it</li>
<li>A winding function that will be used later to draw the windings</li>
</ul>

Implemented winding functions:
<ul>
<li><code>standardWinding</code></li>
<li><code>standardWindingEdge</code></li>
<li><code>curvedWinding</code></li>
</ul>

Once parameters are specified, <code>designs</code> calls a geometry-specific function that:
<ul>
<li>Creates an array of rectangular areas for core drawing</li>
<li>Names the areas</li>
<li>Specifies properties like symmetry</li>
</ul>

Implemented core functions:
<ul>
<li><code>coreSingleInductor</code></li>
<li><code>coreFourPole</code></li>
</ul>

An <strong>Inductor</strong> object is returned.
</p>
</details>

<details>
<summary><strong>drawPlanarInductor</strong> and <strong>drawAxisymmetricInductor</strong></summary>
<p>These functions take an Inductor object and use it to create the design in FEMM.</p>
</details>

<details>
<summary><strong>simulationParameters</strong></summary>
<p>This file controls the behavior of <code>simCustomCore</code> and the FEMM solver, specifying parameters such as operating point and desired ripple.</p>
</details>

<details>
<summary><strong>Message</strong></summary>
<p>
To not only print to the console but also store output in a logfile, <code>simCustomCore</code> creates a <code>Message</code> object that prints to the console and saves to the logfile simultaneously.
</p>
</details>

<details>
<summary><strong>evaluateDesigns</strong></summary>
<p>
After simulating a few designs using <code>simCustomCore</code>, use this script to compare them.
</p>
</details>

## How to Simulate a New Geometry

1. Identify the relevant parameters that fully describe the new geometry.
2. Add a new design to the `designs` file with these parameters.
3. Create a new core file similar to `coreSingleInductor` or `coreFourPole`:
   - Translate parameters into rectangles for planar and axisymmetric simulation.
4. Update `simDesign` in `simCustomCore` to the new design number.
5. Run the simulation.