from libs.import_languages import print_workbook
from pkgutil import get_data
from openpyxl import load_workbook
#from io import BytesIO

try:
    print_workbook()
except Exception as _error_message:
    print(_error_message)


try:
    f = open("version.txt", "r")
    print(f.read())
except Exception as _error_message:
    print(_error_message)


try:
    version = get_data('src', 'version.txt' )
    text_version = version.decode('UTF-8', 'ignore')
except Exception as _error_message:
    print(_error_message)


try:
    version = get_data('src', './version.txt' )
    text_version = version.decode('UTF-8', 'ignore')
except Exception as _error_message:
    print(_error_message)


try:
    version = get_data('src', './version.txt' )
    text_version = version.decode('UTF-8', 'ignore')
except Exception as _error_message:
    print(_error_message)


try:
    f = open("/version.txt", "r")
    print(f.read())
except Exception as _error_message:
    print(_error_message)

