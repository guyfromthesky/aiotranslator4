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
	def __init__(self):
		self.basePath = os.path.abspath(os.path.dirname(sys.argv[0]))
		if sys.platform.startswith('win'):
			self.appdata = os.environ['APPDATA'] + '\\AIO Translator v4'
		else:
			self.appdata = os.getcwd() + '\\AIO Translator'
	
		# Config file
		self.Doc_Config_Path = self.appdata + '\\doc.ini'
		self.Writer_Config_Path = self.appdata + '\\writer.ini'
		self.Translator_Config_Path = self.appdata + '\\translator.ini'

		# Folder
		self.TM_Backup_Folder_Path = self.appdata + '\\TM'

		self.LocalTM = self.appdata + '\\Local.pkl'

		self.Config = {}

		# Generate app folder (os.environ['APPDATA'] + '\\AIO Translator)
		self.initFolder()

		# Set default value:
		self.Writer_Init_Setting()
		self.Doc_Init_Setting()
		self.Translator_Init_Setting()
		#self.Initconfig()
		#self.Init_DB_Config()
		

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

		self.Init_Config_Option(config, Section, 'app_lang', 2)

		self.Init_Config_Option(config, Section, 'target_lang', 2)
		self.Init_Config_Option(config, Section, 'source_lang', 3)
		self.Init_Config_Option(config, Section, 'secondary_target_lang', 5)

		self.Init_Config_Option(config, Section, 'test_info_inable', 1)
		self.Init_Config_Option(config, Section, 'use_simple_template', 0)
		self.Init_Config_Option(config, Section, 'usage', 0)

		Section = 'BugDetails'
		self.Init_Config_Option(config, Section, 'TextTitle', "")
		self.Init_Config_Option(config, Section, 'TextServer', "")
		self.Init_Config_Option(config, Section, 'TextClient', "")
		self.Init_Config_Option(config, Section, 'TextReprodTime', "")
		self.Init_Config_Option(config, Section, 'TextAccount', "")
		self.Init_Config_Option(config, Section, 'TextTestReport', "")
		self.Init_Config_Option(config, Section, 'TextReproduceSteps', "")
		self.Init_Config_Option(config, Section, 'TextShouldBe', "")
		self.Init_Config_Option(config, Section, 'HeaderA', "")
		self.Init_Config_Option(config, Section, 'HeaderB', "")
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

		self.Init_Config_Option(config, Section, 'app_lang', 2)
		
		self.Init_Config_Option(config, Section, 'target_lang', 1)
		self.Init_Config_Option(config, Section, 'source_lang', 2)

		self.Init_Config_Option(config, Section, 'speed_mode', 0)
		self.Init_Config_Option(config, Section, 'value_only', 0)
		self.Init_Config_Option(config, Section, 'file_name_correct', 1)
		self.Init_Config_Option(config, Section, 'file_name_translate', 1)
		self.Init_Config_Option(config, Section, 'sheet_name_translate', 1)
		self.Init_Config_Option(config, Section, 'tm_translate', 1)
		self.Init_Config_Option(config, Section, 'tm_update', 1)
		self.Init_Config_Option(config, Section, 'remove_unselected_sheet', 0)
		self.Init_Config_Option(config, Section, 'usage', 0)
		
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
		self.Init_Config_Option(config, Section, 'db_list_uri', 'config/db_list_v4.csv')
		self.Init_Config_Option(config, Section, 'project_bucket_id', 'credible-bay-281107')
		self.Init_Config_Option(config, Section, 'license_key', '')
		self.Init_Config_Option(config, Section, 'glossary_id', '')
		self.Init_Config_Option(config, Section, 'license_file', '', True)
		self.Init_Config_Option(config, Section, 'translation_memory', '', True)
		
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
					self.Config[Section][Option] = base64.b64decode(Config_Obj[Section][Option]	).decode('utf-8') 	

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
		self.Writer_Init_Setting()
		self.Doc_Init_Setting()
		self.Translator_Init_Setting()