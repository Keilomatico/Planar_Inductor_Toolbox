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

# This script reads all designs from the "data" folder and summarizes them in a nice table.

import os
import pickle
import pandas as pd
from simulationParameters import simulationParameters

def evaluateDesigns():
    # Specify the column names that should be printed in the table. This needs
    # to match with the creation of a row further down
    mynames = ["description", "num", "A [mm^2]", "h [mm]", "V [mm^3]", 
               "L_s_pln [nH]", "L_s_axi [nH]", "k", "fs [MHz]", 
               "Pco_pln [W]", "Pco_axi [W]", "Hdc_max_pln [A/m]"]
    
    # Create an empty DataFrame with the right names
    rawtable = pd.DataFrame(columns=mynames)

    # Get all the filenames from the data directory
    simParam = simulationParameters()
    datafolder = simParam.datafolder
    filenames = os.listdir(datafolder)
    
    index = 0
    for filename in filenames:
        filepath = os.path.join(datafolder, filename)
        # Check if it's actually a file
        if os.path.isfile(filepath):
            # Load the relevant data from the pickle file
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            mywinding = data.get('mywinding')
            myind = data.get('myind')
            result = data.get('result')
            
            # Multiply area by 2 for single designs for a better comparability
            if myind.coupled == 0:
                area = myind.dimension['width'] * myind.dimension['depth'] * 2
            else:
                area = myind.dimension['width'] * myind.dimension['depth']
            
            # Create a new row
            new_row = {
                "description": myind.description,
                "num": mywinding,
                "A [mm^2]": area,
                "h [mm]": myind.dimension['height'],
                "V [mm^3]": area * myind.dimension['height'],
                "L_s_pln [nH]": result[0].L_self * 1e9,
                "L_s_axi [nH]": result[1].L_self * 1e9,
                "k": result[0].k,
                "fs [MHz]": result[0].fs / 1e6,
                "Pco_pln [W]": result[0].loss_copper,
                "Pco_axi [W]": result[1].loss_copper,
                "Hdc_max_pln [A/m]": max(result[0].Hdc)
            }
            rawtable.loc[index] = new_row
            index += 1
    
    # Sort by some desired property, in this case copper loss
    rawtable = rawtable.sort_values(by='Pco_pln [W]', ascending=True)
    print(rawtable)
    
    return rawtable


if __name__ == "__main__":
    evaluateDesigns()
