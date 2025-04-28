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

classdef Message
    % Class to send log-messages. 
    % For each simulation, a message object shoud be creases which is used
    % to store messages into a uniquely named logfile and print messages. 
    % A message needs to be given a priority such that only messages above
    % a certain priority are printed and saved (both values can be adjusted
    % independently within simulationParameters using verbose_detail and
    % logfile_detail
    
    properties
        fileID;
        filename;
    end
    
    methods
        function obj = Message(filename)
            % Create a message object that writes to filename
            obj.filename = filename;
            obj.fileID = fopen(obj.filename,'w');
        end
        
        function print(obj, detail, text, simParam)
            % send some text to the console and/or logfile as specified in simParam
            if simParam.verbose && detail <= simParam.verbose_detail
                fprintf("%s", text);
            end
        
            if simParam.writeLogfile && detail <= simParam.logfile_detail
                fprintf(obj.fileID, text);
            end
        end

        function append(obj, text)
            fprintf(obj.fileID, text);
        end

        function finish(obj, logHandle)
            % Add the data to logHandle and close the current file
            fclose(obj.fileID);
            logdata = fileread(obj.filename);
            logHandle.append(sprintf("\n----------%s: ----------\n", obj.filename));
            logHandle.append(logdata);
        end
        
        % Close the file when the object is deleted
        function delete(obj)
            try
               fclose(obj.fileID);
            catch exception
               
            end
        end
    end
end

