"""TM file class module.

Include the info about the TM and methods to modify TM data.
"""

__version__ = '1.0'
__author__ = 'anonymous'

# System, standard lib
import os
import re
import sys
import datetime

# Data module
import pandas as pd

class TranslationMemoryFile:
    """TM file object.
    
    Info about TM file such as file name, data in the TM and methods to
    modify them.

    Attributes:
        name -- File name.
        dirname -- Directory/Folder name of the TM file.
        backup_dirname -- Directory name of the backup file.
        tm_version -- TM version. Format version x.y. Ex: version 1.0
        ext -- File extension. Currently only support .csv.
        data -- Data in the TM. Accept only DataFrame class from pandas.
    """
    def __init__(self):
        """
        Raises:
            Exception -- Error while initializing TM.
        """
        # Set up default value
        try:
            self.name = None
            self.ext = '.csv' # Only support Comma-separated Values
            self.dirname = self.correct_path_os(
                f"{os.environ['appdata']}\\AIO Translator\\TM\\")
            self.backup_dirname = self.correct_path_os(
                f"{os.environ['appdata']}\\AIO Translator\\Backup\\")
            self.path = self.init_path()
            self.backup_path = self.init_backup_path()
            
            self.tm_version = 4
            self.data = None # Only accept DataFrame type data
        except Exception as e:
            print('Error while initializing TM: ', e)

    def correct_path_os(self, path):
        """Replace backward slash with forward slash if OS is not Windows."""
        if not sys.platform.startswith('win'):
            return str(path).replace('\\', '//')
        return path

    def set_path(self, file_path: str=None):
        """Set a new path of the TM file.
        
        Args:
            path -- New selected path for TM file.
        Raises:
            Exception -- Error while setting TM file path.
            Exception -- Incorrect extension while setting TM file path.
            Exception -- The path is not a file while setting TM file path.
        """
        try:
            file_path = self.correct_path_os(file_path)
            if os.path.isfile(file_path):
                file_basename = os.path.basename(file_path)
                file_name, file_ext = os.path.splitext(file_basename)
                # Only support .csv
                if file_ext == '.csv':
                    self.path = file_path
                    self.name = file_name
                else:
                    raise Exception('Incorrect extension while'
                        'setting TM file path.')
            else:
                raise Exception('The path is not a file while'
                    'setting TM file path.')
        except Exception as e:
            print('Error while setting TM file path: ', e)

    def init_path(self):
        """Return str of the path to the TM file."""
        return self.correct_path_os(
            f'{self.dirname}\\{self.name}{self.ext}')

    def init_backup_path(self):
        """Return str of the path to the backup TM file."""
        return self.correct_path_os(
            f'{self.backup_dirname}\\{self.name}_backup{self.ext}')

    def get_data(self):
        """Return data in the csv TM file.
        
        Only allow DataFrame from pandas and csv extension.

        Returns:
            data: DataFrame instance from pandas
        """
        # path = self.get_path()
        # # Only accept DataFrame type data
        # if isinstance(self.data, pd.DataFrame):
        #     self.data = pd.read_csv(path, )
            


tm_file = TranslationMemoryFile()