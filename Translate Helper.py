#System variable and io handling
import sys
import os
import re

#Regular expression handling

#Object copy, handle excel style
import copy
#Get timestamp
import datetime
from datetime import date
#import time
#function difination
# Copy to clipboard
from pyperclip import copy, paste
#from tkinter import *
#from tkinter.ttk import *
from ttkbootstrap import Entry, Label, Style
from ttkbootstrap import Checkbutton, OptionMenu, Notebook, Radiobutton, LabelFrame, Button
from ttkbootstrap import Progressbar, Style, Window

from tkinter import Tk, Frame, Toplevel, Scale

# Widget type
from tkinter import Menu, filedialog, messagebox
from tkinter import Text
# Variable type
from tkinter import IntVar, StringVar, DoubleVar
# Wrap type
from tkinter import WORD
# sticky state
from tkinter import W, E, S, N, END,X, Y, BOTH, TOP, BOTTOM
# Config state
from tkinter import DISABLED, NORMAL, HORIZONTAL
from tkhtmlview import HTMLScrolledText

#from tkinter import filedialog
#from tkinter import messagebox
#from tkinter import ttk

#import configparser
import multiprocessing
from multiprocessing import Queue, Process, Manager

import pickle
import queue 

import webbrowser
import inspect

from libs.aiotranslator import generate_translator

from libs.aioconfigmanager import ConfigLoader

from libs.cloudconfig import CloudConfigLoader

#from libs.grammarcheck import LanguageTool

from libs.version import get_version
from libs.tkinter_extension import AutocompleteCombobox, AutocompleteEntry, CustomText
from libs.tkinter_extension import Generate_BugWriter_Tab_UI, Generate_BugWriter_Menu_UI, Generate_Translate_Setting_UI
from libs.tkinter_extension import Generate_BugWriter_UI, Generate_SimpleTranslator_UI
from libs.tkinter_extension import Apply_Transparency, BugWriter_BottomPanel

from libs.general import get_version, resource_path, get_user_name
#from openpyxl import load_workbook, worksheet, Workbook

from google.cloud import logging

tool_display_name = "Translate Helper"
tool_name = 'writer'
REV = 4202
ver_num = get_version(REV) 
version = tool_display_name  + " " +  ver_num

DELAY = 20
DELAY2 = 1000

#**********************************************************************************
# UI handle ***********************************************************************
#**********************************************************************************

class MyTranslatorHelper(Frame):
	def __init__(self,
				parent = None, 
				TranslationQueue = None, 
				MyTranslator_Queue = None, 
				tm_manager = None,
				grammar_check_result = None,
				language_tool_enable = False,):

		Frame.__init__(self, parent)
		self.pack(side=TOP, expand=Y, fill=X)
		self.style =  Style()

		self.parent = parent
		self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

		self.MyTranslator_Queue = MyTranslator_Queue
		self.MyTranslator = None

		self.language_tool_enable = language_tool_enable
		self.grammar_check_result = grammar_check_result
		self.tm_manager = tm_manager
		self.return_text = TranslationQueue

		self.grammar_check_list = []
		self.grammar_corrected_list = []

		self.SOURCE_WIDTH = 80
		self.BUTTON_SIZE = 20 
		self.HALF_BUTTON_SIZE = 15
		self.ROW_SIZE = 26
		
		self.Btn_Style = "Accent.TButton"

		self.str_test_version = ""
		self.str_test_info = ""
		self.str_report = ""
		self.str_reprod_steps = ""
		self.str_should_be = ""
		self.str_title = ""
		self.str_title_source = ""
		self.header_list = ['']
		self.header_first = ""
		self.header_second = ""
		self.Separator = '====================================================='
		
		self.language_id_list = ['', 'ko', 'en', 'cn', 'jp', 'vi']
		self.language_list = ['', 'Hangul', 'English', 'Chinese', 'Japanese', 'Vietnamese']
		self.source_text = ''
		self.main_translation = ''
		self.primary_translation = ''

		# Widget list vars to change color via Translate Setting tab.

		self._after_id = None

		self.init_App_Setting()
		
		if self.AppLanguage != 'kr':
			from libs.languagepack import LanguagePackEN as LanguagePack
		else:
			from libs.languagepack import LanguagePackKR as LanguagePack

		self.report_details = None

		self.LanguagePack = LanguagePack
		

		self.init_theme()
		
		self.init_ui()
		
		self.init_UI_setting()

		if REV < int(self.latest_version):
			self.Error('Current version is lower than the minimal version allowed. Please update.')	
			webbrowser.open_new(r"https://confluence.nexon.com/display/NWMQA/AIO+Translator")
			self.quit()
			return

		if self.banning_status:
			self.Error('You\'re not allowed to use the tool. If you feel that it\'s unfair, please contact with your manager for more information.')	
			self.quit()
			return

		if self.LicensePath.get() != "":
			self.generate_translator_engine()
			self.parent.withdraw()
			self.parent.update_idletasks()
			self.LoadTempReport()
			self.parent.deiconify()
					
		else:
			closed_box = messagebox.askokcancel('Bug Writer', 'No license selected, please select the key in Translate setting.',icon = 'info')

			if closed_box == True:
				#self.Error('No license selected, please select the key in Translate setting.')
				self.TAB_CONTROL.select(self.TranslateSettingTab)
				#self.flash_btn(self.Browse_License_Btn)
		
		self.parent.minsize(self.parent.winfo_width(), self.parent.winfo_height())
		x_cordinate = int((self.parent.winfo_screenwidth() / 2) - (self.parent.winfo_width() / 2))
		y_cordinate = int((self.parent.winfo_screenheight() / 2) - (self.parent.winfo_height() / 2))
		self.parent.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

		#self.after(DELAY2, self.auto_save)
		
	def handle_wait(self,event):
        # cancel the old job
		if self._after_id is not None:
			self.after_cancel(self._after_id)
        # create a new job
		self._after_id = self.after(DELAY2, self.SaveTempReport)

    
	# Menu function
	def Error(self, ErrorText):
		messagebox.showinfo('Translate error...', ErrorText)	

	def OpenWeb(self):
		webbrowser.open_new(r"https://confluence.nexon.com/display/NWMQA/AIO+Translator")

	def About(self):
		messagebox.showinfo("About....", "Creator: Evan@nexonnetworks.com")

	def on_closing(self):
		if messagebox.askokcancel(tool_display_name, "Do you want to quit?"):
			self.parent.destroy()
			self.TranslatorProcess.terminate()

	def rebuild_UI(self):
		if messagebox.askokcancel("Quit", "Do you want to restart?"):
			self.parent.destroy()
			main()
		else:
			messagebox.showinfo('Language update','The application\'s language will be changed in next session.')	

	def init_ui(self):
		self.parent.resizable(False, False)
		self.parent.title(version)

		Generate_BugWriter_Menu_UI(self)
		Generate_BugWriter_Tab_UI(self)

		try:
			Generate_BugWriter_UI(self, self.BugWriterTab)
			Generate_SimpleTranslator_UI(self, self.SimpleTranslatorTab)
			Generate_Translate_Setting_UI(self, self.TranslateSettingTab)

			self.bottom_panel = BugWriter_BottomPanel(self)
	
		except Exception as e:
			print(f'An error occurs while initializing UI: {e}')



		#self.Generate_Search_UI(self.Searcher)

		#self.Init_Translator_Config

		
	
		
	# Init functions
	# Some option is saved for the next time use
	def init_App_Setting(self):
		print('init_App_Setting')
		self.SkipTestInfo = IntVar()
		self.UseSimpleTemplate = IntVar()

		self.LicensePath = StringVar()
		self.Transparent = DoubleVar()

		#self.DictionaryPath = StringVar()
		self.TMPath = StringVar()

		self.CurrentDataSource = StringVar()
		self.Notice = StringVar()
		self.DictionaryStatus = StringVar()
		
		#self.TMStatus  = StringVar()
		self.HeaderStatus = StringVar()
		self.VersionStatus  = StringVar()
		self._update_day = StringVar()

		self.AppConfig = ConfigLoader(Writer = True)

		self.Configuration = self.AppConfig.Config
		#print('self.Configuration', self.Configuration)

		self.AppLanguage  = self.Configuration['Bug_Writer']['app_lang']
		license_file_path = self.Configuration['Translator']['license_file']
		self.LicensePath.set(license_file_path)


		Transparent = self.Configuration['Bug_Writer']['Transparent']
		self.Transparent.set(Transparent)

		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = license_file_path
		self.TMPath.set(self.Configuration['Translator']['translation_memory'])
		# Address of the bucket
		self.bucket_id = self.Configuration['Translator']['bucket_id']
		# Address of the project config file
		self.db_list_uri = self.Configuration['Translator']['db_list_uri']
		# Address of the project config file
		self.project_bucket_id = self.Configuration['Translator']['project_bucket_id']

		self.glossary_id = self.Configuration['Translator']['glossary_id']
		
		self.used_theme = self.Configuration['Bug_Writer']['theme_name']
	
		try:
			cloud_config = CloudConfigLoader()
			cloud_configuration = cloud_config.Config
			self.banning_status = cloud_configuration['banned']
			self.latest_version = cloud_configuration['latest_version']
		except Exception as e:
			print("Error while loading cloud configuration:", e)
			self.banning_status = False
			self.latest_version = 1000
			
		
		self.source_language = StringVar()	
		self.target_language = StringVar()
		self.secondary_target_language = StringVar()

		self.simple_source_language = StringVar()
		self.simple_target_language = StringVar()
		self.simple_secondary_target_language = StringVar()

		self.strvar_theme_name = StringVar()
		#self.Config['bucket_db_list']


		#self.Config['glossary_data_list']
		

	def init_UI_setting(self):
		
		self.source_language.set(self.language_list[self.Configuration['Bug_Writer']['source_lang']])
		self.target_language.set(self.language_list[self.Configuration['Bug_Writer']['target_lang']])
		secondary_language = self.Configuration['Bug_Writer']['secondary_target_lang']
		if secondary_language == 6:
			self.secondary_target_language.set('')
		else:
			self.secondary_target_language.set(self.language_list[secondary_language])
		
		self.SkipTestInfo.set(self.Configuration['Bug_Writer']['test_info_inable'])
		self.UseSimpleTemplate.set(self.Configuration['Bug_Writer']['use_simple_template'])


		self.simple_source_language.set(self.language_list[self.Configuration['Simple_Translator']['source_lang']])
		self.simple_target_language.set(self.language_list[self.Configuration['Simple_Translator']['target_lang']])
		simple_secondary_language = self.Configuration['Simple_Translator']['secondary_target_lang']
		
		if simple_secondary_language == 6:
			self.simple_secondary_target_language.set('')
		else:
			self.simple_secondary_target_language.set(self.language_list[simple_secondary_language])

	def init_theme(self):
		"""Applied the theme name saved in the settings on init."""
		try:
			all_themes = self.style.theme_names()
			personalize_themes = ['wynnmeister', 'erza\'s', 'tien\'s', 'dao\'s', 'blackpink']
			self.theme_names = []
			for theme in all_themes:
				
				if theme in personalize_themes:
					print('Personalize theme:', theme)
					user = get_user_name()
					if theme == 'dao\'s' and user == 'jennie':
						self.theme_names.append(theme)
					elif theme == 'wynnmeister' and user == 'wynn.saltywaffle':
						self.theme_names.append(theme)	
					elif theme == 'erza\'s' and user == 'erzaerza':
						self.theme_names.append(theme)	
					elif theme == 'tien\'s' and user == 'hann':
						self.theme_names.append(theme)	
					elif theme == 'blackpink' and user == 'ruko':
						self.theme_names.append(theme)
					elif user == 'evan':
						self.theme_names.append(theme)
				else:	
					self.theme_names.append(theme)
	
			if self.used_theme not in self.theme_names:
				raise Exception('Cannot use the theme saved in the config'
					' because it is not supported or required files have'
					' been removed.')

			self.style.theme_use(self.used_theme)

		except Exception as err:
			print('Error while initializing theme:\n'
				f'- {err}\n'
				'The system default theme will be used instead.')
		transparency  = self.Configuration['Bug_Writer']['Transparent']
		Apply_Transparency(transparency, self)


	def select_theme_name(self):
		"""Save the theme name value to Configuration and change
		the theme based on the selection in the UI.
		
		Args:
			config_theme_name -- str
				Theme name retrieved from config. (Default: '')
		"""

		try:
			theme_name = self.strvar_theme_name.get()
			print('Select theme:', theme_name)
			self.style.theme_use(theme_name)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Bug_Writer',
				'theme_name',
				theme_name, True)

		except Exception as err:
			messagebox.showerror(
				title='Error',
				message=f'Error occurs when selecting theme: {err}')

	
	def remove_theme(self):
		print('remove_theme')
		"""Remove the theme saved in config then restart the app."""
		self.AppConfig.Save_Config(
			self.AppConfig.Writer_Config_Path,
			'Bug_Writer',
			'theme_name',
			'')
		
		messagebox.showinfo(
			title='Info',
			message='App will restart to apply the change.')
		self.parent.destroy()
		main()

#######################################################################
# Menu function
#######################################################################

	def SetLanguageKorean(self):
		self.AppLanguage = 'kr'
		self.SaveAppLanguage(self.AppLanguage)
		self.rebuild_UI()
		#self.initUI()
	
	def SetLanguageEnglish(self):
		self.AppLanguage = 'en'
		self.SaveAppLanguage(self.AppLanguage)
		self.rebuild_UI()
		#self.initUI()

	def SaveAppLanguage(self, language):

		self.Notice.set(self.LanguagePack.ToolTips['AppLanuageUpdate'] + " "+ language) 
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'app_lang', language)

	def SelectDictionary(self):
		filename = filedialog.askopenfilename(title = "Select Database file",filetypes = (("Dictionary files","*.xlsx *.xlsm"), ), )	
		if filename != "":
			NewDictionary = self.CorrectPath(filename)	
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'database', 'path', NewDictionary, True)
			self.Notice.set(self.LanguagePack.ToolTips['DocumentLoaded'])
		else:
			self.Notice.set(self.LanguagePack.ToolTips['SourceDocumentEmpty'])
	
	def SelectDataTableSource(self):
		filename = filedialog.askopenfilename(title =  self.LanguagePack.ToolTips['SelectDB'],filetypes = (("Dictionary files","*.xlsx *.xlsm" ), ), multiple=True)	
		if filename != "":
			self.DataTablePathList = list(filename)
			for path in self.DataTablePathList:
				path = self.CorrectPath(path)

			self.CurrentDataSource.set(str(self.DataTablePathList[0]))
			#self.Notice.set(self.LanguagePack.ToolTips['SourceSelected'])
			self.Notice.set(self.LanguagePack.ToolTips['DBUpdated'])
		else:
			#self.Notice.set(self.LanguagePack.ToolTips['SourceDocumentEmpty'])
			self.Notice.set(self.LanguagePack.ToolTips['NoDictUse'])
		return

	def SelectTM(self):
		filename = filedialog.askopenfilename(title = "Select Translation Memory file", filetypes = (("TM files","*.pkl"), ),)
		if filename != "":
			NewTM = self.CorrectPath(filename)
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'translation_memory', 'path', NewTM, True)
			self.Notice.set(self.LanguagePack.ToolTips['TMUpdated'])
		else:
			self.Notice.set(self.LanguagePack.ToolTips['SourceDocumentEmpty'])

	def SaveNewTM(self):

		filename = filedialog.asksaveasfilename(title = "Select file", filetypes = (("Translation Memory", "*.pkl"),),)
		filename = self.CorrectExt(filename, "pkl")
		if filename == "":
			return
		else:
			NewTM = self.CorrectPath(filename)
			#print(NewTM)


			with open(NewTM, 'wb') as pickle_file:
				pickle.dump([], pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
				
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'translation_memory', 'path', NewTM, True)

	def CorrectPath(self, path):
		if sys.platform.startswith('win'):
			return str(path).replace('/', '\\')
		else:
			return str(path).replace('\\', '//')
	
	def CorrectExt(self, path, ext):
		if path != None and ext != None:
			Outputdir = os.path.dirname(path)
			baseName = os.path.basename(path)
			sourcename = os.path.splitext(baseName)[0]
			newPath = self.CorrectPath(Outputdir + '/'+ sourcename + '.' + ext)
			return newPath

	def _create_grammar_confirmation_window(self, dif_dict, _class):
		self.new = Toplevel(self.master)

		_class(self.new, dif_dict)
	
	#I dont know why I put it here
	def UpdateSize(self,event):
		
		self.parent.update()
		#print(self.parent.winfo_width(), 'x', self.parent.winfo_height())
		#print(self.SourceText.winfo_width(), 'x', self.SourceText.winfo_height())
		iWidth = int(int(self.parent.winfo_width()*0.5 - 22)/8)
		iHeight = int(int(self.parent.winfo_height() - 154)/16)
		#print(iWidth, 'x', iHeight)
		self.SourceText.configure(width = iWidth, height = iHeight)
		self.TargetText.configure(width = iWidth, height = iHeight)

	def set_writer_language(self, event):
		
		target_language_index = self.language_list.index(self.target_language.get())
		target_language = self.language_id_list[target_language_index]
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'target_lang', target_language_index)

		source_language_index = self.language_list.index(self.source_language.get())
		source_language = self.language_id_list[source_language_index]
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'source_lang', source_language_index)

		secondary_target_language_index = self.language_list.index(self.secondary_target_language.get())
		#secondary_target_language = self.language_id_list[self.language_list.index(secondary_target_language_index)]
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'secondary_target_lang', secondary_target_language_index)

		self.MyTranslator.set_language_pair(source_language = source_language, target_language = target_language)
		self.DictionaryStatus.set(str(self.MyTranslator.glossary_size))
		self.UpdateHeaderList()


	def set_simple_language(self, event):
		print(event)
		simple_target_language_index = self.language_list.index(self.simple_target_language.get())
		simple_target_language = self.language_id_list[simple_target_language_index]
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Simple_Translator', 'target_lang', simple_target_language_index)

		simple_source_language_index = self.language_list.index(self.simple_source_language.get())
		simple_source_language = self.language_id_list[simple_source_language_index]
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Simple_Translator', 'source_lang', simple_source_language_index)
		
		simple_secondary_target_language_index = self.language_list.index(self.simple_secondary_target_language.get())
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Simple_Translator', 'secondary_target_lang', simple_secondary_target_language_index)

		self.MyTranslator.set_language_pair(source_language = simple_source_language, target_language = simple_target_language)

	def generate_translator_engine(self):
		self.Notice.set(self.LanguagePack.ToolTips['AppInit'])
	
		target_language = self.language_id_list[self.language_list.index(self.target_language.get())]
		source_language = self.language_id_list[self.language_list.index(self.source_language.get())]

		#self.glossary_id = self.bottom_panel.project_id_select.get()
		#self.glossary_id = self.glossary_id.replace('\n', '')
		print('Start new process: Generate Translator')
		self.TranslatorProcess = Process(	target = generate_translator,
											kwargs= {	'my_translator_queue' : self.MyTranslator_Queue, 
														'temporary_tm' : self.tm_manager, 
														'from_language' : source_language, 
														'to_language' : target_language, 
														'glossary_id' : self.glossary_id, 
														'used_tool' : tool_name,
														'tm_path' : None,
														'bucket_id' : self.bucket_id, 
														'db_list_uri' : self.db_list_uri, 
														'project_bucket_id' : self.project_bucket_id,
													},
										)
		self.TranslatorProcess.start()										
		self.after(DELAY, self.GetMyTranslator)
		return	

	def GetMyTranslator(self):
		try:
			self.MyTranslator = self.MyTranslator_Queue.get_nowait()
		except queue.Empty:
			self.after(DELAY, self.GetMyTranslator)

		if self.MyTranslator != None:
			self.Notice.set(self.LanguagePack.ToolTips['AppInitDone'])

			#self.MyTranslator.Convert_Translation_Memory()

			self.enable_btn()
			
			self.UpdateHeaderList()
			self.UpdatePredictionList()

			try:
				db_count = str(self.MyTranslator.glossary_size)
			except:
				db_count = 0
			
			self.DictionaryStatus.set(db_count)

			#_glossary_list = [""] + self.MyTranslator.glossary_list
			#glossary_list = []
			#for project in _glossary_list:
			#	if project in self.MyTranslator.bucket_db_list:
			#		glossary_list.append(project)
			glossary_list = [""] + self.MyTranslator.glossary_list
			

			self.project_id_select.set_completion_list(glossary_list)
			#print('saved gloss:', self.glossary_id)
			#print('list gloss', self.MyTranslator.glossary_list)
			if self.glossary_id in self.MyTranslator.glossary_list:
				self.project_id_select.set(self.glossary_id)
			else:
				self.project_id_select.set("")

			if isinstance(self.MyTranslator.version, str):
				version = self.MyTranslator.version[0:10]
			else:
				version = '-'

			if isinstance(self.MyTranslator.update_day, str):
				Date = self.MyTranslator.update_day[0:10]
			else:
				Date = '-'

			self.VersionStatus.set(version)
			self._update_day.set(Date)

			#self.Error('No Valid Project selected, please update the project ID in Translate Setting tab')	
			#DBLength = self.MyTranslator.get_glossary_length()
			#self.DictionaryStatus.set(str(DBLength))

			self.TranslatorProcess.join()
		else:
			self.Notice.set(self.LanguagePack.ToolTips['AppInit'])

	def get_source_text(self):
		self.source_text = self.SourceText.get("1.0", END)
		if self.source_text.endswith('\n'):
			self.source_text = self.source_text[:-1]

	#Execute function
	def single_translate(self):
		if self.LicensePath.get() == "":
			self.Error('Please select License file and relaunch the app!')
			return
			
		self.Notice.set(self.LanguagePack.ToolTips['Translating'])

		target_language = self.language_id_list[self.language_list.index(self.simple_target_language.get())]
		source_language = self.language_id_list[self.language_list.index(self.simple_source_language.get())]

		if target_language == source_language:
			messagebox.showinfo('Error', 'Source and Primary Target language is the same.')	
			return
		if target_language != self.MyTranslator.to_language or source_language != self.MyTranslator.from_language:
			self.MyTranslator.set_language_pair(source_language = source_language, target_language = target_language)
			print('Update language pair from: ', source_language, ' to ',  target_language)		

		self.get_source_text()
		#print('Source:', self.source_text)
		try:
			_temp_source = 	self.source_text.split('\n')
		except:
			pass
		source_text = []
		try:
			for text in _temp_source:
				if text != "":
					source_text.append(text)
		except:
			pass
		
		self.p3 = Process(target=SimpleTranslate, args=(self.return_text, self.MyTranslator, source_text,))
		self.p3.start()
		self.after(DELAY, self.GetSimpleTranslateStatus)

	def GetSimpleTranslateStatus(self):
		if (self.p3.is_alive()):
			self.after(DELAY, self.GetSimpleTranslateStatus)
		else:
			try:
				Translated = self.return_text.get()
				self.TargetText.delete("1.0", END)
				if Translated[0] != False:
					_index = 0
					_translation = []
					try:
						_temp_source = 	self.source_text.split('\n')
					except:
						pass
	
					try:
						for text in _temp_source:
							if text != "":
								_translation.append(Translated[_index])
								_index += 1
							else:
								_translation.append(text)	
					except:
						pass	
					self.main_translation = "\n".join(_translation)
					self.main_translation = self.main_translation.replace('\r\n', '\n')
					self.TargetText.insert("end", self.main_translation)
					
					
					
					#for pair in self.MyTranslator.Dictionary:
					#	EN = pair[1]
					'''
					for pattern in self.MyTranslator.EN:
						#print('pattern', pattern)
						pattern = " " + pattern.strip() + " "
						self.SourceText.highlight_pattern(pattern, 'blue')
					'''
					self.Notice.set(self.LanguagePack.ToolTips['Translated'])
					
				else:
					#Show = "\n".join(Translated)
					#self.TargetText.insert("end", 'Fail to translate')
					self.Notice.set(self.LanguagePack.ToolTips['TranslateFail'])	
				self.p3.join()
			except queue.Empty:
				pass

	def dual_translate(self):
		if self.LicensePath.get() == "":
			self.Error('Please select License file and relaunch the app!')
			return
			
		self.Notice.set(self.LanguagePack.ToolTips['Translating'])
		
		self.primary_translation = ''
		self.main_translation = ''
		#self.source_language
	
		primary_target_language = self.language_id_list[self.language_list.index(self.simple_secondary_target_language.get())]
		if primary_target_language == "":
			messagebox.showinfo('Warning', 'Secondary target language is EMPTY.\nIf you don\'t need to use the secondary target language,\nplease use Translate button to save the API usage.')	
			self.single_translate()
			return
		
		target_language = self.language_id_list[self.language_list.index(self.simple_target_language.get())]
		source_language = self.language_id_list[self.language_list.index(self.simple_source_language.get())]

		if source_language == target_language:
			messagebox.showinfo('Error', 'Source and Primary Target language is the same.')	
			return
		if source_language == primary_target_language:
			messagebox.showinfo('Error', 'Source and Secondary Target language is the same.')	
			return
		if target_language == primary_target_language:
			messagebox.showinfo('Error', 'Primary and Secondary Target language is the same.')	
			return
		
		if target_language != self.MyTranslator.to_language or source_language != self.MyTranslator.from_language:
			self.MyTranslator.set_language_pair(source_language = source_language, target_language = target_language)
			print('Update language pair from: ', source_language, ' to ',  target_language)


		self.source_text = self.SourceText.get("1.0", END)
		if self.source_text.endswith('\n'):
			self.source_text = self.source_text[:-1]
		#print('Source:', self.source_text)	
		try:
			_temp_source = 	self.source_text.split('\n')
		except:
			pass
		source_text = []
		try:
			for text in _temp_source:
				if text != "":
					source_text.append(text)
		except:
			pass
		
		self.dual_translate_process = Process(target=dual_translate, args=(self.return_text, self.MyTranslator, primary_target_language, source_text,))
		self.dual_translate_process.start()
		self.after(DELAY, self.get_dual_translate_result)

	def get_dual_translate_result(self):
		"""
		[Dual Translate] button in Simple Translator
		Generate the translated text in Target Text textbox.
		"""
		if (self.dual_translate_process.is_alive()):
			self.after(DELAY, self.get_dual_translate_result)
		else:
			try:
				Translated = self.return_text.get()
				self.TargetText.delete("1.0", END)
				if isinstance(Translated, dict):
					main_translation = Translated['main']
					secondary_translation = Translated['primary']


					_index = 0
					_main_translation = []
					_secondary_translation = []
					try:
						_temp_source = 	self.source_text.split('\n')
					except:
						pass
	
					try:
						for text in _temp_source:
							if text != "":
								_main_translation.append(main_translation[_index])
								_secondary_translation.append(secondary_translation[_index])
								_index += 1
							else:
								_main_translation.append(text)
								_secondary_translation.append(text)
					except:
						pass	

					self.main_translation = "\n".join(_main_translation)
					self.main_translation = self.main_translation.replace('\r\n', '\n')
					self.TargetText.insert("end", "[" + self.simple_target_language.get() + "]\n")
					self.TargetText.insert("end", self.main_translation)
					self.TargetText.insert("end", "\n" + self.Separator + "\n")
					
					
					self.primary_translation = "\n".join(_secondary_translation)
					self.primary_translation = self.primary_translation.replace('\r\n', '\n')

					self.TargetText.insert("end", "[" + self.simple_secondary_target_language.get() + "]\n")
					self.TargetText.insert("end", self.primary_translation)

					#for pair in self.MyTranslator.Dictionary:
					#	EN = pair[1]
					'''
					for pattern in self.MyTranslator.EN:
						#print('pattern', pattern)
						pattern = " " + pattern.strip() + " "
						self.SourceText.highlight_pattern(pattern, 'blue')
					'''
					self.Notice.set(self.LanguagePack.ToolTips['Translated'])
					
				else:
					#Show = "\n".join(Translated)
					#self.TargetText.insert("end", 'Fail to translate')
					self.Notice.set(self.LanguagePack.ToolTips['TranslateFail'])	
				self.dual_translate_process.join()
			except queue.Empty:
				pass			

	#Execute function
	def BtnCopy(self):
		self.get_source_text()
		#Translated = self.TargetText.get("1.0", END)
		#Translated = Translated.replace('\r', '')
		copy(self.main_translation)
		self.Notice.set(self.LanguagePack.ToolTips['Copied'])

	def btn_bilingual_copy(self):
		"""
		[Bilingual] button in Simple Translator.
		Copy the text in Source Text and Target Text to the clipboard when clicked.
		"""

		self.get_source_text()

		# Copy all text in the Source Text and Target Text textbox
		bilingual = self.TargetText.get("1.0", END) + "\n"
		bilingual += self.Separator + "\n"
		bilingual += self.SourceText.get("1.0", END)
		
		copy(bilingual)
		self.Notice.set(self.LanguagePack.ToolTips['Copied'])

	def btn_trilingual(self):
		
		primary_target_language = self.language_id_list[self.language_list.index(self.simple_secondary_target_language.get())]
		if primary_target_language == "":
			messagebox.showinfo('Warning', 'Secondary target language is EMPTY.\nPlease select the secondary target language or use Bilingual Copy instead.')	
			self.btn_bilingual_copy()
			return
		self.get_source_text()

		trilingual = self.main_translation + "\n"	
		trilingual += self.Separator + "\n"
		trilingual += self.source_text + "\n"
		trilingual += self.Separator + "\n"
		trilingual += self.primary_translation
	
		copy(trilingual)

		self.Notice.set(self.LanguagePack.ToolTips['Copied'])


	def BtnTranslateAndBilingual(self):
		copy("")
		try:
			if (self.SimpleTranslator.is_alive()):
				self.SimpleTranslator.terminate()
		except:
			pass
		self.Notice.set(self.LanguagePack.ToolTips['Translating'])
		self.TargetText.delete("1.0", END)

		SourceText = self.SourceText.get("1.0", END)
		try:
			SourceText = SourceText.split('\n')
		except:
			pass
		self.SimpleTranslator = Process(target=SimpleTranslate, args=(self.return_text, self.MyTranslator, SourceText,))
		self.SimpleTranslator.start()
		self.after(DELAY, self.Generate_Bilingual_Text)
		return
		
	def Generate_Bilingual_Text(self):
		if (self.SimpleTranslator.is_alive()):
			self.after(DELAY, self.Generate_Bilingual_Text)
			return
		else:
			try:
				Translated = self.return_text.get()
				#Translated = Translated.replace('\r\n', '\n')
				if Translated[0] != False:
					Show = "\n".join(Translated)
					Show = Show.replace('\r\n', '\n')
					self.TargetText.insert("end", Show)
					self.Notice.set(self.LanguagePack.ToolTips['Translated'])
				
				SourceText = self.SourceText.get("1.0", END)
				SourceText = SourceText.replace('\r\n', '\n')
				
				Bilingual = Show + "\r\n" + self.Separator + "\r\n" + SourceText
				copy(Bilingual)
				self.Notice.set(self.LanguagePack.ToolTips['Copied'])
				self.SimpleTranslator.join()
			except queue.Empty:
				self.Notice.set(self.LanguagePack.ToolTips['TranslateFail'])
		return
	

	def BindSwap(self, event):
		self.Swap()
		return "break"

	def _get_language(self):
		target_language_index = self.language_list.index(self.simple_target_language.get())
		source_language_index = self.language_list.index(self.simple_source_language.get())

		target_language = self.language_id_list[target_language_index]
		source_language = self.language_id_list[source_language_index]

	def Swap(self):
		
		SourceText = self.SourceText.get("1.0", END)
		Translated = self.TargetText.get("1.0", END)

		self.SourceText.delete("1.0", END)
		self.TargetText.delete("1.0", END)

		self.TargetText.insert("end", SourceText)
		self.SourceText.insert("end", Translated)
		
		target_language_index = self.language_list.index(self.simple_target_language.get())
		source_language_index = self.language_list.index(self.simple_source_language.get())

		target_language = self.language_id_list[target_language_index]
		source_language = self.language_id_list[source_language_index]
		
		self.simple_target_language.set(self.language_list[source_language_index])
		self.simple_source_language.set(self.language_list[target_language_index])
		
		self.MyTranslator.set_language_pair(target_language = source_language, source_language = target_language)

		return

	def bind_translate(self,event):
		self.single_translate()
		return "break"

	def disable_btn(self):
		self.GetTitleBtn.configure(state=DISABLED)
		self.GetReportBtn.configure(state=DISABLED)
		#self.CorrectGrammarBtn.configure(state=DISABLED)
		self.TranslateBtn.configure(state=DISABLED)
		self.dual_translate_btn.configure(state=DISABLED)
		#self.RenewTranslator.configure(state=DISABLED)
		#self.RenewTranslatorMain.configure(state=DISABLED)
		self.RenewTranslatorMain.configure(state=DISABLED)
		
		self.secondary_target_language_select.configure(state=DISABLED)
		self.target_language_select.configure(state=DISABLED)
		self.source_language_select.configure(state=DISABLED)

		self.simple_secondary_target_language_select.configure(state=DISABLED)
		self.simple_target_language_select.configure(state=DISABLED)
		self.simple_source_language_select.configure(state=DISABLED)
		
		self.project_id_select.configure(state=DISABLED)

		#self.Translate_bilingual_Btn.configure(state=DISABLED)
		self.TranslateBtn.configure(state=DISABLED)

		self.ReviewReportBtn.configure(state=DISABLED)

		#self.db_correction.configure(state=DISABLED)

	def enable_btn(self):
		self.GetTitleBtn.configure(state=NORMAL)
		self.GetReportBtn.configure(state=NORMAL)
		#self.CorrectGrammarBtn.configure(state=NORMAL)
		self.TranslateBtn.configure(state=NORMAL)
		self.dual_translate_btn.configure(state=NORMAL)
		#self.RenewTranslator.configure(state=NORMAL)
		#self.RenewTranslatorMain.configure(state=NORMAL)
		self.RenewTranslatorMain.configure(state=NORMAL)

		self.secondary_target_language_select.configure(state=NORMAL)
		self.target_language_select.configure(state=NORMAL)
		self.source_language_select.configure(state=NORMAL)

		self.simple_secondary_target_language_select.configure(state=NORMAL)
		self.simple_target_language_select.configure(state=NORMAL)
		self.simple_source_language_select.configure(state=NORMAL)

		self.project_id_select.configure(state=NORMAL)

		#self.Translate_bilingual_Btn.configure(state=NORMAL)
		self.TranslateBtn.configure(state=NORMAL)

		#self.db_correction.configure(state=NORMAL)

	def RenewMyTranslator(self):
		
		self.disable_btn()

		del self.MyTranslator
		self.MyTranslator = None

		self.HeaderOptionA.set_completion_list([])
		self.HeaderOptionB.set_completion_list([])
		
		self.search_entry.set_completion_list([])
		self.HeaderStatus.set('0')

		self.generate_translator_engine()

	#Option functions

	def UpdatePredictionList(self):
		#print('self.header_list', self.header_list)
		Autolist = self.MyTranslator.dictionary
		
	
		'''
		for item in self.MyTranslator.NameList:
			Autolist.append("\"" + item[0] + "\"")
			Autolist.append("\"" + item[1] + "\"")
		'''
		#print('Autolist', Autolist)
		#set_completion_list
		
		self.search_entry.set_completion_list(Autolist)

	def UpdateHeaderList(self):
		try:
			header_count = str(len(self.MyTranslator.header))
		except:
			header_count = 0
		self.HeaderStatus.set(header_count)
		self.header_listFull = self.MyTranslator.header	
		self.header_list = [""]

		for Header in self.header_listFull:
			self.header_list.append(Header[0])
		self.HeaderOptionA.set_completion_list(self.header_list)
		self.HeaderOptionB.set_completion_list(self.header_list)



	def ResetReport(self,event=None):
		self.ResetTestReport()

	def analyze_terminology(self):
		for term in self.MyTranslator.dictionary:
			if term not in [' ']:
				self.TextTestReport.highlight_fault_pattern(term, 'blue')
				self.TextTitle.highlight_fault_pattern(term, 'blue')
				self.TextReproduceSteps.highlight_fault_pattern(term, 'blue')
				self.TextShouldBe.highlight_fault_pattern(term, 'blue')

	def tag_selected(self, event):
		self.TextTestReport.tag_selected()
		self.TextTitle.tag_selected()
		self.TextReproduceSteps.tag_selected()
		self.TextShouldBe.tag_selected()
		self.SourceText.tag_selected()

	def review_report(self):

		child_windows = Toplevel(self.parent)
		#child_windows.geometry("200x200")  # Size of the window 
		child_windows.resizable(False, False)
		child_windows.title("Report reviewer")
		self.report_review = HTMLScrolledText(child_windows)
		self.report_review.set_html(self.html_content)
		self.report_review.pack(pady=5, padx=5, fill=BOTH)
	
	def analyze_fault_terminology(self):
		for term in self.MyTranslator.dictionary:
			if term not in [' ']:
				self.TextTestReport.highlight_fault_pattern(term, 'red')
				self.TextTitle.highlight_fault_pattern(term, 'red')
				self.TextReproduceSteps.highlight_fault_pattern(term, 'red')
				self.TextShouldBe.highlight_fault_pattern(term, 'red')
				

	def analyze_grammar(self):
		self.confirm_report_grammar()
		

	def GetTitle(self, event=None):
		self.disable_btn()
		copy("")
		target_language = self.language_id_list[self.language_list.index(self.target_language.get())]
		source_language = self.language_id_list[self.language_list.index(self.source_language.get())]
		if target_language != self.MyTranslator.to_language or source_language != self.MyTranslator.from_language:
			self.MyTranslator.set_language_pair(source_language = source_language, target_language = target_language)
			print('Update language pair from: ', source_language, ' to ',  target_language)
		self.Notice.set(self.LanguagePack.ToolTips['GenerateBugTitle'])
		#self.strSourceTitle = self.TextTitle.get("1.0", END).replace('\n', '')
		self.strSourceTitle = self.TextTitle.get("1.0", END).rstrip()
		self.Title_Translate = Process(target=SimpleTranslate, args=(self.return_text, self.MyTranslator, self.strSourceTitle,))
		self.Title_Translate.start()
		self.after(DELAY, self.TextTitleGet)
		return

	def TextTitleGet(self):
		if (self.Title_Translate.is_alive()):
			self.after(DELAY, self.TextTitleGet)
			return
		else:
			try:
				TempTitle  = self.return_text.get(0)
				if isinstance(TempTitle, list):
					self.TargetTitle = "\n".join(TempTitle)
				elif isinstance(TempTitle, str):
					self.TargetTitle = TempTitle
				else:
					self.TargetTitle = ""
				
				HeaderA = ""
				HeaderB = ""
				
				HeaderA = self.HeaderOptionA.get()
				if HeaderA != "":
					HeaderA_Translated = self.MyTranslator.translate_header(HeaderA)
				else:
					HeaderA_Translated = False
					
				HeaderB = self.HeaderOptionB.get()
				if HeaderB != "":
					HeaderB_Translated = self.MyTranslator.translate_header(HeaderB)
				else:
					HeaderB_Translated = False
				SourceHeader = ""
				TargetHeader = ""

				if HeaderA != "" and HeaderA_Translated != False:
					SourceHeader += "[" + HeaderA + "]"
					TargetHeader += "[" + HeaderA_Translated + "]"
				if HeaderB != False and HeaderB_Translated != False:
					SourceHeader += "[" + HeaderB + "]"
					TargetHeader += "[" + HeaderB_Translated + "]"	

				Title = TargetHeader + " "  +  self.TargetTitle + " | " + SourceHeader  + " " +  self.strSourceTitle
				
				copy(str(Title))
				self.Notice.set(self.LanguagePack.ToolTips['GeneratedBugTitle'])
				self.Title_Translate.join()
			except queue.Empty:
				self.Notice.set(self.LanguagePack.ToolTips['GenerateBugTitleFail'])

			self.enable_btn()	
		return

	#Reset buttons
	def ResetTestVersion(self):	
		self.TextServer.delete("1.0", END)
		self.TextClient.delete("1.0", END)
		self.TextClient.insert("end", "ver.")
		return

	def ResetTestInfo(self):
		self.TextReprodTime.delete("1.0", END)
		self.TextAccount.delete("1.0", END)
		return

	def ResetTestReport(self):
		self.TextTitle.delete("1.0", END)
		self.TextTestReport.delete("1.0", END)
		self.TextReproduceSteps.delete("1.0", END)
		self.TextShouldBe.delete("1.0", END)		
		return
	#END

	#GUI function
	def collect_report_elements(self):
		TextTestServer = self.TextServer.get("1.0", END).replace('\n', '')
		#print('TextTestServer', TextTestServer)
		TextTestClient = self.TextClient.get("1.0", END).replace('\n', '')
		#print('TextTestClient', TextTestClient)
		To_Translate = {}
		To_Translate['TextTestVersion'] = [TextTestServer, TextTestClient]
	
		if self.SkipTestInfo.get() == 1:
			TextReproduceTime = self.TextReprodTime.get("1.0", END).replace('\n', '')
			TextTestAccount = self.TextAccount.get("1.0", END).replace('\n', '')
			To_Translate['TextTestInfo'] = [TextReproduceTime, TextTestAccount]
		else:
			print('Test info exclude')
			To_Translate['TextTestInfo'] = None
		
		To_Translate['TextShouldBe'] = self.TextShouldBe.get("1.0", END)
		To_Translate['TextReproduceSteps'] = self.TextReproduceSteps.get("1.0", END)

		

		To_Translate['TextTestReport'] = self.TextTestReport.get("1.0", END)
		To_Translate['TextShouldBe'] = self.TextShouldBe.get("1.0", END)
		To_Translate['TextReproduceSteps'] = self.TextReproduceSteps.get("1.0", END)
		self.report_details = To_Translate

			

	def add_no_translate_tag(self, text):
		for index in range(len(text)):
			string_to_translate = text[index]
			special_texts = re.findall("\<([^\>]*)\>", string_to_translate)
			#print('special_texts list', special_texts)
			for special_text in special_texts:
				text[index]  = string_to_translate.replace("<" + special_text + ">", ("<span class=\"notranslate\">" + special_text + "</span>"))
		#print('New source', source_text)
		return text

	def prepare_translator_language(self):
		return

	def GenerateReportCSS(self):
		self.Notice.set(self.LanguagePack.ToolTips['GenerateBugReport'])

		copy("")
		target_language = self.language_id_list[self.language_list.index(self.target_language.get())]
		source_language = self.language_id_list[self.language_list.index(self.source_language.get())]
		secondary_target_language = self.language_id_list[self.language_list.index(self.secondary_target_language.get())]
		#self.MyTranslator.set_language_pair(target_language = target_language, source_language = source_language)
		if secondary_target_language == "":
			secondary_target_language = None
		if target_language != self.MyTranslator.to_language or source_language != self.MyTranslator.from_language:
			self.MyTranslator.set_language_pair(source_language = source_language, target_language = target_language)
			print('Update language pair from: ', source_language, ' to ',  target_language)

		Simple_Template = self.UseSimpleTemplate.get()

		self.BugWriter = Process(target=Translate_Simple, args=(self.report_details, Simple_Template, self.MyTranslator, secondary_target_language))
		self.BugWriter.start()

		self.after(DELAY, self.GetBugDetails)

	def GetBugDetails(self):
		self.disable_btn()
		self.Notice.set(self.LanguagePack.ToolTips['ClipboardRemoved'])

		if (self.BugWriter.is_alive()):
			self.after(DELAY, self.GetBugDetails)
		else:
			self.Notice.set(self.LanguagePack.ToolTips['GeneratedBugReport'])
			self.BugWriter.join()
			self.html_content = paste()
			#self.html_content = '#my{zoom: 75%;}\n' + self.html_content
			self.enable_btn()
			self.ReviewReportBtn.configure(state=NORMAL)

	def generate_report(self,event=None):
		self.collect_report_elements()
		self.GenerateReportCSS()


	def confirm_report_grammar(self):
		self.collect_report_elements()
		
		self.Notice.set('Checking grammar from the report')
		
		source_language_index = self.language_list.index(self.source_language.get())
		source_language = self.language_id_list[source_language_index]
		#print('report_details', self.report_details)
		
		self.grammar_check_list = []
		for dict_key in self.report_details:
			if dict_key != 'TextTestVersion':
				if self.report_details[dict_key] != None:	
					self.grammar_check_list.append(self.report_details[dict_key])
		print('List sentence: ',self.grammar_check_list)
		self.Grammar_Check = Process(target= correct_sentence, args=(self.grammar_check_result, self.grammar_check_list, source_language,))
		self.Grammar_Check.start()
		self.after(DELAY, self.get_grammar_confirmation)

		

	def get_grammar_confirmation(self):

		self.grammar_check_result[:]
		if (self.Grammar_Check.is_alive()):
			self.after(DELAY, self.get_grammar_confirmation)
		else:

			self.grammar_corrected_list = self.grammar_check_result
			print('Grammar check result', self.grammar_corrected_list)
			if len(self.grammar_corrected_list) > 0:
				self._create_grammar_confirmation_window(self.grammar_corrected_list, ConfirmationPopup)
			else:
				self.Notice.set('Grammar check is Passed.')
	
			self.Grammar_Check.join()


	def _save_report(self,event=None):
		print('Save report')
		try:
			for widget_name in self.Configuration['BugDetails']:
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_string = _widget.get("1.0", END)
					
						self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', widget_name, _string, True)

			HeaderA = self.HeaderOptionA.get()
			HeaderB = self.HeaderOptionB.get()		
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'HeaderA', HeaderA)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'HeaderB', HeaderB)

			
		except Exception as e:
			print('Cannot sve the report:', e)
			pass


	def SaveTempReport(self, event=None):
		
		try:
			for widget_name in self.Configuration['Temp_BugDetails']:
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_string = _widget.get("1.0", END)
						self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', widget_name, _string, True)

			HeaderA = self.HeaderOptionA.get()
			HeaderB = self.HeaderOptionB.get()		
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'HeaderA', HeaderA)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'HeaderB', HeaderB)			
		except Exception as e:
			print('Cannot save the report:', e)
			pass



	def _save_project_key(self, event=None):
		
		self.glossary_id = self.project_id_select.get()
		self.glossary_id = self.glossary_id.replace('\n', '')
		if self.glossary_id in self.MyTranslator.glossary_list:
			print('Save current project key: ', self.glossary_id)
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'Translator', 'glossary_id', self.glossary_id)
			self.MyTranslator.glossary_id = self.glossary_id
			self.RenewMyTranslator()
		else:
			messagebox.showinfo('Error', "The selected project doesn't exist.")

	def _load_report(self,event=None):
	
		try:
			self.AppConfig.Refresh_Config_Data()
			self.Configuration = self.AppConfig.Config
			for widget_name in self.Configuration['BugDetails']:
				temp_string = self.Configuration['BugDetails'][widget_name]
				if temp_string != None:
					temp_string = temp_string.rstrip('\n')
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_widget.delete("1.0", END)
						_widget.insert("end", temp_string)
	
			self.HeaderOptionA.set(self.Configuration['BugDetails']['HeaderA'])
			self.HeaderOptionB.set(self.Configuration['BugDetails']['HeaderB'])
			
		except Exception as e:
			print('Fail somewhere:', e)
			pass

	def LoadTempReport(self):
		try:
			self.AppConfig.Refresh_Config_Data()
			self.Configuration = self.AppConfig.Config
			
			self.AppConfig.Refresh_Config_Data()
			self.Configuration = self.AppConfig.Config
			for widget_name in self.Configuration['Temp_BugDetails']:
				temp_string = self.Configuration['Temp_BugDetails'][widget_name]
				# Remove break line
				if temp_string != None:
					temp_string = temp_string.rstrip('\n')

				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_widget.delete("1.0", END)
						_widget.insert("end", temp_string)
	
			self.HeaderOptionA.set(self.Configuration['Temp_BugDetails']['HeaderA'])
			self.HeaderOptionB.set(self.Configuration['Temp_BugDetails']['HeaderB'])

			SourceText  = self.Configuration['Temp_BugDetails']['SimpleTranslator']
			self.SourceText.delete("1.0", END)
			if SourceText != None:
				SourceText = SourceText.rstrip('\n')

			self.SourceText.insert("end", SourceText)


		except Exception as e:
			print('Fail somewhere:', e)


	def SaveSetting(self):

		#self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'test_info_inable', 'path', self.SkipTestInfo.get())
		#self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'use_simple_template', 'path', self.UseSimpleTemplate.get())
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'test_info_inable', self.SkipTestInfo.get())
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'use_simple_template', self.UseSimpleTemplate.get())





# Class

class ConfirmationPopup:
	def __init__(self, master, dif_dict):
		self.master = master
		self.master.geometry("400x350+300+300")
		self.vars = []
		row = 1
		for string_index in range(len(dif_dict)- 1):
			sentence = dif_dict[string_index]['old']
			corrected_sentence = dif_dict[string_index]['new']
			show_text = sentence + "\t-->\t" + corrected_sentence
			self.vars.append(IntVar())
			l = Checkbutton(self.master, text= show_text, variable=self.vars[string_index]).grid(row = row, column = 1, padx=5, pady=5, stick=W)
			self.vars[string_index].set(1)
			row += 1
		Button(self.master, width = 20, text= 'Decline All').grid(row=row, column=1, columnspan=1, padx=5, pady=5, sticky=E)
		Button(self.master, width = 20, text= 'Confirm').grid(row=row, column=2, columnspan=1, padx=5, pady=5, sticky=E)


#Simple Translator
def SimpleTranslate(queue, MyTranslator, Text):
	#Translated = MyTranslator.translate(Text)
	try:
		Translated = MyTranslator.translate(Text)
		queue.put(Translated)
	except Exception as e:
		Error = ['Error to translate:' + str(e)]
		queue.put(Error)

def dual_translate(queue, MyTranslator, second_target_language, text):
	try:
		main_translation = MyTranslator.translate(text)
		temp_language = MyTranslator.to_language
		MyTranslator.set_target_language(second_target_language)
		primary_translation = MyTranslator.translate(text)
		MyTranslator.set_target_language(temp_language)
		result = {'main': main_translation, 'primary': primary_translation}
		queue.put(result)
	except Exception as e:
		Error = ['Error to translate:' + str(e)]
		queue.put(Error)

def correct_sentence(result_manager, sentence_list, language):
	language_tool = None
	#language_tool = LanguageTool(language)
	for paragraph in sentence_list:
		sentences = []
		print('paragraph', paragraph)
		sentences = language_tool.sentence_split(paragraph)
		for sentence in sentences:
			sub_sentences = sentence.split('\n')
			print('sub_sentences', sub_sentences)
			for sub_sentence in sub_sentences:
				if sub_sentence != "":
					corrected_sentence = []
					corrected_sentence = language_tool.correct(sub_sentence)
					if sub_sentence != corrected_sentence:
						result_obj = {'old': sub_sentence, 'new': corrected_sentence}
						result_manager.append(result_obj)

	print('result_manager', result_manager)
	return
#Bug Writer 
def Translate_Simple(Object, simple_template, my_translator, secondary_target_language = None):
	
	to_translate = []

	TextTestReport_index = []
	TextShouldBe_index = []
	TextReproduceSteps_index = []

	TextTestServer = Object['TextTestVersion'][0]
	TextTestClient = Object['TextTestVersion'][1]

	if Object['TextTestInfo'] != None:
		skip_test_info = False
		TextReproduceTime = Object['TextTestInfo'][0]
		TextTestAccount = Object['TextTestInfo'][1]
	else:
		skip_test_info = True
		TextReproduceTime = ""
		TextTestAccount = ""
	
	TextTestReport = Object['TextTestReport'].replace('\r', '').split('\n')
	TextShouldBe = Object['TextShouldBe'].replace('\r', '').split('\n')
	TextReproduceSteps = Object['TextReproduceSteps'].replace('\r', '').split('\n')
	
	if simple_template != 1:
		Details = '<p><b>Server : </b>&nbsp;' + TextTestServer + '</p>'
		Details += '\r\n<p><b>Client : </b>&nbsp;' + TextTestClient + '</p>'	

		strTestVersion = AddCssLayout("Test Version", Details)

		if TextReproduceTime == "":
			now = datetime.datetime.now()
			TextReproduceTime = str(date.today()) + " " + str(now.hour) + ':' + str(now.minute) 
		Details = '\r\n<p><b>Reproduce Time : </b>&nbsp;' + TextReproduceTime + '</p>'
		Details += '\r\n<p><b>Account ID/Character Name : </b>&nbsp;' + TextTestAccount + '</p>'

		strTestInfo = '\r\n' + AddCssLayout("Test Info", Details)	
	else:
		Title = "Test Version"
		Details = Add_Style(Title)
		Details += '\r\nServer : ' + TextTestServer
		Details += '\r\nClient : ' + TextTestClient
		
		strTestVersion = Details

		Title = "Test Info"
		Details = "\r\n"
		Details += Add_Style(Title)
		Details += '\r\nReproduce Time : ' + TextReproduceTime
		Details += '\r\nAccount ID/Character Name : ' + TextTestAccount

		strTestInfo = Details	

	Old_TextTestReport = []
	Old_TextShouldBe = []
	Old_TextReproduceSteps = []

	New_TextTestReport = []
	New_TextShouldBe = []
	New_TextReproduceSteps = []

	secondary_TextTestReport = []
	secondary_TextShouldBe = []
	secondary_TextReproduceSteps = []

	counter = 0

	for index in range(len(TextTestReport)):
		item = TextTestReport[index]
		if str(item) != "":
			to_translate.append(item)
			Old_TextTestReport.append(item)
			TextTestReport_index.append(counter)
			counter+=1


	for index in range(len(TextShouldBe)):
		item = TextShouldBe[index]
		if str(item) != "":
			to_translate.append(item)
			Old_TextShouldBe.append(item)
			TextShouldBe_index.append(counter)
			counter+=1


	for index in range(len(TextReproduceSteps)):
		item = TextReproduceSteps[index]
		if str(item) != "":
			to_translate.append(item)
			Old_TextReproduceSteps.append(item)
			TextReproduceSteps_index.append(counter)
			counter+=1
			
	first_language_translation = my_translator.translate(to_translate)
	if secondary_target_language not in [None, '']:
		temp_language = my_translator.to_language
		my_translator.set_target_language(secondary_target_language)
		second_language_translation = my_translator.translate(to_translate)
		my_translator.set_target_language(temp_language)
	else:
		second_language_translation = []

	for index in TextTestReport_index:
		New_TextTestReport.append(first_language_translation[index])
		if secondary_target_language != None:
			secondary_TextTestReport.append(second_language_translation[index])

	for index in TextShouldBe_index:
		New_TextShouldBe.append(first_language_translation[index])
		if secondary_target_language not in [None, '']:
			secondary_TextShouldBe.append(second_language_translation[index])

	for index in TextReproduceSteps_index:
		New_TextReproduceSteps.append(first_language_translation[index])
		if secondary_target_language not in [None, '']:
			secondary_TextReproduceSteps.append(second_language_translation[index])	

	Lang = my_translator.to_language
	
	if simple_template != 1:
		strReport = Simple_Row_CSS_Template(Lang, "Report", New_TextTestReport, Old_TextTestReport, secondary_TextTestReport)	
		strReprodSteps = Simple_Step_CSS_Template(Lang, "Reproduce Steps", New_TextReproduceSteps, Old_TextReproduceSteps, secondary_TextReproduceSteps)	
		strShouldBe = Simple_Row_CSS_Template(Lang, "Should Be", New_TextShouldBe, Old_TextShouldBe, secondary_TextShouldBe)	
	else:	
		strReport = Simple_Row_Template(Lang,  "Report", New_TextTestReport, Old_TextTestReport, second_language_translation)	
		strReprodSteps = Simple_Step_Template(Lang, "Reproduce Steps", New_TextReproduceSteps, Old_TextReproduceSteps, second_language_translation)	
		strShouldBe = Simple_Row_Template(Lang, "Should Be", New_TextShouldBe, Old_TextShouldBe, second_language_translation)	
	
	CssText = strTestVersion
	#print("Skip info:", self.SkipTestInfo.get())
	if skip_test_info == False:
		CssText += strTestInfo
	CssText += strReport
	CssText += strReprodSteps
	CssText += strShouldBe

	print('Copy to clipboard')
	copy(CssText)

def Simple_Step_CSS_Template(Lang, Title, Text_List, Text_List_Old, Text_List_Secondary = []):
	#print('Text_List_Secondary', Text_List_Secondary)
	Details = ''
	x = 1
	if Lang == 'ko':		
		for row in Text_List:
			Details += '\r\n<p><b>'+ str(x) + ')</b>&nbsp;' + remove_notranslate_tag(row) + '&nbsp;</p>'
			x += 1
		Details += '\r\n================================================='
		x = 1
		for row in Text_List_Old:
			Details += '\r\n<p><b>' + str(x) + ')</b>&nbsp;' + remove_notranslate_tag(row) + '&nbsp;</p>'
			x += 1
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			x = 1
			for row in Text_List_Secondary:
				Details += '\r\n<p><b>' + str(x) + ')</b>&nbsp;' + remove_notranslate_tag(row) + '&nbsp;</p>'
				x += 1	
	else:
		for row in Text_List_Old:
			Details += '\r\n<p><b>'+ str(x) + ')</b>&nbsp;' + remove_notranslate_tag(row) + '&nbsp;</p>'
			x += 1
		Details += '\r\n================================================='
		x = 1
		for row in Text_List:
			Details += '\r\n<p><b>' + str(x) + ')</b>&nbsp;' + remove_notranslate_tag(row) + '&nbsp;</p>'
			x += 1
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			x = 1
			for row in Text_List_Secondary:
				Details += '\r\n<p><b>' + str(x) + ')</b>&nbsp;' + remove_notranslate_tag(row) + '&nbsp;</p>'
				x += 1		
	Details = AddCssLayout(Title, Details)
	return Details

def Simple_Step_Template(Lang, Title, Text_List, Text_List_Old, Text_List_Secondary = []):
	print('Text_List_Secondary', Text_List_Secondary)
	Details = "\r\n"
	Details += Add_Style(Title)
	x = 1
	if Lang == 'ko':		
		for row in Text_List:
			Details += '\r\n' + str(x) + ') ' + remove_notranslate_tag(row)
			x += 1
		Details += '\r\n================================================='
		x = 1
		for row in Text_List_Old:
			Details += '\r\n' + str(x) + ') ' + remove_notranslate_tag(row)
			x += 1
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n' + str(x) + ') ' + remove_notranslate_tag(row)
				x += 1
	else:
		for row in Text_List_Old:
			Details += '\r\n' + str(x) + ') ' + remove_notranslate_tag(row)
			x += 1
		Details += '\r\n================================================='
		x = 1
		for row in Text_List:
			Details += '\r\n' + str(x) + ') ' + remove_notranslate_tag(row)
			x += 1
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n' + str(x) + ') ' + remove_notranslate_tag(row)
				x += 1
	return Details

def Simple_Row_CSS_Template(Lang, Title, Text_List, Text_List_Old, Text_List_Secondary = []):
	print('Text_List_Secondary', Text_List_Secondary)
	Details = ''
	if Lang == 'ko':		
		for row in Text_List:
			Details += '\r\n<p>'+ remove_notranslate_tag(row) + '&nbsp;</p>'
		Details += '\r\n================================================='
		for row in Text_List_Old:
			Details += '\r\n<p>' + remove_notranslate_tag(row) + '&nbsp;</p>'
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n<p>' + remove_notranslate_tag(row) + '&nbsp;</p>'
	else:
		for row in Text_List_Old:
			Details += '\r\n<p>'+ remove_notranslate_tag(row) + '&nbsp;</p>'
		Details += '\r\n================================================='
		for row in Text_List:
			Details += '\r\n<p>' + remove_notranslate_tag(row) + '&nbsp;</p>'
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n<p>' + remove_notranslate_tag(row) + '&nbsp;</p>'
	
	Details = AddCssLayout(Title, Details)
	return Details


#Place holder
def remove_notranslate_tag(source_text):
	return source_text
	
def Simple_Row_Template(Lang, Title, Text_List, Text_List_Old, Text_List_Secondary = []):
	#print('Text_List_Secondary', Text_List_Secondary)
	Details = "\r\n"
	Details += Add_Style(Title)
	if Lang == 'ko':		
		for row in Text_List:
			Details += '\r\n'+ remove_notranslate_tag(row)
		Details += '\r\n================================================='
		for row in Text_List_Old:
			Details += '\r\n'+ remove_notranslate_tag(row)
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n'+ remove_notranslate_tag(row)

	else:
		for row in Text_List_Old:
			Details += '\r\n'+ remove_notranslate_tag(row)
		Details += '\r\n================================================='
		for row in Text_List:
			Details += '\r\n'+ remove_notranslate_tag(row)
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n'+ remove_notranslate_tag(row)
	return Details


def AddCssLayout(Title, content):
	CssCode = '<div class="jePanel_blue" style="background-color:#f4ffff; border:1px solid #cccccc; margin-bottom:1em; margin-left:1em; margin-right:1em; margin-top:1em">'
	CssCode += '\r\n<div class="jePanelHeader" style="background-color:#9bc3ff; border-bottom-color:#cccccc; border-bottom-style:solid; border-bottom-width:1px; font-weight:bold; padding:.3em; text-align:center">[' + Title + ']</div>'
	CssCode += '\r\n<div class="jePanelContent" style="padding:.5em 2em .5em 2em">'
	CssCode += '\r\n<p>&nbsp;</p>'
	CssCode += content
	CssCode += '\r\n<p>&nbsp;</p>'
	CssCode += '\r\n</div>'
	CssCode += '\r\n</div>'
	return CssCode



def Add_Style(Text):
	return '___________' + Text + '___________' 

def main():

	MyTranslator = Queue()
	return_text = Queue()
	MyManager = Manager()
	grammar_check_result = MyManager.list()
	tm_manager = MyManager.list()
	language_tool_enable = False

	#root = Tk()
	root = Window(themename="minty")
	#root.iconbitmap(r"theme\ico\ico.ico")
	
	#root.geometry("400x350+300+300")
	#application = MyTranslatorHelper(root, return_text, MyTranslator, grammar_check_result = grammar_check_result, tm_manager = tm_manager, language_tool_enable = language_tool_enable)

	try:
		#root.attributes('-topmost', True)
		application = MyTranslatorHelper(root, return_text, MyTranslator, grammar_check_result = grammar_check_result, tm_manager = tm_manager, language_tool_enable = language_tool_enable)
		
		icon_path = resource_path('resource/translate_helper.ico')
		print(icon_path)
		if os.path.isfile(icon_path):
			root.iconbitmap(icon_path)
			
		#root.attributes('-topmost', False)
		root.mainloop()
		try:
			application.MyTranslator.send_tracking_record()
		except:
			pass	
	except Exception as e:	
		try:
			root.withdraw()
		except:
			pass
		try:
			#from google.cloud import logging
			AppConfig = ConfigLoader(Writer = True)
			Configuration = AppConfig.Config
			license_file_path = Configuration['Translator']['license_file']
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = license_file_path
			client = logging.Client()
		except:
			print('Fail to communicate with logging server')
			print("Usage logging error:", e)
			messagebox.showinfo(title='Critical error', message=e)
			return

		log_name = 'critical-error'
		logger = client.logger(log_name)
		try:
			name = os.environ['COMPUTERNAME']
		except:
			print('Fail to get computer name')
			name = 'Anonymous'

		text_log = name + ', ' + str(e) + ', ' + version

		try:
			logger.log_text(text_log)
		except:
			print('Fail to send log to server.')
			
		print("error message:", e)	
		messagebox.showinfo(title='Critical error', message=e)



if __name__ == '__main__':
	if sys.platform.startswith('win'):
		multiprocessing.freeze_support()

	#AIOTracker.GenerateToolUsageEvent(version)
	#AIOTracker.UpdateTrackingData()

	main()