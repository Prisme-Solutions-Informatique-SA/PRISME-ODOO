# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2020 Prisme Solutions Informatique SA <http://prisme.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public Lic
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Project ID :    OERP-006-02
#    Phabricator :   T515
#
##########################################################################
import os
import datetime
import time
import platform

# Log data into files named by date
# Remove automatically old files
# TODO Improve performances if necessary (remove old files in constructor, aso.)
class prisme_file_logger():

    # Format of the dates used
    global date_format
    date_format = '%Y-%m-%d'
    
    # logs_dir (String): Directory where to put logs
    # keep_history (int): Keep logs from the x last days
    def __init__(self, logs_dir='/var/log/prisme/warranty/', keep_history=15):
        self.logs_dir = logs_dir
        self.keep_history = keep_history
    
    # Main function. Add the message to the file log of the current date.
    def log(self, message):
        # Keeping this file logger in case it needs to be used again in the future
        """if(platform.system() == 'Linux'):
            # Adding the date to the file
            message = '[' + time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()) +\
             '] ' + message
            # Getting log file name
            log_file = self._manage_log_file()
            # Opening the file in "add" mode
            file = open(self.logs_dir + log_file, 'a')
            # Adding the line
            file.write(message + '\n')
            # Closing the file
            file.close()"""
        
    # Create the file if necessary and remove old files. Return the
    # file to use.
    def _manage_log_file(self):
        self._remove_old_files()
        now = datetime.date.today()
        file_name = now.strftime(date_format)
        
        # Creating file if it not exists
        if not os.path.exists(self.logs_dir + file_name):
            file = open(self.logs_dir + file_name, 'w')
            file.close()
            
        return file_name
        
    # Remove files aged of more than the number of days given by keep_history
    def _remove_old_files(self):
        # For each file in the directory where to keep log files
        dir_list = os.listdir(self.logs_dir)
        for file_name in dir_list:
            now_date = datetime.date.today()
            try:
                # Try to convert the file name into a date
                file_date = datetime.datetime.strptime(file_name,date_format).date()
            except ValueError:
                # In case of exception (the file has not the date format), 
                # delete the file and go to the next loop (to avoid errors)
                os.remove(self.logs_dir + file_name)
                continue
            # Get the difference between now ant the file date
            difference = now_date - file_date
            # If the file is to old, delete
            if difference.days > self.keep_history:
                os.remove(self.logs_dir + file_name)
                
