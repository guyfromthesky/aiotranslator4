"""TM file class module.

Include the info about the TM and methods to modify TM data.
"""

__version__ = '1.1'
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
        path -- Path to the TM file.
        basename -- File basename.
        backup_dirname -- Directory name of the backup file.
        tm_version -- TM version. Format version x.y. Ex: version 1.0
        ext -- File extension. Currently only support .csv.
        supported_languages -- Languages that the TM supports. Used as columns
            in DataFrame.
        data -- Data in the TM. Accept only DataFrame class from pandas.
    """
    def __init__(self, path: str):
        """
        Args:
            path -- Path to the TM file.

        Raises:
            Exception -- Error while initializing TM.
        """
        # Set up default value
        try:
            self._path = path # Set up property for self.path
            self.basename = None
            self.ext = '.csv' # Only support Comma-separated Values
            self.backup_dirname = self.correct_path_os(
                f"{os.environ['appdata']}\\AIO Translator\\Backup\\")
            self.backup_path = self.init_backup_path()
            
            self.tm_version = 4
            self.supported_languages = ['ko', 'en', 'cn', 'jp', 'vi']
            self._data = None
        except Exception as e:
            print('Error while initializing TM file: ', e)

    @property
    def path(self):
        """path attribute of the class."""
        return self._path

    @path.setter
    def path(self, path):
        """Set path attribute via self._path.
        
        Validate the path to TM file when initializing a class instance.
        Also set the basename of the TM file.
        Supported extension: .csv

        Args:
            path -- str path that gets directly on initialization.

        Raises:
            Exception -- Error while initializing TM path in {__class__}
        """
        try:
            if os.path.isfile(path):
                file_root, file_ext = os.path.splitext(path)
                if file_ext == '.csv':
                    self.basename = os.path.basename(path)
                    self._path = self.correct_path_os(path)
                else:
                    print(f'Incorrect file format: {file_ext}')
            else:
                print('Cannot initialize TM file path '
                    'because path is not a file: ', path)
        except Exception as e:
            raise(f'Error while initializing TM path in {__class__}: ', e)

    @property
    def data(self):
        """data attribute of the class"""
        print('value data')
        return self._data

    @data.setter
    def data(self, data):
        """Set data attribute via self._data

        Get the data directly from the TM file.
        Only allow DataFrame from pandas and csv extension.

        Args:
            data -- An instance of pandas DataFrame. Empty dataframe
                by default.

        Raises:
            TypeError -- Data type is not an instance of DataFrame
        """
        # Only accept DataFrame type data
        print('set value...')
        if isinstance(data, pd.DataFrame):
            print('true')
            data = pd.read_csv(
                self.path, usecols=self.supported_languages)
            self._data = data
        else:
            print('false')
            # raise TypeError('Data type is not an instance of DataFrame: ',
            #     type(data))

    def correct_path_os(self, path):
        """Replace backward slash with forward slash if OS is not Windows.
        
        Args:
            path -- Path to replace backward slash.
        """
        if not sys.platform.startswith('win'):
            return str(path).replace('\\', '//')
        return path

    
    ### DEPRICATED: VER 1.0
    # def set_path(self, file_path: str=None):
    #     """Set a new path of the TM file.
        
    #     Args:
    #         path -- New selected path for TM file.
    #     Raises:
    #         Exception -- Error while setting TM file path.
    #         Exception -- Incorrect extension while setting TM file path.
    #         Exception -- The path is not a file while setting TM file path.
    #     """
    #     try:
    #         file_path = self.correct_path_os(file_path)
    #         if os.path.isfile(file_path):
    #             file_basename = os.path.basename(file_path)
    #             file_name, file_ext = os.path.splitext(file_basename)
    #             # Only support .csv
    #             if file_ext == '.csv':
    #                 self.path = file_path
    #                 self.name = file_name
    #             else:
    #                 raise Exception('Incorrect extension while'
    #                     'setting TM file path.')
    #         else:
    #             raise Exception('The path is not a file while'
    #                 'setting TM file path.')
    #     except Exception as e:
    #         print('Error while setting TM file path: ', e)

    ### DEPRICATED: VER 1.0
    # def init_path(self):
    #     """Return str of the path to the TM file."""
    #     return self.correct_path_os(
    #         f'{self.dirname}\\{self.name}{self.ext}')

    def init_backup_path(self):
        """Return str of the path to the backup TM file."""
        return self.correct_path_os(
            f"{os.environ['appdata']}\\AIO Translator\\Backup\\"
                f"{self.basename}_backup{self.ext}")

class CloudTranslationMemoryFile(TranslationMemoryFile):
    """TM file object in Google Cloud Storage.
    
    Info about TM file such as file name, data in the TM and methods to
    modify them.
    This class inherits from TranslationMemoryFile class with methods to
    access Google Cloud Storage and get the data.

    Attributes:
        path -- Path to the TM file.
        basename -- File basename.
        local_dirname -- Directory/Folder name of the TM file on the local
            computer of a user.
        backup_dirname -- Directory name of the backup file.
        tm_version -- TM version. Format version x.y. Ex: version 1.0
        ext -- File extension. Currently only support .csv.
        supported_languages -- Languages that the TM supports. Used as columns
            in DataFrame.
        data -- Data in the TM. Accept only DataFrame class from pandas.
    """
    def __init__(self, path):
        super().__init__(path)
        self.local_dirname = self.correct_path_os(
            f"{os.environ['appdata']}\\AIO Translator\\TM\\")
        self.data = None

test_path = r"D:\Translation Tool\TM_MSM.csv"

tm_file = TranslationMemoryFile(test_path)
print(tm_file.path)
print(tm_file.data)
print(tm_file._data)