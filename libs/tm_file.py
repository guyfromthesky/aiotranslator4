"""TM file class module.

Include the info about the TM and methods to modify TM data.
"""

__version__ = '1.0'
__author__ = 'anonymous'

# System, standard lib
import os
import datetime

# Data module
import pandas as pd

class TMFile:
    """TM file object.
    
    Info about TM file such as file name, data in the TM and methods to
    modify them.

    Attributes:
        name: File name.
        dirname: Directory/Folder name of the TM file.
        tm_version: TM version. Format version x.y. Ex: version 1.0
        ext: File extension. Must be .pkl or .csv.
        data: Data in the TM. Accept only DataFrame class from pandas.
    """
    def __init__(self, tm_info_obj):
        """Raises: Exception: Error while initializing TM."""
        try:
            # Support only pickle and csv extension
            if tm_info_obj['ext'] in ['.pkl', '.csv']:
                # Only accept DataFrame
                if isinstance(tm_info_obj['data'], pd.DataFrame):
                    self.name = tm_info_obj['name']
                    self.ext = tm_info_obj['ext']
                    self.dirname = tm_info_obj['dirname']
                    self.tm_version = tm_info_obj['tm_version']
                    self.data = tm_info_obj['data']
                else:
                    print('Cannot create TM due to incorrect data type.')
            else:
                print('Cannot create TM due to incorrect extension.')
        except Exception as e:
            print('Error while initializing TM: ', e)

tm_info = {
    'name': None,
    'dirname': None,
    'tm_version': 4,
    'ext': '.csv',
    'data': pd.DataFrame(),
}

tm_file = TMFile(tm_info)

print(tm_file)