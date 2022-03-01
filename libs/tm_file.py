"""TM file class module.

Include the info about the TM and methods to modify TM data.
"""

__version__ = '1.2'
__author__ = 'anonymous'

# System, standard libs
import os
import sys
from datetime import datetime
import re
from io import StringIO
import json

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
        info_ext -- TM info file extension. Support .json (default '.json')
        data -- @property Data in the TM. Accept only pandas DataFrame class.
        supported_languages -- Languages that the TM supports. Used to
            select columns in self.data DataFrame.
        length -- Length len(data) of the DataFrame data in TM file.
        last_modified -- Time when data is modified.
    """
    def __init__(self):
        # Set up default value
        self.ext = '.csv'
        self.info_ext = '.json'
        self._data = pd.DataFrame()
        self.supported_languages = ['ko', 'en', 'cn', 'jp', 'vi']
        self.length = 0
        self.last_modified = None

    @property
    def data(self):
        """data attribute of the class"""
        return self._data

    @data.setter
    def data(self, data):
        """Validate data set to self.data.

        Only allow pandas DataFrame type.
        Also update the last modified time.

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
            self.length = len(data)
            self.last_modified = datetime.now()
        else:
            raise TypeError('Invalid data type. Data type is not '
                f'an instance of DataFrame: {type(data)}' )
    

    def append_datetime(self):
        """Return a string of the current time format using datetime.now().
        
        The decimal in second is removed. Purpose is to add the current time
        to a file name.
        """
        # Convert to string and replace ":" in time format
        now = str(datetime.now()).split('.')[0].replace(':', '')
        return ('_' + now.replace('-', ''))

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

###############################################################################
### LocalTranslationMemoryFile CLASS
###############################################################################
class LocalTranslationMemoryFile(TranslationMemoryFile):
    """TM file object on a user computer.
    
    Info about TM file such as file name, data in the TM and methods to
    modify them.

    Attributes:
        path -- @property path to the TM file. Path is validated depending
            on the OS.
        backup_path -- Path of the backup TM file. Path is validated depending
            on the OS.
        info_path -- Path to the TM info file. Path is validated depending
            on the OS.
        ext -- TM file extension. Only support .csv. (default '.csv')
        info_ext -- TM info file extension. Support .json (default '.json')
        tm_version -- TM version. (default 4)
        supported_languages -- Languages that the TM supports. Used to
            select columns in self.data DataFrame.
        data -- @property Data in the TM. Accept only pandas DataFrame class.
        length -- Length len(data) of the DataFrame data in TM file.
        info_ext -- Extension of TM info file.
        last_modified -- Time when data is modified. Loads value from
            TM info file on init. If there's no info file, create a new one.
    """
    def __init__(self, path: str):
        """
        Args:
            path -- Path to the TM file.

        Raises:
            Exception -- Error while initializing path: Not a file path
                or csv extension.
            Exception -- Error while loading TM info file on init.
            TypeError -- Error while initializing data.
                Invalid TM data type. Must be pandas DataFrame.
        """
        super().__init__()
        # Set up default value
        try:
            ### INIT SELF.PATH, SELF.INFO_PATH, SELF.INFO_EXT,
            ### SELF.LAST_MODIFIED
            # Only accepts file path and csv extension
            # Init other paths along the way
            if os.path.isfile(path) and path.endswith('.csv'):
                self._path = path # Set up property for self.path
                tm_file_root, self.ext = os.path.splitext(path)
                tm_filename = os.path.basename(tm_file_root)
                self.info_path = self.correct_path_os(
                    f'{tm_file_root}_info.{self.info_ext}')
                # Load the TM info file to get last_modified value in a
                # json format.
                try:
                    if os.path.exists(self.info_path) and \
                            os.path.isfile(self.info_path):
                        with open(self.info_path, 'r') as tm_info_file:
                            tm_info_data = json.loads(tm_info_file.read())
                            self.last_modified = datetime.fromtimestamp(
                                tm_info_data['last_modified'])
                    # Create a new file if the file doesn't exist
                    else:
                        with open(self.info_path, 'w') as tm_info_file:
                            self.last_modified = datetime.now()
                            tm_info_data = {
                                'last_modified': datetime.timestamp(
                                    self.last_modified)
                            }
                            tm_info_file.write(json.dumps(tm_info_data))
                except Exception as e:
                    print(f'Error while loading TM info file on init: {e}')
            else:
                raise Exception('Error while initializing path: '
                    f'Not a file path or csv extension: {path}')
            
            ### INIT BACKUP PATH: SELF.BACKUP_PATH
            if sys.platform.startswith('win'):
                self.backup_path = self.correct_path_os(
                    f"{os.environ['APPDATA']}\\AIO Translator\\Backup\\"
                        f"{tm_filename}_backup{self.ext}")
            else:
                self.backup_path = os.getcwd()
            self.tm_version = 4
            ### INIT SELF.DATA, SELF.LENGTH
            data = pd.read_csv(self.path, usecols=self.supported_languages)
            # Only retrieve data from pandas DataFrame
            if isinstance(data, pd.DataFrame):
                # Use self._data instead of self.data so that last_modified
                # attribute won't be changed when loading the TM
                # on program start because of the parent class
                self._data = data
                self.length = len(data)
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
    def path(self, tm_path: str):
        """Set path attribute via self._path.
        
        Validate the path to TM file when initializing a class instance.
        Path is validated depending on the OS.
        Also set the basename of the TM file.
        Supported extension: .csv
        Assign value to the path to the TM info file along the way.

        Args:
            path -- str path that gets directly on initialization.

        Raises:
            Exception -- Error while initializing TM path in {__class__}.
            Exception -- Cannot initialize TM file path because path
                is not a file.
            TypeError -- Incorrect file extension. Must be .csv.
        """
        try:
            if os.path.isfile(tm_path):
                tm_file_root, tm_file_ext = os.path.splitext(tm_path)
                if tm_file_ext == '.csv':
                    self.ext = '.csv'
                    self._path = self.correct_path_os(tm_path)
                    self.info_path = f'{tm_file_root}_info.{self.info_ext}'
                else:
                    raise TypeError(f'Incorrect file extension: '
                        f'{tm_file_ext}. Must be .csv.')
            else:
                raise Exception('Cannot initialize TM file path '
                    'because path is not a file: ', tm_path)
        except Exception as e:
            print(f'Error while initializing TM path in {__class__}: ', e)


    def write_file(self):
        """Create a csv file with the data and json file with info data.
        
        Raises:
            Exception -- Error while writing TM files.
        """
        try:
            self.data.to_csv(self.path)
            with open(self.info_path, 'w') as tm_info_file:
                tm_info_data = {
                    'last_modified': self.last_modified
                }
                tm_info_file.write(json.dumps(tm_info_data))
        except Exception as e:
            print(f'Error while writing TM files: {e}')


###############################################################################
### CloudTranslationMemoryFile CLASS
###############################################################################
class CloudTranslationMemoryFile(TranslationMemoryFile):
    """TM file object in Google Cloud Storage.
    
    Info about TM file such as file name, data in the TM and methods to
    modify them.
    Most of the attributes should not be changed by value assignment
    except the following: data.

    Attributes:
        bucket -- Bucket in the cloud storage. Currently using Google Cloud
            Storage by default.
        glossary_id -- Name of the project.
        path -- The URI path of the TM in cloud storage.
        info_path -- The URI path of the TM info file in cloud storage.
        local_path -- Path to the local file on user computer. The local
            file is used to load data when there's no new update about
            the TM on cloud storage. Path is validated depending
            on the OS.
        ext -- TM file extension. Only support .csv. (default '.csv')
        info_ext -- TM info file extension. Support .json (default '.json')
        blob -- A dict/object containing the data of TM file on a specific
            cloud storage.
        info_blob -- A dict/object containing the data of TM info file
            on a specific cloud storage.
        basename -- File basename.
        tm_version -- TM version. (default 4)
        supported_languages -- Languages that the TM supports. Used to
            select columns in self.data DataFrame.
        data -- @property Data in the TM. Accept only pandas DataFrame class.
            Data first checks the data from local_path
        length -- Length len(data) of the DataFrame data in TM file.
        last_modified -- Time when data is modified. Currently this class
            is not used this attribute.
        upload_time -- Time when TM file is uploaded to the cloud storage.
    """
    def __init__(self,
            license_path: str, *,
            bucket_id: str,
            glossary_id: str):
        """
        A local path to local TM file will be created if it doesn't exist.

        Args:
            license_path -- Path to the required license file
                to access the cloud storage. Mostly selected from the UI.
            bucket_id -- Name of the bucket in the cloud storage.
            glossary_id -- Name of the project.
        
        Raises:
            Exception -- Error while setting up license in Cloud TM file.
            Exception -- Error while loading TM data in cloud TM class on init.
            Exception -- Error while intitializing blob in Cloud TM file.
            Exception -- Error while initializing Cloud TM file.
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
            # The exceptions already include empty blob handling
            try:
                self.blob = self.bucket.get_blob(self.path)
            except Exception as e:
                print('Error while intitializing blob in Cloud TM file: ', e)
            ### INIT SELF.INFO_BLOB
            self.info_ext = '.json'
            self.info_path = f"TM/{self.glossary_id}/TM_{self.glossary_id}" \
                f"_info{self.info_ext}"
            self.info_blob = self.bucket.get_blob(self.info_path)
            
            self.upload_time = None
            ### INIT LOCAL PATH: SELF.LOCAL_PATH
            if sys.platform.startswith('win'):
                local_dir = self.correct_path_os(
                    f"{os.environ['APPDATA']}\\AIO Translator\\TM")
                self.local_path = self.correct_path_os(
                    f'{local_dir}\\TM_{glossary_id}{self.ext}')
            else:
                self.local_path = os.getcwd()
            ### INIT SELF.DATA, SELF.LENGTH
            # Use self._data instead of self.data so that last_modified
            # attribute won't be changed when loading the TM
            # on program start because of the parent class.
            # Check if local path is a TM file, it means that there's
            # already a local TM file to load the data from. If there's
            # no TM file, download file from the blob and load data from it.
            try:
                if os.path.exists(self.local_path) and \
                        os.path.isfile(self.local_path):
                    self._data = pd.read_csv(self.local_path)
                    print('Successfully loaded data from local TM.')
                else:
                    os.mkdir(local_dir)
                    self.download_from_blob(self.local_path)
                    self._data = pd.read_csv(self.local_path)
                    print('Successfully loaded data from local TM.')
            except Exception as e:
                print('Error while loading TM data in cloud TM class on init: '
                    f'{e}')
        except Exception as e:
            print('Error while initializing Cloud TM file: ', e)


    def download_from_blob(self, destination_path):
        """Download TM file on cloud storage.
        
        Raises:
            Exception -- Error while downloading TM file on cloud storage.
        """
        try:
            self.blob.download_to_filename(destination_path)
            print(f'Downloaded TM file from {self.path} blob to '
                f'{destination_path} on local device.')
        except Exception as e:
            print(f'Error while downloading TM file on cloud storage: {e}')


    def download_data_from_blob(self):
        """Download and return TM data from the blob.

        Also download the TM info from info blob.
        
        Raises:
            Exception -- Error while getting data from Cloud TM blob.
        """
        try:
            stringio_data = StringIO(self.blob.download_as_text())
            # Convert to pandas DataFrame since data must be a DataFrame
            # instance.
            # Without dtype paramater, "DtypeWarning: Columns (x)
            # have mixed types" warning will occur
            data = pd.read_csv(
                stringio_data,
                sep=',',
                dtype={lang: str for lang in self.supported_languages})
            self.length = len(data)
            # TM info
            # tm_info_data is json format
            tm_info_data = json.loads(self.info_blob.download_as_text())
            self.upload_time = datetime.fromtimestamp(
                tm_info_data['upload_timestamp'])
            return data
        except Exception as e:
            print(f'Error while getting data from Cloud TM blob: {e}')

    def upload_to_blob(self, local_path: str):
        """Upload the TM file to the blob.
        
        Args:
            local_path -- Path to the local TM file on user computer
            to upload the file.

        Raises:
            Exception -- Error while uploading TM file to Cloud TM blob.
        """
        try:
            tm_info_data = {
                'upload_timestamp': datetime.now().timestamp(),
            }

            if self.blob != None or self.info_blob != None:
                self.blob.upload_from_filename(local_path)
                # Record the upload time and length in another blob
                self.info_blob.upload_from_string(json.dumps(tm_info_data))
                print('Uploaded TM to cloud.')
            # Create a new blob if not exist by using blob object
            # instead of get_blob method
            else:
                blob = self.bucket.blob(self.local_path)
                info_blob = self.bucket.blob(self.info_path)
                blob.upload_from_filename(local_path)
                # Record the upload time and length in another blob
                info_blob.upload_from_string(json.dumps(tm_info_data))
                print('New blobs have been created for cloud TM upload.')
        except Exception as e:
            print('Error while uploading TM file and info file to the '
                f'cloud storage: {e}')



### TEST RUN ################################################################
test_path = r''
license_path = r''
bucket_id = 'nxvnbucket'
glossary_id = 'MSM'

# tm_file = LocalTranslationMemoryFile(test_path)
# print(tm_file.path)
# print(tm_file.ext)
# print(tm_file.length)
# print(tm_file.last_modified)

# gcs_tm_file = CloudTranslationMemoryFile(
#     license_path,
#     bucket_id=bucket_id,
#     glossary_id=glossary_id)
# # print(gcs_tm_file.data)
# # gcs_tm_file.upload_to_blob(test_path)
# gcs_tm_file.get_data_from_blob()
