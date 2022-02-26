"""TM file class module.

Include the info about the TM and methods to modify TM data.
"""

__version__ = '1.2'
__author__ = 'anonymous'

# System, standard libs
import os
import sys
import datetime
import re
from io import StringIO

# Data modules
import pandas as pd

# Google Cloud modules
from google.cloud import storage

class TranslationMemoryFile:
    """TM file object.

    Mainly used as a parent to share attributes between
    LocalTranslationMemoryFile and CloudTranslationMemoryFile.

    Attributes:
        ext -- TM file extension. Only support .csv (default '.csv')
        data -- @property Data in the TM. Accept only pandas DataFrame class.
        supported_languages -- Languages that the TM supports. Used to
            select columns in self.data DataFrame.
    """
    def __init__(self):
        # Set up default value
        self.ext = '.csv'
        self._data = pd.DataFrame()
        self.supported_languages = ['ko', 'en', 'cn', 'jp', 'vi']

    @property
    def data(self):
        """data attribute of the class"""
        return self._data

    @data.setter
    def data(self, data):
        """Validate data set to self.data.

        Only allow pandas DataFrame type.

        Args:
            data -- Data assigned to the TM. Must be an instance of
                pandas DataFrame.

        Raises:
            TypeError -- Invalid data type.
                Data type is not an instance of DataFrame.
        """
        # Only accept DataFrame type data
        if isinstance(data, pd.DataFrame):
            self._data = data
        else:
            raise TypeError('Invalid data type. Data type is not '
                f'an instance of DataFrame: {type(data)}' )


class LocalTranslationMemoryFile(TranslationMemoryFile):
    """TM file object on a user computer.
    
    Info about TM file such as file name, data in the TM and methods to
    modify them.

    Attributes:
        path -- @property path to the TM file.
        ext -- TM file extension. Only support .csv. (default '.csv')
        basename -- Full filename of the TM.
        backup_path -- Path of the backup TM file.
        tm_version -- TM version. (default 4)
        supported_languages -- Languages that the TM supports. Used to
            select columns in self.data DataFrame.
        data -- @property Data in the TM. Accept only pandas DataFrame class.
    """
    def __init__(self, path: str):
        """
        Args:
            path -- Path to the TM file.

        Raises:
            Exception -- Error while initializing TM file.
            TypeError -- Error while initializing data.
                Invalid TM data type. Must be pandas DataFrame.
        """
        super().__init__()
        # Set up default value
        try:
            ### INIT SELF.PATH
            # Only accepts file path and csv extension
            if os.path.isfile(path) and path.endswith('.csv'):
                self._path = path # Set up property for self.path
                _, self.ext = os.path.splitext(path)
                self.basename = os.path.basename(path)
            else:
                raise Exception('Error while initializing path: '
                    f'Not a file path or csv extension: {path}')
            
            self.backup_path = self.correct_path_os(
                f"{os.environ['appdata']}\\AIO Translator\\Backup\\"
                    f"{self.basename}_backup{self.ext}")
            self.tm_version = 4
            ### INIT SELF.DATA
            data = pd.read_csv(self.path, usecols=self.supported_languages)
            # Only retrieve data from pandas DataFrame
            if isinstance(data, pd.DataFrame):
                self._data = data
            else:
                raise TypeError('Error while initializing TM data. '
                    f'Invalid TM data type: {type(data)}. '
                    'Must be pandas DataFrame.')
        
        except Exception as e:
            print('Error while initializing TM file: ', e)

    @property
    def path(self):
        """path attribute of the class."""
        return self._path

    @path.setter
    def path(self, path: str):
        """Set path attribute via self._path.
        
        Validate the path to TM file when initializing a class instance.
        Also set the basename of the TM file.
        Supported extension: .csv

        Args:
            path -- str path that gets directly on initialization.

        Raises:
            Exception -- Error while initializing TM path in {__class__}.
            Exception -- Cannot initialize TM file path because path
                is not a file.
            TypeError -- Incorrect file extension. Must be .csv.
        """
        try:
            if os.path.isfile(path):
                _, file_ext = os.path.splitext(path)
                if file_ext == '.csv':
                    self.basename = os.path.basename(path)
                    self.ext = '.csv'
                    self._path = self.correct_path_os(path)
                else:
                    raise TypeError(f'Incorrect file format: {file_ext}. '
                        'Must be .csv.')
            else:
                raise Exception('Cannot initialize TM file path '
                    'because path is not a file: ', path)
        except Exception as e:
            print(f'Error while initializing TM path in {__class__}: ', e)


    def correct_path_os(self, path) -> str:
        """Replace backward slash with forward slash.

        Replace if OS is not Windows.
        
        Args:
            path -- Path to replace backward slash.

        Returns:
            A str path with backward slash is replaced with forward slash
            if OS is not Windows.
        """
        if not sys.platform.startswith('win'):
            return str(path).replace('\\', '//')
        return path

    def export_data_to_file(self):
        """Create a csv file with the data."""
        self.data.to_csv(self.path)

    ### NOT USED: VER 1.1
    # def is_csv(self, path: str):
    #     """Validate if a file is csv extension.
        
    #     Args:
    #         path -- Path of the TM file to validate.
    #     """
    #     if path.endswith('.csv'):
    #         return True
    #     else:
    #         return False

    ### DEPRICATED: VER 1.0
    # def get_data(self):
    #     """Retrieve data from TM File.

    #     Only allow pandas DataFrame type.

    #     Returns:
    #         pandas DataFrame in the TM file.

    #     Raises:
    #         TypeError -- Invalid data type.
    #             Data type is not an instance of DataFrame
    #     """
    #     # Only accept DataFrame type data
    #     data = pd.read_csv(self.path, usecols=self.supported_languages)
    #     if isinstance(data, pd.DataFrame):
    #         return data
    #     else:
    #         raise TypeError('Invalid data type. Data type is not '
    #             'an instance of DataFrame: ', type(data))
    
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

class CloudTranslationMemoryFile(TranslationMemoryFile):
    """TM file object in Google Cloud Storage.
    
    Info about TM file such as file name, data in the TM and methods to
    modify them.
    Most of the attributes should not be changed by any means except the
    following: data.

    Attributes:
        bucket -- Bucket in the cloud storage. Currently using Google Cloud
            Storage by default.
        glossary_id -- Name of the project.
        path -- The URI path of the TM in cloud storage.
        ext -- TM file extension. Only support .csv. (default '.csv')
        blob -- A dict/object containing info and data of a specific
            cloud storage.
        basename -- File basename.
        tm_version -- TM version. (default 4)
        supported_languages -- Languages that the TM supports. Used to
            select columns in self.data DataFrame.
        data -- @property Data in the TM. Accept only pandas DataFrame class.
    """
    def __init__(self,
            license_path: str, *,
            bucket_id: str,
            glossary_id: str):
        """
        Args:
            license_path -- Path to the required license file
                to access the cloud storage.
            bucket_id -- Name of the bucket in the cloud storage.
            glossary_id -- Name of the project.
        
        Raises:
            Exception - Error while setting up license.
        """
        super().__init__()
        try:
            ### CLOUD STORAGE SET UP
            ### SET UP LICENSE
            try:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = license_path
            except Exception as e:
                print(f'Error while setting up license in Cloud TM file: {e}')
            self.bucket = storage.Client().get_bucket(bucket_id)
            # For more security, in the future, may need to add
            # a validation to check if glossary_id exists in a supported list
            # in another blob.
            self.glossary_id = glossary_id
            self.path = f"TM/{self.glossary_id}/TM_{self.glossary_id}" \
                f"{self.ext}"
            self.basename = os.path.basename(self.path)
            ### INIT SELF.BLOB
            try:
                self.blob = self.bucket.get_blob(self.path)
            except Exception as e:
                print('Error while intitializing blob in Cloud TM file: ', e)
            
            ### INIT SELF.DATA
            self._data = self.get_data_from_blob()
        except Exception as e:
            print('Error while initializing Cloud TM file: ', e)


    def get_data_from_blob(self):
        """Retreive and return TM data from the blob.
        
        Raises:
            Exception -- Error while getting data from Cloud TM blob.
        """
        try:
            stringio_data = StringIO(self.blob.download_as_text())
            # Convert to pandas DataFrame since data must be a DataFrame
            # instance.
            # Without dtype paramater, "DtypeWarning: Columns (x)
            # have mixed types" warning will occur
            df = pd.read_csv(
                stringio_data,
                sep=',',
                dtype={lang: str for lang in self.supported_languages})
            return df
        except Exception as e:
            print(f'Error while getting data from Cloud TM blob: {e}')

    def upload_to_blob(self, path: str):
        """Upload the TM file to the blob.
        
        Args:
            path -- Path to the local TM file on user computer.

        Raises:
            Exception -- Error while uploading TM file to Cloud TM blob.
        """
        try:
            if self.blob != None:
                self.blob.upload_from_filename(path)
                print('Uploaded the blob to cloud.')
            # Create a new blob if not exist by using blob object
            # instead of get_blob method
            else:
                blob = self.bucket.blob(self.path)
                blob.upload_from_filename(path)
                print('A new blob has been created for cloud TM upload.')
        except Exception as e:
            print(f'Error while uploading TM file to the Cloud TM blob: {e}')



### TEST RUN ################################################################
# bucket_id = 'nxvnbucket'
# glossary_id = 'MSM'


# tm_file = LocalTranslationMemoryFile(test_path)
# # tm_file.path = 'bca'
# print(tm_file.path)
# print(tm_file.ext)
# # print(tm_file.data)


# gcs_tm_file = CloudTranslationMemoryFile(
#     license_path,
#     bucket_id=bucket_id,
#     glossary_id=glossary_id)
# # print(gcs_tm_file.data)
# gcs_tm_file.upload_to_blob(test_path)

# mydata = gcs_tm_file.get_data()
# print(type(mydata))
