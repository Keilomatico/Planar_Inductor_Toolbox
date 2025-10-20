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

class Message:
    # Class to send log-messages. 
    # For each simulation, a message object shoud be creases which is used
    # to store messages into a uniquely named logfile and print messages. 
    # A message needs to be given a priority such that only messages above
    # a certain priority are printed and saved (both values can be adjusted
    # independently within simulationParameters using verbose_detail and
    # logfile_detail
    
    def __init__(self, filename):
        # Create a message object that writes to filename
        self.filename = filename
        self.fileID = open(self.filename, 'w')
    
    def print_msg(self, detail, text, simParam):
        # send some text to the console and/or logfile as specified in simParam
        if simParam.verbose and detail <= simParam.verbose_detail:
            print(text, end='')
        
        if simParam.writeLogfile and detail <= simParam.logfile_detail:
            self.fileID.write(text)
    
    def append(self, text):
        self.fileID.write(text)
    
    def finish(self, logHandle):
        # Add the data to logHandle and close the current file
        self.fileID.close()
        with open(self.filename, 'r') as f:
            logdata = f.read()
        logHandle.append(f"\n----------{self.filename}: ----------\n")
        logHandle.append(logdata)
    
    # Close the file when the object is deleted
    def __del__(self):
        try:
            self.fileID.close()
        except:
            pass
