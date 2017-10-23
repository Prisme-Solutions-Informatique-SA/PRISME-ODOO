import os
import datetime
import time

# Log data into files named by date
# Remove automatically old files
# TODO Improve permormances if necessary (remove old files in constructor, aso.)
class prisme_file_logger():

    # Format of the dates used
    
    global date_format
    date_format = '%Y-%m-%d'
    
    # logs_dir (String): Directory where to put logs
    # keep_history (int): Keep logs from the x last days
    def __init__(self, logs_dir='/var/log/prisme/postit/', keep_history=15):
        self.logs_dir = logs_dir
        self.keep_history = keep_history
    
    # Main function. Add the message to the file log of the current date.
    def log(self, message):
        # Converting to UTF-8
        msg_clean = message.encode("ascii", "replace")
        # Adding the date to the file
        msg_clean = '[' + time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()) +\
         '] ' + msg_clean
        # Getting log file name
        log_file = self._manage_log_file()
        # Oppening the file in "add" mode
        file = open(self.logs_dir + log_file, 'a')
        # Adding the line
        file.write(msg_clean + '\n')
        # Closing the file
        file.close()
        
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
                file_date = \
                        datetime.datetime.strptime(file_name, \
                        date_format).date()
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
                
