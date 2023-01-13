"""Module to modify the config.

To add a new setting, add the related to Init_Setting functions first.
"""

#Regular expression handling
import re
import configparser
#http request and parser
# Base64 convert
import base64
#System lib
import os
import sys

class ConfigLoader:
	def __init__(self, Writer = False, Document = False):
		self.basePath = os.path.abspath(os.path.dirname(sys.argv[0]))
		if sys.platform.startswith('win'):
			self.appdata = os.environ['APPDATA'] + '\\AIO Translator'
		else:
			self.appdata = os.getcwd() + self.correct_path_os('\\AIO Translator')
	
		# Config file
		self.Translator_Config_Path = self.appdata + self.correct_path_os('\\translator.ini')
		self.Theme_Config_Path = self.appdata + self.correct_path_os('\\theme.ini')
		
		if Document == True:
			self.Doc_Config_Path = self.appdata + self.correct_path_os('\\doc.ini')
		if Writer == True:
			self.Writer_Config_Path = self.appdata + self.correct_path_os('\\writer.ini')
			self.Custom_Writer_Config_Path = self.appdata + self.correct_path_os('\\custom_writer.ini')
		# Folder
		self.TM_Backup_Folder_Path = self.appdata + self.correct_path_os('\\TM')

		self.LocalTM = self.appdata + self.correct_path_os('\\Local.pkl')

		self.Config = {}
		self.Document = Document
		self.Writer = Writer
		# Generate app folder (os.environ['APPDATA'] + '\\AIO Translator)
		self.initFolder()

		self.Translator_Init_Setting()
		self.Theme_Init_Setting()

		if self.Writer == True:
			self.Writer_Init_Setting()
		if self.Document == True:
		
			self.Doc_Init_Setting()
	
		
		#self.Initconfig()
		#self.Init_DB_Config()
		
	def correct_path_os(self, path):
		if not sys.platform.startswith('win'):
			return str(path).replace('\\', '/')
		return path

	def initFolder(self):
		if not os.path.isdir(self.appdata):
			print("No app data folder, create one")
			#No config, create one
			try:
				os.mkdir(self.appdata)
			except OSError:
				print ("Creation of the directory %s failed" % self.appdata)
			else:
				print ("Successfully created the directory %s " % self.appdata)
			#Check local database

	def Custom_Writer_Init_Setting(self):

		config_path = self.Custom_Writer_Config_Path

		if not os.path.isfile(config_path):
			config = configparser.ConfigParser()
			with open(config_path, 'w') as configfile:
				config.write(configfile)

		config = configparser.ConfigParser()
		config.read(config_path, encoding='utf-8-sig')
		Section = 'Custom_Writer'

		if not config.has_section(Section):
			config.add_section(Section)
			self.Config[Section] = {}

		self.Init_Config_Option(config, Section, 'sec_1_title', "Details")
		self.Init_Config_Option(config, Section, 'sec_2_title', "Reproduce Step")
		self.Init_Config_Option(config, Section, 'sec_3_title', "Reproducibility")
		self.Init_Config_Option(config, Section, 'sec_4_title', "Expected result")
		self.Init_Config_Option(config, Section, 'sec_5_title', "Environmental Information")
		self.Init_Config_Option(config, Section, 'sec_6_title', "")

		self.Init_Config_Option(config, Section, 'sec_1_row', 7)
		self.Init_Config_Option(config, Section, 'sec_2_row', 5)
		self.Init_Config_Option(config, Section, 'sec_3_row', 1)
		self.Init_Config_Option(config, Section, 'sec_4_row', 3)
		self.Init_Config_Option(config, Section, 'sec_5_row', 15)
		self.Init_Config_Option(config, Section, 'sec_6_row', 0)



		
		Section = 'Simple_Translator'
		if not config.has_section(Section):
			config.add_section(Section)
			self.Config[Section] = {}
		self.Init_Config_Option(config, Section, 'target_lang', 2)
		self.Init_Config_Option(config, Section, 'source_lang', 3)
		self.Init_Config_Option(config, Section, 'secondary_target_lang', 5)


		with open(config_path, 'w') as configfile:
			config.write(configfile)

	def Writer_Init_Setting(self):

		config_path = self.Writer_Config_Path

		if not os.path.isfile(config_path):
			config = configparser.ConfigParser()
			#config.add_section('Document_Translator')
			with open(config_path, 'w') as configfile:
				config.write(configfile)

		config = configparser.ConfigParser()
		config.read(config_path, encoding='utf-8-sig')
		Section = 'Bug_Writer'

		if not config.has_section(Section):
			config.add_section(Section)
			self.Config[Section] = {}

		

		self.Init_Config_Option_Numberic(config, Section, 'target_lang', 1)
		self.Init_Config_Option_Numberic(config, Section, 'source_lang', 2)
		self.Init_Config_Option_Numberic(config, Section, 'secondary_target_lang', 6)

		
		self.Init_Config_Option_Numberic(config, Section, 'test_info_inable', 1)
		self.Init_Config_Option_Numberic(config, Section, 'use_simple_template', 0)
		self.Init_Config_Option_Numberic(config, Section, 'usage', 0)
		
		self.Init_Config_Option(config, Section, 'app_lang', 'en')

		self.Init_Config_Option_Float(config, Section, 'Transparent', 97)
		self.Init_Config_Option(config, Section, 'BackgroundColor', "")
		self.Init_Config_Option(config, Section, 'ForcegroundColor', "")
		self.Init_Config_Option(config, Section, 'FrameColor', "")
		self.Init_Config_Option(config, Section, 'MenuColor', "")
		self.Init_Config_Option(config, Section, 'UsedTheme', "", True)
		
		self.Init_Config_Option(config, Section, 'theme_name', "minty", True)
		self.Init_Config_Option(config, Section, 'font_size', "12", True)
		Section = 'BugDetails'
		
		self.Init_Config_Option(config, Section, 'TextTitle', "", True)
		self.Init_Config_Option(config, Section, 'TextServer', "", True)
		self.Init_Config_Option(config, Section, 'TextClient', "", True)
		self.Init_Config_Option(config, Section, 'TextReprodTime', "", True)
		self.Init_Config_Option(config, Section, 'TextAccount', "", True)

		self.Init_Config_Option(config, Section, 'EnvInfo', "", True)
		self.Init_Config_Option(config, Section, 'Precondition', "", True)
		self.Init_Config_Option(config, Section, 'Reproducibility', "", True)

		self.Init_Config_Option(config, Section, 'TextTestReport', "", True)
		self.Init_Config_Option(config, Section, 'TextReproduceSteps', "", True)
		self.Init_Config_Option(config, Section, 'TextShouldBe', "", True)
		self.Init_Config_Option(config, Section, 'HeaderA', "")
		self.Init_Config_Option(config, Section, 'HeaderB', "")

		Section = 'NXLog'
		self.Init_Config_Option(config, Section, 'table', "", True)
		self.Init_Config_Option(config, Section, 'column', "", True)
		self.Init_Config_Option(config, Section, 'jsondata', "", True)
		self.Init_Config_Option(config, Section, 'nx_TextTestReport', "", True)
		self.Init_Config_Option(config, Section, 'nx_TextShouldBe', "", True)
		self.Init_Config_Option(config, Section, 'nx_TextTitle', "", True)

		Section = 'Temp_BugDetails'
		self.Init_Config_Option(config, Section, 'TextTitle', "", True)

		self.Init_Config_Option(config, Section, 'TextServer', "", True)
		self.Init_Config_Option(config, Section, 'TextClient', "", True)
		self.Init_Config_Option(config, Section, 'TextReprodTime', "", True)
		self.Init_Config_Option(config, Section, 'TextAccount', "", True)

		self.Init_Config_Option(config, Section, 'EnvInfo', "", True)
		self.Init_Config_Option(config, Section, 'Precondition', "", True)
		self.Init_Config_Option(config, Section, 'Reproducibility', "", True)

		self.Init_Config_Option(config, Section, 'TextTestReport', "", True)
		self.Init_Config_Option(config, Section, 'TextReproduceSteps', "", True)
		self.Init_Config_Option(config, Section, 'TextShouldBe', "", True)
		self.Init_Config_Option(config, Section, 'HeaderA', "")
		self.Init_Config_Option(config, Section, 'HeaderB', "")

		self.Init_Config_Option(config, Section, 'SimpleTranslator', "", True)
		
		## BUG WRITER_V2 TAB
		Section = 'Temp_BugDetails_v2'
		self.Init_Config_Option(config, Section, 'Header A', "")
		self.Init_Config_Option(config, Section, 'Header B', "")
		self.Init_Config_Option(config, Section, 'Bug Title', "", True)
		self.Init_Config_Option(config, Section, 'Reproduce Steps', "", True)
		self.Init_Config_Option(config, Section, 'Expected Results', "", True)
		self.Init_Config_Option(config, Section, 'Description', "", True)

		#BG_CL = None
		#FG_CL = None
		#FRAME_BG = None
		#MENU_BG = None
		#FOLK_BLUE = None
		
		Section = 'Simple_Translator'
		if not config.has_section(Section):
			config.add_section(Section)
			self.Config[Section] = {}
		self.Init_Config_Option_Numberic(config, Section, 'target_lang', 1)
		self.Init_Config_Option_Numberic(config, Section, 'source_lang', 2)
		self.Init_Config_Option_Numberic(config, Section, 'secondary_target_lang', 5)
		self.Init_Config_Option(config, Section, 'SourceText', "", True)
		self.Init_Config_Option(config, Section, 'TargetText', "", True)

		Section = 'Temp_NXLog'
		if not config.has_section(Section):
			config.add_section(Section)
			self.Config[Section] = {}
		self.Init_Config_Option(config, Section, 'table', "", True)
		self.Init_Config_Option(config, Section, 'column', "", True)
		self.Init_Config_Option(config, Section, 'jsondata', "", True)
		self.Init_Config_Option(config, Section, 'nx_TextTestReport', "", True)
		self.Init_Config_Option(config, Section, 'nx_TextShouldBe', "", True)
		self.Init_Config_Option(config, Section, 'nx_TextTitle', "", True)

		with open(config_path, 'w') as configfile:
			config.write(configfile)



	def Doc_Init_Setting(self):

		config_path = self.Doc_Config_Path

		if not os.path.isfile(config_path):
			config = configparser.ConfigParser()
			with open(config_path, 'w') as configfile:
				config.write(configfile)

		config = configparser.ConfigParser()

		config.read(config_path, encoding='utf-8-sig')
		Section = 'Document_Translator'

		if not config.has_section(Section):
			config.add_section(Section)
			self.Config[Section] = {}

		self.Init_Config_Option(config, Section, 'app_lang', 'en')
		#self.Init_Config_Option(config, Section, 'translation_memory', self.LocalTM, True)
		
		

		self.Init_Config_Option_Numberic(config, Section, 'target_lang', 1)
		self.Init_Config_Option_Numberic(config, Section, 'source_lang', 2)

		

		self.Init_Config_Option_Numberic(config, Section, 'speed_mode', 0)
		self.Init_Config_Option_Numberic(config, Section, 'bilingual', 0)
		self.Init_Config_Option_Numberic(config, Section, 'value_only', 0)
		self.Init_Config_Option_Numberic(config, Section, 'file_name_correct', 1)
		self.Init_Config_Option_Numberic(config, Section, 'file_name_translate', 1)
		self.Init_Config_Option_Numberic(config, Section, 'sheet_name_translate', 1)
		self.Init_Config_Option_Numberic(config, Section, 'tm_translate', 1)
		self.Init_Config_Option_Numberic(config, Section, 'tm_update', 1)
		self.Init_Config_Option_Numberic(config, Section, 'remove_unselected_sheet', 0)
		self.Init_Config_Option_Numberic(config, Section, 'usage', 0)
		
		self.Init_Config_Option_Float(config, Section, 'Transparent', 97)
		self.Init_Config_Option(config, Section, 'theme_name', "minty", True)
		self.Init_Config_Option(config, Section, 'font_size', "12", True)


		with open(config_path, 'w') as configfile:
			config.write(configfile)

	def Translator_Init_Setting(self):
		Section = 'Translator'

		config_path = self.Translator_Config_Path

		if not os.path.isfile(config_path):
			config = configparser.ConfigParser()
			config.add_section('Translator')

			with open(config_path, 'w') as configfile:
				config.write(configfile)

		
		config = configparser.ConfigParser()
		config.read(config_path)

		self.Init_Config_Option(config, Section, 'bucket_id', 'nxvnbucket')
		self.Init_Config_Option(config, Section, 'db_list_uri', 'config/db_list.csv')
		self.Init_Config_Option(config, Section, 'project_bucket_id', 'credible-bay-281107')
		#self.Init_Config_Option(config, Section, 'license_key', '')
		self.Init_Config_Option(config, Section, 'glossary_id', '')
		self.Init_Config_Option(config, Section, 'license_file', '', True)
		self.Init_Config_Option(config, Section, 'translation_memory', self.LocalTM, True)
		
		with open(config_path, 'w') as configfile:
			config.write(configfile)
	
	def Theme_Init_Setting(self):
		Section = 'Theme'

		config_path = self.Theme_Config_Path

		if not os.path.isfile(config_path):
			config = configparser.ConfigParser()
			config.add_section('Theme')

			with open(config_path, 'w') as configfile:
				config.write(configfile)

		
		config = configparser.ConfigParser()
		config.read(config_path)

		self.Init_Config_Option(config, Section, 'primary', '#0080ff')
		self.Init_Config_Option(config, Section, 'secondary', '#94a2a4')
		self.Init_Config_Option(config, Section, 'success', '#44aca4')
		self.Init_Config_Option(config, Section, 'info', '#3f98d7')
		self.Init_Config_Option(config, Section, 'warning', '#d05e2f')
		self.Init_Config_Option(config, Section, 'danger', '#d95092')
		self.Init_Config_Option(config, Section, 'light', '#A9BDBD')
		self.Init_Config_Option(config, Section, 'dark', '#073642')
		self.Init_Config_Option(config, Section, 'bg', '#002B36')
		self.Init_Config_Option(config, Section, 'fg', '#ffffff')
		self.Init_Config_Option(config, Section, 'selectbg', '#0b5162')
		self.Init_Config_Option(config, Section, 'selectfg', '#ffffff')
		self.Init_Config_Option(config, Section, 'border', '#00252e')
		self.Init_Config_Option(config, Section, 'inputfg', '#A9BDBD')
		self.Init_Config_Option(config, Section, 'inputbg', '#073642')
		self.Init_Config_Option(config, Section, 'active', '#002730')

		
		
		with open(config_path, 'w') as configfile:
			config.write(configfile)

	# Function will load the value from selected option.
	# If value does not exist, return the default value
	def Init_Config_Option(self, Config_Obj, Section, Option, Default_Value, Encoded = False):
		# Config does not exist
		if not Section in self.Config:
			self.Config[Section] = {}
		# Config does not have that section
		if not Config_Obj.has_section(Section):
			Config_Obj.add_section(Section)
			Config_Obj.set(Section, Option, str(Default_Value))
			self.Config[Section][Option] = Default_Value
		# Config have that section
		else:
			# The section does not have that option
			if not Config_Obj.has_option(Section, Option):
				Config_Obj.set(Section, Option, str(Default_Value))
				self.Config[Section][Option] = Default_Value
			# The section have that option
			else:
				Value = Config_Obj[Section][Option]
				if Encoded == False:
					if Value.isnumeric():
						self.Config[Section][Option] = int(Config_Obj[Section][Option])
					else:	
						self.Config[Section][Option] = Config_Obj[Section][Option]
				else:
					try:
						self.Config[Section][Option] = base64.b64decode(Config_Obj[Section][Option]	).decode('utf-8') 	
					except:
						self.Config[Section][Option] = Default_Value

	def Init_Config_Option_Numberic(self, Config_Obj, Section, Option, Default_Value, Encoded = False):
		# Config does not exist
		if not Section in self.Config:
			self.Config[Section] = {}
		# Config does not have that section
		if not Config_Obj.has_section(Section):
			Config_Obj.add_section(Section)
			Config_Obj.set(Section, Option, str(Default_Value))
			self.Config[Section][Option] = Default_Value
		# Config have that section
		else:
			# The section does not have that option
			if not Config_Obj.has_option(Section, Option):
				Config_Obj.set(Section, Option,str(Default_Value))
				self.Config[Section][Option] = Default_Value
			# The section have that option
			else:
				self.Config[Section][Option] = int(Config_Obj[Section][Option])
		
	def Init_Config_Option_Float(self, Config_Obj, Section, Option, Default_Value, Encoded = False):
		# Config does not exist
		if not Section in self.Config:
			self.Config[Section] = {}
		# Config does not have that section
		if not Config_Obj.has_section(Section):
			Config_Obj.add_section(Section)
			Config_Obj.set(Section, Option, str(Default_Value))
			self.Config[Section][Option] = Default_Value
		# Config have that section
		else:
			# The section does not have that option
			if not Config_Obj.has_option(Section, Option):
				Config_Obj.set(Section, Option,str(Default_Value))
				self.Config[Section][Option] = Default_Value
			# The section have that option
			else:
				self.Config[Section][Option] = float(Config_Obj[Section][Option])
				
	def Config_Save_Path(self, Config_Obj, Section, Path_Value, Default_Value):
		if not Section in self.Config:
			self.Config[Section] = {}

		if not Config_Obj.has_section(Section):
			Config_Obj.add_section(Section)

		Raw_Encoded_Path =  str(base64.b64encode(Path_Value.encode('utf-8')))
		Encoded_Path = re.findall(r'b\'(.+?)\'', Raw_Encoded_Path)[0]

		Option = 'path'
		if not Config_Obj.has_option(Section, Option):
			Config_Obj.set(Section, Option, str(Default_Value))
			self.Config[Section][Option] = Default_Value
		else:
			Config_Obj[Section][Option] = Encoded_Path
			self.Config[Section][Option] = Encoded_Path
		
	def Config_Load_Path(self, Config_Obj, Section, Default_Value = ''):
		if not Section in self.Config:
			self.Config[Section] = {}

		if not Config_Obj.has_section(Section):
			Config_Obj.add_section(Section)

		Option = 'path'
		if Config_Obj.has_section(Section):
			if Config_Obj.has_option(Section, Option):
				Raw_Path = Config_Obj[Section][Option]
				if Raw_Path != '':
					Path = base64.b64decode(Raw_Path).decode('utf-8')
					self.Config[Section][Option] = Path
				else:
					Config_Obj.set(Section, Option, str(Default_Value))
					self.Config[Section][Option] = Default_Value
			else:
				Config_Obj.set(Section, Option, str(Default_Value))
				self.Config[Section][Option] = Default_Value
		else:
			Config_Obj.set(Section, Option, str(Default_Value))
			self.Config[Section][Option] = Default_Value

	def Get_Config(self, FileName, Section, Option, Default_Value = None, Encode = False):
		
		if FileName in self:
			config_path = self.FileName
		else:
			return Default_Value

		if not os.path.isfile(config_path):
			return Default_Value

		Config_Obj = configparser.ConfigParser()
		Config_Obj.read(config_path)

		if not Config_Obj.has_section(Section):
			return Default_Value

		if not Config_Obj.has_option(Section, Option):	
			return Default_Value

		Value = Config_Obj[Section][Option]
		if Value != '':
			if Encode == True:
				return base64.b64decode(Value).decode('utf-8')
			else:
				return Value
		else:
			return Default_Value

	def Save_Config(self, Config_Path, Section, Option, Default_Value = None, Encode = False):	

		if Encode == True:
			Default_Value =  str(base64.b64encode(Default_Value.encode('utf-8')))
			Default_Value = re.findall(r'b\'(.+?)\'', Default_Value)[0]

		#print('Update value:', Default_Value)
		#print('Target file:', Config_Path)


		if not os.path.isfile(Config_Path):
			config = configparser.ConfigParser()
			with open(Config_Path, 'w') as configfile:
				config.write(configfile)

		Config_Obj = configparser.ConfigParser()
		Config_Obj.read(Config_Path)

		if not Config_Obj.has_section(Section):
			Config_Obj.add_section(Section)
			Config_Obj.set(Section, Option, str(Default_Value))

			self.Config[Section] = {}
			self.Config[Section][Option] = Default_Value
		else:
				
			if not Config_Obj.has_option(Section, Option):
				Config_Obj.set(Section, Option, str(Default_Value))
				self.Config[Section][Option] = Default_Value
			else:
				Config_Obj.set(Section, Option, str(Default_Value))

		with open(Config_Path, 'w') as configfile:
			Config_Obj.write(configfile)
		
	def Refresh_Config_Data(self):
		self.Theme_Init_Setting()
		self.Translator_Init_Setting()
		if self.Writer == True:
			
			self.Writer_Init_Setting()
			
		elif self.Document == True:
			self.Doc_Init_Setting()
		