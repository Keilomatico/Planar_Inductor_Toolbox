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

def sortData(data, index):
    # Sorts the complex data by absolute value
    myarray = np.column_stack([np.abs(data), index, data])
    mytable = pd.DataFrame(myarray)
    mytable = mytable.sort_values(0, ascending=False)
    index = mytable.iloc[:, 1].values
    data = mytable.iloc[:, 2].values
    return data, index
