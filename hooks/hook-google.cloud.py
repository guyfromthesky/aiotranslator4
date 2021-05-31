from PyInstaller.utils.hooks import copy_metadata, collect_data_files
datas = copy_metadata('google-cloud-core')
datas += collect_data_files('grpc')
