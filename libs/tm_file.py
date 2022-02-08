"""TM file class module.

Include the info about the TM and methods to modify TM data.
"""

__version__ = '1.0'
__author__ = 'anonymous'

# System, standard lib
import os
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
    def __init__(self, test=[]):
        """
        Raises:
            Exception -- Error while initializing TM.
        """
        # Set up default value
        try:
            self.name = 'hello'
            self.dirname = self.correct_path_os(
                f"{os.environ['appdata']}\\AIO Translator\\TM\\")
            self.backup_dirname = self.correct_path_os(
                f"{os.environ['appdata']}\\AIO Translator\\Backup\\")
            # Only support Comma-separated Values
            self.ext = '.csv'
            self.tm_version = 4
            # Only accept DataFrame type data
            self.data = pd.DataFrame()
        except Exception as e:
            print('Error while initializing TM: ', e)

    def correct_path_os(self, path):
        """Replace backward slash with forward slash if OS is not Windows."""
        if not sys.platform.startswith('win'):
            return str(path).replace('\\', '//')
        return path

    def get_path(self):
        """Return the path to the TM file."""
        return self.correct_path_os(
            f'{self.dirname}\\{self.name}{self.ext}')

    def get_backup_path(self):
        """Return the path to the backup TM file."""
        return self.correct_path_os(
            f'{self.backup_dirname}\\{self.name}_backup{self.ext}')

tm_file = TranslationMemoryFile()