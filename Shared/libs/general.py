import sys
import os

def get_version(version_number=1000):
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
