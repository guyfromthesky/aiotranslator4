import sys
import os


def get_version(rev):
	a,b,c,d = list(str(rev))
	return a + '.' + b + '.' + c + chr(int(d)+97)

def get_version_from_file():
	version_file = resource_path('resource/version.txt')
	if os.path.isfile(version_file):
		pass
	else:
		version_file = r'\scr\version.txt'
	f = open(version_file, "r")
	version_number = f.read()
	a,b,c,d = list(str(version_number))
	return a + '.' + b + '.' + c + chr(int(d)+97)

def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)

def get_user_name():
	if sys.platform.startswith('win'):
		try:
			user_name = os.getlogin()
		except:
			user_name = os.environ['COMPUTERNAME']
	else:
		try:
			user_name = os.environ['LOGNAME']
		except:
			user_name = "Anonymous"
	return user_name

def send_fail_request(error_message, ver_num):
	try:
		from google.cloud import logging
		from libs.aioconfigmanager import ConfigLoader
		from tkinter import messagebox
		AppConfig = ConfigLoader(Document=True)
		Configuration = AppConfig.Config
		
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Configuration['license_file']['path']
		client = logging.Client()
	except:
		messagebox.showinfo(title='Critical error', message=error_message)
		return

	log_name = 'critical-error'
	logger = client.logger(log_name)
	
	try:
		if sys.platform.startswith('win'):
			try:
				user_name = os.getlogin()
			except:
				user_name = os.environ['COMPUTERNAME']
		else:
			try:
				user_name = os.environ['LOGNAME']
			except:
				user_name = "Anonymous"
	except:
		user_name = "Anonymous"

	data_object = {
		'tool': 'Document Translator',
		'translator_ver': ver_num,
		'error_message': str(error_message)
	}

	tracking_object = {
		'user': user_name,
		'details': data_object
	}
	
	try:
		logger.log_struct(tracking_object)
	except Exception  as e:
		print('exception:', e)
		result = False
	return