from libs.grammarcheck import LanguageTool
import os
print('Language tool require Java Runtime to be installed.')
print('If you don\'t, please download it here:')
print(r'https://www.java.com/en/download/manual.jsp')
try:
	download_path = os.environ.get('LTP_PATH',os.path.join(os.path.expanduser("~"), ".cache", "language_tool_python"))
	print('Language tool path:', download_path)
	if os.path.isdir(download_path):
		LangTool = LanguageTool('en')
	else:
		print('Downloading Language tool:')
		LangTool = LanguageTool('en')
except Exception as e:
	print("Error", e)
	print('Language Tool disabled.')
