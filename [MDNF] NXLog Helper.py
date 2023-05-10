#System variable and io handling
import sys
import os
import re

#Regular expression handling

#Object copy, handle excel style
import copy
#Get timestamp
#import time
#function difination
# Copy to clipboard
from pyperclip import copy, paste
#from tkinter import *
#from tkinter.ttk import *
from ttkbootstrap import Style
from ttkbootstrap import Radiobutton, Button
from tkinter import Tk, Frame, Toplevel

# Widget type
from tkinter import filedialog, messagebox
# Variable type
from tkinter import IntVar, StringVar
# Wrap type
# sticky state
from tkinter import W, END,X, Y, BOTH, TOP
# Config state
from tkinter import DISABLED, NORMAL

from tkhtmlview import HTMLScrolledText
import textwrap
#from tkinter import filedialog
#from tkinter import messagebox
#from tkinter import ttk

#import configparser
import multiprocessing
from multiprocessing import Queue, Process, Manager

import pickle
import queue 

from libs.aiotranslator import generate_translator

from libs.aioconfigmanager import ConfigLoader

from libs.cloudconfig import CloudConfigLoader

from libs.grammarcheck import LanguageTool

from libs.version import get_version
from libs.tkinter_extension import ConfirmationPopup, Generate_NXLog_UI


from libs.tkinter_extension import Generate_NXLog_Tab_UI, Generate_BugWriter_Menu_UI, Generate_Translate_Setting_UI, Generate_Template_UI
from libs.tkinter_extension import Generate_SimpleTranslator_UI, BugWriter_BottomPanel
from libs.tkinter_extension import init_writer_theme
from libs.NXLogTemplate import Template as Template
import webbrowser

from google.cloud import logging

tool_display_name = "[MDNF] NXLog Helper"
tool_name = 'writer'
REV = 4204
ver_num = get_version(REV) 
#VERSION = tool_display_name  + " " +  ver_num + " | Language Tool v5.6"

DELAY = 20
DELAY2 = 300000

isSimpleTranslated = False

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


		self.parent = parent
		self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
		

		Frame.__init__(self, parent)
		self.pack(side=TOP, expand=Y, fill=X)
		self.style =  Style()


		self.MyTranslator_Queue = MyTranslator_Queue
		self.MyTranslator = None

		self.language_tool_enable = language_tool_enable
		self.grammar_check_result = grammar_check_result
		self.tm_manager = tm_manager
		self.return_text = TranslationQueue

		self.grammar_check_list = []
		self.grammar_corrected_list = []

		self.SOURCE_WIDTH = 75
		self.BUTTON_SIZE = 20
		self.HALF_BUTTON_SIZE = 15
		self.ROW_SIZE = 24

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
		self.TitleForReport = ""
		self.Separator = '====================================================='
		
		self.language_id_list = ['', 'ko', 'en', 'cn', 'jp', 'vi']
		self.language_list = ['', 'Hangul', 'English', 'Chinese', 'Japanese', 'Vietnamese']
		self.source_text = ''
		self.main_translation = ''
		self.primary_translation = ''

		self.text_widgets = []
		self.label_widgets = []
		self.menu_widgets = []
		self.frame_widgets = []

		self._after_id = None

		self.Title_Template = []
		self.titleIndex=[]
		for index in Template.Title:
			self.titleIndex.append(index)
		for title in Template.Title:
			self.Title_Template.append(Template.Title[title])

		self.bodyAction_Template = []
		self.bodyActionIndex=[]
		for index in Template.BodyAction:
			self.bodyActionIndex.append(index)
		for action in Template.BodyAction:
			self.bodyAction_Template.append(Template.BodyAction[action])

		self.bodyValue_Template = []
		self.bodyValueIndex=[]
		for index in Template.BodyValue:
			self.bodyValueIndex.append(index)
		for value in Template.BodyValue:
			self.bodyValue_Template.append(Template.BodyValue[value])

		self.init_App_Setting()
		
		if self.AppLanguage != 'kr':
			from libs.languagepack import LanguagePackEN as LanguagePack
		else:
			from libs.languagepack import LanguagePackKR as LanguagePack

		self.report_details = None

		self.LanguagePack = LanguagePack
		
		init_writer_theme(self)
		
		self.init_ui()
		self.init_UI_setting()
		
		#self.change_color()

		if REV < int(self.latest_version):
			self.Error('Current version is lower than the minimal version allowed. Please update.')	
			
			webbrowser.open_new(r"https://confluence.nexon.com/display/NWMQA/Translate+Helper")
			self.quit()
			return

		if self.banning_status:
			self.Error('You\'re not allowed to use the tool. If you feel that it\'s unfair, please contact with your manager for more information.')	
			self.quit()
			return

		if self.LicensePath.get() != "":
			self.generate_translator_engine()
		else:
			self.Error('No license selected, please select the key in Translate setting.')	
		
		self.parent.withdraw()
		self.parent.update_idletasks()
		self.parent.deiconify()
		
		
		self.parent.minsize(self.parent.winfo_width(), self.parent.winfo_height())
		x_cordinate = int((self.parent.winfo_screenwidth() / 2) - (self.parent.winfo_width() / 2))
		y_cordinate = int((self.parent.winfo_screenheight() / 2) - (self.parent.winfo_height() / 2))
		self.parent.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

		self.after(DELAY2, self.status_listening)
		self.LoadTempReport()	

		
	def Error(self, ErrorText):
		messagebox.showinfo('Translate error...', ErrorText)	
		
	# Menu function
	def handle_wait(self,event):
		# cancel the old job
		if self._after_id is not None:
			self.after_cancel(self._after_id)
		# create a new job
		self._after_id = self.after(DELAY2, self.SaveTempReport)

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

	def status_listening(self):
		
		if self.MyTranslator == None:
			self.after(DELAY2, self.status_listening)
		else:
			self.after(DELAY2, self.status_listening)
		#print('Device status:', device_status, time.time()- Start)

	def init_ui(self):
		self.parent.resizable(False, False)
		self.parent.title(VERSION)

		Generate_BugWriter_Menu_UI(self)
		Generate_NXLog_Tab_UI(self)

		try:
			Generate_NXLog_UI(self, self.NXLogTab)
			Generate_Template_UI(self, self.TemplateTab)
			Generate_SimpleTranslator_UI(self, self.SimpleTranslatorTab)
			Generate_Translate_Setting_UI(self, self.TranslateSettingTab)
			self.bottom_panel = BugWriter_BottomPanel(self)
			#Generate_Theme_Setting_UI(self, self.ThemeSettingTab)
			self.SourceText.bind('<KeyRelease>', self.SourceTextCallback)
			self.bottom_panel = BugWriter_BottomPanel(self)

		except Exception as e:
			print(f'An error occurs while initializing UI: {e}')

		#ADB_Controller(self.ADB_Controller)
		#self.Generate_Search_UI(self.Searcher)

		#self.Init_Translator_Config
		

	# Init functions
	# Some option is saved for the next time use
	def init_App_Setting(self):
		print('init_App_Setting')
		self.UseSimpleTemplate = IntVar()

		self.LicensePath = StringVar()
		self.Transparent = IntVar()

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

		Transparent  = self.Configuration['Bug_Writer']['Transparent']
		self.Transparent.set(Transparent)

		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = license_file_path
		self.TMPath.set(self.Configuration['Translator']['translation_memory'])

		self.bucket_id = self.Configuration['Translator']['bucket_id']
		self.db_list_uri = self.Configuration['Translator']['db_list_uri']
		self.project_bucket_id = self.Configuration['Translator']['project_bucket_id']

		self.glossary_id = self.Configuration['Translator']['glossary_id']

		self.used_theme = self.Configuration['Used_Theme']['Bug_Writer']

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
		self.titleTemplate = StringVar()
		self.bodyActionTemplate = StringVar()
		self.bodyValueTemplate = StringVar()
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


		self.simple_source_language.set(self.language_list[self.Configuration['Simple_Translator']['source_lang']])
		self.simple_target_language.set(self.language_list[self.Configuration['Simple_Translator']['target_lang']])
		simple_secondary_language = self.Configuration['Simple_Translator']['secondary_target_lang']
		
		if simple_secondary_language == 6:
			self.simple_secondary_target_language.set('')
		else:
			self.simple_secondary_target_language.set(self.language_list[simple_secondary_language])

	def select_theme_name(self):
		"""Save the theme name value to Configuration and change
		the theme based on the selection in the UI.
		
		Args:
			config_theme_name -- str
				Theme name retrieved from config. (Default: '')
		"""
		try:
			""""
			style = Style(self.parent) # self.parent is root
			theme_name = self.strvar_theme_name.get()
			
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Bug_Writer',
				'theme_name',
				theme_name, True)
			self.change_theme_color(theme_name)
			style.theme_use(theme_name)
			self.apply_theme_color()
			self.btn_remove_theme.configure(state=NORMAL)
			"""
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
	
	def SetLanguageEnglish(self):
		self.AppLanguage = 'en'
		self.SaveAppLanguage(self.AppLanguage)
		self.rebuild_UI()

	def SaveAppLanguage(self, language):

		self.Notice.set(self.LanguagePack.ToolTips['AppLanuageUpdate'] + " "+ language) 
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'app_lang', language)
	
	def SaveAppTransparency(self, transparency):
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'Transparent', transparency)

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
			return str(path).replace('\\', '/')
	
	def CorrectExt(self, path, ext):
		if path != None and ext != None:
			Outputdir = os.path.dirname(path)
			baseName = os.path.basename(path)
			sourcename = os.path.splitext(baseName)[0]
			newPath = self.CorrectPath(Outputdir + '/'+ sourcename + '.' + ext)
			return newPath

	def _create_grammar_confirmation_window(self, dif_dict, diff_index, _class):
		self.Child_Window = Toplevel(self.master)
		self.Child_Window.resizable(False, False)
		self.Child_Window.title("Confirm the correction")
		_class(self, dif_dict, diff_index)
	
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
	
			try:
				db_count = str(self.MyTranslator.glossary_size)
			except:
				db_count = 0
			
			self.DictionaryStatus.set(db_count)
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
			
			#self.TextTitle.focus_set()

			self.TranslatorProcess.join()
			self.LoadTempReport()
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
			messagebox.showerror('Error', 'Source and Primary Target language is the same.')	
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
		global isSimpleTranslated
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
					isSimpleTranslated = True
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
		self.source_language
	
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
		global isSimpleTranslated
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
					isSimpleTranslated = True
				else:
					#Show = "\n".join(Translated)
					#self.TargetText.insert("end", 'Fail to translate')
					self.Notice.set(self.LanguagePack.ToolTips['TranslateFail'])	
				self.dual_translate_process.join()
			except queue.Empty:
				pass			

	#Execute function
	def SourceTextCallback(self, event):
		global isSimpleTranslated
		isSimpleTranslated = False

	def BtnCopy(self):
		#self.get_source_text()			
		#Translated = self.TargetText.get("1.0", END)
		#Translated = Translated.replace('\r', '')
		if isSimpleTranslated:
			copy(self.TargetText.get("1.0", END).strip())
			self.Notice.set(self.LanguagePack.ToolTips['Copied'])
		else:
			if messagebox.askokcancel(tool_display_name, "Translation mismatches. Please double check!\nIf you have translated, press OK to copy."):			
				copy(self.TargetText.get("1.0", END).strip())
				self.Notice.set(self.LanguagePack.ToolTips['Copied'])


	def btn_bilingual_copy(self):
		"""
		[Bilingual] button in Simple Translator.
		Copy the text in Source Text and Target Text to the clipboard when clicked.
		"""

		#self.get_source_text()

		# Copy all text in the Source Text and Target Text textbox
		bilingual = self.TargetText.get("1.0", END).strip() + "\n"
		bilingual += self.Separator + "\n"
		bilingual += self.SourceText.get("1.0", END).strip()
		if isSimpleTranslated:
			copy(bilingual)
			self.Notice.set(self.LanguagePack.ToolTips['Copied'])
		else:
			if messagebox.askokcancel(tool_display_name, "Translation mismatches. Please double check!\nIf you have translated, press OK to copy."):
				copy(bilingual)
				self.Notice.set(self.LanguagePack.ToolTips['Copied'])

	def btn_trilingual(self):
		
		primary_target_language = self.language_id_list[self.language_list.index(self.simple_secondary_target_language.get())]
		if primary_target_language == "":
			messagebox.showinfo('Warning', 'Secondary target language is EMPTY.\nPlease select the secondary target language or use Bilingual Copy instead.')	
			self.btn_bilingual_copy()
			return

		trilingual = self.main_translation + "\n"	
		trilingual += self.Separator + "\n"
		trilingual += self.source_text + "\n"
		trilingual += self.Separator + "\n"
		trilingual += self.primary_translation
		if isSimpleTranslated:
			copy(trilingual)
			self.Notice.set(self.LanguagePack.ToolTips['Copied'])
		else:
			if messagebox.askokcancel(tool_display_name, "Translation mismatches. Please double check!\nIf you have translated, press OK to copy."):
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
		self.nx_GetTitleBtn.configure(state=DISABLED)
		self.nx_GetReportBtn.configure(state=DISABLED)
		#self.CorrectGrammarBtn.configure(state=DISABLED)
		self.TranslateBtn.configure(state=DISABLED)
		self.dual_translate_btn.configure(state=DISABLED)
		#self.RenewTranslator.configure(state=DISABLED)
		#self.RenewTranslatorMain.configure(state=DISABLED)
		self.RenewTranslatorMain.configure(state=DISABLED)
		
		self.nx_secondary_target_language_select.configure(state=DISABLED)
		self.nx_target_language_select.configure(state=DISABLED)
		self.nx_source_language_select.configure(state=DISABLED)

		self.simple_secondary_target_language_select.configure(state=DISABLED)
		self.simple_target_language_select.configure(state=DISABLED)
		self.simple_source_language_select.configure(state=DISABLED)
		
		self.project_id_select.configure(state=DISABLED)

		#self.Translate_bilingual_Btn.configure(state=DISABLED)
		self.TranslateBtn.configure(state=DISABLED)

		self.nx_GetTitleBtn.configure(state=DISABLED)
		self.nx_GetReportBtn.configure(state=DISABLED)
		#self.db_correction.configure(state=DISABLED)

	def enable_btn(self):
		self.nx_GetTitleBtn.configure(state=NORMAL)
		self.nx_GetReportBtn.configure(state=NORMAL)
		#self.CorrectGrammarBtn.configure(state=NORMAL)
		self.TranslateBtn.configure(state=NORMAL)
		self.dual_translate_btn.configure(state=NORMAL)
		#self.RenewTranslator.configure(state=NORMAL)
		#self.RenewTranslatorMain.configure(state=NORMAL)
		self.RenewTranslatorMain.configure(state=NORMAL)

		self.nx_secondary_target_language_select.configure(state=NORMAL)
		self.nx_target_language_select.configure(state=NORMAL)
		self.nx_source_language_select.configure(state=NORMAL)

		self.simple_secondary_target_language_select.configure(state=NORMAL)
		self.simple_target_language_select.configure(state=NORMAL)
		self.simple_source_language_select.configure(state=NORMAL)

		self.project_id_select.configure(state=NORMAL)
		self.nx_GetTitleBtn.configure(state=NORMAL)
		self.nx_GetReportBtn.configure(state=NORMAL)

		#self.Translate_bilingual_Btn.configure(state=NORMAL)
		#self.db_correction.configure(state=NORMAL)
		

	def RenewMyTranslator(self):
		self.disable_btn()
		del self.MyTranslator
		self.MyTranslator = None
		self.HeaderStatus.set('0')
		self.generate_translator_engine()

	#Option functions

	def UpdateHeaderList(self):
		try:
			header_count = str(len(self.MyTranslator.header))
		except:
			header_count = 0
		self.HeaderStatus.set(header_count)
		
	def ResetReport(self, event):
		self.ResetTestReport()

	def analyze_terminology(self):
		for term in self.MyTranslator.dictionary:
			if term not in [' ']:
				#term = term.lower()
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
				term = term.lower()
				self.TextTestReport.highlight_fault_pattern(term, 'red')
				self.TextTitle.highlight_fault_pattern(term, 'red')
				self.TextReproduceSteps.highlight_fault_pattern(term, 'red')
				self.TextShouldBe.highlight_fault_pattern(term, 'red')
				

	def analyze_report_grammar(self, event = None):
		self.disable_btn()
		self.collect_report_elements()
		self.confirm_report_grammar()
		
	def analyze_simple_grammar(self, event=None):
		self.disable_btn()
		source_language = self.language_id_list[self.language_list.index(self.simple_source_language.get())]
		if source_language == 'en':
			self.collect_simple_text()
			self.confirm_report_grammar()

		
	def GetTitle(self, event = None):
		self.disable_btn()
		copy("")
		self.event = event
		target_language = self.language_id_list[self.language_list.index(self.target_language.get())]
		source_language = self.language_id_list[self.language_list.index(self.source_language.get())]
		if target_language != self.MyTranslator.to_language or source_language != self.MyTranslator.from_language:
			self.MyTranslator.set_language_pair(source_language = source_language, target_language = target_language)
			print('Update language pair from: ', source_language, ' to ',  target_language)
		self.Notice.set(self.LanguagePack.ToolTips['GenerateBugTitle'])
		self.strSourceTitle = self.nx_TextTitle.get("1.0", END).rstrip()
		self.Title_Translate = Process(target=SimpleTranslate, args=(self.return_text, self.MyTranslator, self.strSourceTitle))
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
				HeaderA = self.table.get("1.0", END).rstrip()
				HeaderB = self.column.get("1.0", END).rstrip()
				if HeaderA == "":
					raise Exception
				if (HeaderB == ""):
					TargetHeader = "[" + HeaderA + "]"
				else:
					TargetHeader = "[" + HeaderA + "]" + " <" + HeaderB + ">"
				Title = TargetHeader + " "  +  self.TargetTitle
				copy(str(Title))
				self.Notice.set(self.LanguagePack.ToolTips['GeneratedBugTitle'])
				self.Title_Translate.join()
			except Exception as e:
				print(e)
				self.Notice.set(self.LanguagePack.ToolTips['GenerateBugTitleFail'])

			self.enable_btn()	
		return

	#Reset buttons
	def ResetTestReport(self):
		self.TextTitle.delete("1.0", END)
		self.jsondata.delete("1.0", END)
		self.nx_TextTestReport.delete("1.0", END)
		self.nx_TextShouldBe.delete("1.0", END)	
		return
	#END
	
	#GUI function
	def collect_report_elements(self):
		To_Translate = {}
		To_Translate['Phenomenon'] = self.nx_TextTestReport.get("1.0", END)
		To_Translate['Expected'] = self.nx_TextShouldBe.get("1.0", END)
		self.report_details = To_Translate

	def collect_simple_text(self):
		To_Translate = {}
		To_Translate['Simple'] = self.SourceText.get("1.0", END)
		self.report_details = To_Translate

	def update_report_elements(self):
		for key in self.report_details:
			report = self.report_details[key]
			if key == 'TextShouldBe':
				self.TextShouldBe.delete("1.0", END)
				self.TextShouldBe.insert("end", report)
			elif key == 'TextReproduceSteps':
				self.TextReproduceSteps.delete("1.0", END)
				self.TextReproduceSteps.insert("end", report)	
			elif key == 'TextTestReport':
				self.TextTestReport.delete("1.0", END)
				self.TextTestReport.insert("end", report)
			elif key == 'Title':
				self.TextTitle.delete("1.0", END)
				self.TextTitle.insert("end", report)
			elif key == 'Simple':
				self.SourceText.delete("1.0", END)
				self.SourceText.insert("end", report)
			else:
				pass

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
		nxlog_data = [self.table.get("1.0", END).rstrip(), self.column.get("1.0", END).rstrip(), self.jsondata.get("1.0", END).rstrip()]
		self.BugWriter = Process(target=Translate_Simple, args=(self.report_details, self.MyTranslator, nxlog_data, secondary_target_language))
		self.BugWriter.start()
		self.after(DELAY, self.GetBugDetails)
		self.TitleForReport = ""

	def GetBugDetails(self):
		self.disable_btn()
		self.Notice.set(self.LanguagePack.ToolTips['ClipboardRemoved'])

		if (self.BugWriter.is_alive()):
			self.after(DELAY, self.GetBugDetails)
		else:
			self.Notice.set(self.LanguagePack.ToolTips['GeneratedBugReport'])

			self.BugWriter.join()
			self.html_content = paste()
			self.html_content = '#my{zoom: 75%;}\n' + self.html_content
			self.enable_btn()

	def generate_report(self, event=None):
		self.collect_report_elements()
		self.GenerateReportCSS()

	def confirm_simple_garmmar(self):
		self.collect_simple_text()
		self.Notice.set('Checking grammar in the report')
		
		source_language_index = self.language_list.index(self.source_language.get())
		source_language = self.language_id_list[source_language_index]
		
		
		#self.grammar_check_list = {}
		self.grammar_index_list = {}
		self.for_grammar_check = []
		index = 0
		for dict_key in self.report_details:
			self.grammar_index_list[dict_key] = []
			if dict_key not in ['EnvInfo', 'Reproducibility']:
				if self.report_details[dict_key] != None:
					all_sentence = self.report_details[dict_key].rstrip().split('\n')
					for sentence in all_sentence:
						if sentence.isprintable():
							self.for_grammar_check.append(sentence.rstrip())
							self.grammar_index_list[dict_key].append(index)
							index+=1
			else:
				del self.grammar_index_list[dict_key]

		self.grammar_check_result[:]= []
		self.Grammar_Check = Process(target= correct_sentence, args=(self.grammar_check_result, self.for_grammar_check, source_language,))
		self.Grammar_Check.start()
		self.after(DELAY, self.get_grammar_confirmation)


	def confirm_report_grammar(self):
		#self.collect_report_elements()
		
		self.Notice.set('Checking grammar in the simple translator')
		
		source_language_index = self.language_list.index(self.source_language.get())
		source_language = self.language_id_list[source_language_index]
		
		
		#self.grammar_check_list = {}
		self.grammar_index_list = {}
		self.for_grammar_check = []
		index = 0
		for dict_key in self.report_details:
			self.grammar_index_list[dict_key] = []
			if dict_key not in ['EnvInfo', 'Reproducibility']:
				if self.report_details[dict_key] != None:
					all_sentence = self.report_details[dict_key].rstrip().split('\n')
					for sentence in all_sentence:
						if sentence.isprintable():
							self.for_grammar_check.append(sentence.rstrip())
							self.grammar_index_list[dict_key].append(index)
							index+=1
			else:
				del self.grammar_index_list[dict_key]

		self.grammar_check_result[:]= []
		self.Grammar_Check = Process(target= correct_sentence, args=(self.grammar_check_result, self.for_grammar_check, source_language,))
		self.Grammar_Check.start()
		self.after(DELAY, self.get_grammar_confirmation)

	def get_grammar_confirmation(self):	
		if (self.Grammar_Check.is_alive()):
			self.after(DELAY, self.get_grammar_confirmation)
		else:
			self.grammar_corrected_list = self.grammar_check_result
			self.confirmed_list = []
			self.confirmed_index_list = []
			for i in range(len(self.grammar_corrected_list)):
				if self.grammar_corrected_list[i] != self.for_grammar_check[i]:
					self.confirmed_list.append({'old': self.for_grammar_check[i], 'new': self.grammar_corrected_list[i]})
					self.confirmed_index_list.append(i)

			if len(self.confirmed_list) > 0:
				self._create_grammar_confirmation_window(self.confirmed_list, self.confirmed_index_list, ConfirmationPopup)
			else:
				#messagebox.showinfo('Grammar check is done', 'The report is OK')
				self.Notice.set('Grammar check is done')
				self.enable_btn()
	
			self.Grammar_Check.join()

	def _save_report(self,event=None):
		print('Save report')
		try:		
			for widget_name in self.Configuration['NXLog']:
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_string = _widget.get("1.0", END)
						self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'NXLog', widget_name, _string, True)

			for widget_name in self.Configuration['Simple_Translator']:
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_string = _widget.get("1.0", END)
						self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Simple_Translator', widget_name, _string, True)
			
		except Exception as e:
			print('Cannot save the report:', e)
			pass


	def SaveTempReport(self, event=None):
		print('Save temp report')
		try:		
			for widget_name in self.Configuration['Temp_NXLog']:
				
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_string = _widget.get("1.0", END)
						self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_NXLog', widget_name, _string, True)

			for widget_name in self.Configuration['Simple_Translator']:
				
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_string = _widget.get("1.0", END)
						self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Simple_Translator', widget_name, _string, True)				
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
			
			for widget_name in self.Configuration['NXLog']:
				temp_string = self.Configuration['NXLog'][widget_name]
				if temp_string != None and isinstance(temp_string, str):
					temp_string = temp_string.rstrip('\n')
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_widget.delete("1.0", END)
						_widget.insert("end", temp_string)

			for widget_name in self.Configuration['Simple_Translator']:
				temp_string = self.Configuration['Simple_Translator'][widget_name]
				if temp_string != None and isinstance(temp_string, str):
					temp_string = temp_string.rstrip('\n')
				for widget in dir(self):
					if widget == widget_name:
						if isinstance(temp_string, str):	
							_widget = getattr(self, widget)
							_widget.delete("1.0", END)
							_widget.insert("end", temp_string)
			print(self.Configuration['Simple_Translator']['source_lang'])
			self.simple_source_language.set(self.language_list[self.Configuration['Simple_Translator']['source_lang']])
			self.simple_target_language.set(self.language_list[self.Configuration['Simple_Translator']['target_lang']])
			self.simple_secondary_target_language.set(self.language_list[self.Configuration['Simple_Translator']['secondary_target_lang']])			 
		except Exception as e:
			print('Fail somewhere:', e)
			pass

	def LoadTempReport(self):
		try:
			self.AppConfig.Refresh_Config_Data()
			self.Configuration = self.AppConfig.Config
			for widget_name in self.Configuration['Temp_NXLog']:
				temp_string = self.Configuration['Temp_NXLog'][widget_name]
				if temp_string != None and isinstance(temp_string, str):
					temp_string = temp_string.rstrip('\n')					
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_widget.delete("1.0", END)
						_widget.insert("end", temp_string)

			for widget_name in self.Configuration['Simple_Translator']:
				temp_string = self.Configuration['Simple_Translator'][widget_name]
				if temp_string != None and isinstance(temp_string, str):
					temp_string = temp_string.rstrip('\n')
				for widget in dir(self):
					if widget == widget_name:
						_widget = getattr(self, widget)
						_widget.delete("1.0", END)
						_widget.insert("end", temp_string)
			self.simple_source_language.set(self.language_list[self.Configuration['Simple_Translator']['source_lang']])
			self.simple_target_language.set(self.language_list[self.Configuration['Simple_Translator']['target_lang']])
			self.simple_secondary_target_language.set(self.language_list[self.Configuration['Simple_Translator']['secondary_target_lang']])

		except Exception as e:
			print('Fail somewhere:', e)


	def SaveSetting(self):

		#self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'test_info_inable', 'path', self.SkipTestInfo.get())
		#self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'use_simple_template', 'path', self.UseSimpleTemplate.get())
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'test_info_inable', self.SkipTestInfo.get())
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'use_simple_template', self.UseSimpleTemplate.get())


# Class

class ConfirmationPopup:
	def __init__(self, master, dif_dict, index_list):
		self.Root = master
		self.master = master.Child_Window
		#self.master.geometry("400x350+300+300")
		self.index = index_list
		row = 1
		self.All_Widget = []
		self.diff = dif_dict
		for diff_object in dif_dict:
			widget = {}
			sentence = diff_object['old'].replace('\r', '')
			corrected_sentence = diff_object['new'].replace('\r', '')
			widget['var'] = IntVar()
			_wraped_sentence = textwrap.fill(sentence, 40)
			_wraped_corrected_sentence = textwrap.fill(corrected_sentence, 40)
			row_count = len(_wraped_corrected_sentence) + 1
			a = Radiobutton(self.master, width= 40, text=  _wraped_sentence, value=1, variable= widget['var'])
			a.grid(row=row, column=1, columnspan=3, rowspan= row_count, padx=5, pady=5, sticky=W)
			#a.configure(wraplength=30 + 10)  
			
			b = Radiobutton(self.master, width= 40, text=  _wraped_corrected_sentence, value=2, variable= widget['var'])
			b.grid(row=row, column=4, columnspan=3, rowspan= row_count, padx=5, pady=5, sticky=W)
			#b.configure(wraplength=30 + 10)  
		
			widget['var'].set(2)
			self.All_Widget.append(widget)
			row += row_count
		Button(self.master, width = 20, text= 'Accept All', command = self.Accept_All, style=self.Btn_Style).grid(row=row, column=1, columnspan=2, padx=5, pady=5)
		Button(self.master, width = 20, text= 'Decline All', command = self.Decline_All, style=self.Btn_Style).grid(row=row, column=3, columnspan=2, padx=5, pady=5)
		Button(self.master, width = 20, text= 'Confirm', command = self.Confirm_Correction, style=self.Btn_Style).grid(row=row, column=5, columnspan=2, padx=5, pady=5)

		self.master.protocol("WM_DELETE_WINDOW", self.Confirm_Correction)	

	def Accept_All(self):
		for widget in self.All_Widget:
			widget['var'].set(2)
		self.Confirm_Correction()

	def Decline_All(self):
		for widget in self.All_Widget:
			widget['var'].set(1)
		self.Confirm_Correction()	

	def Confirm_Correction(self):
		i = 0
		for widget in self.All_Widget:
			result = widget['var'].get()
			if result == 2:
				to_update = self.diff[i]['new']
				_index_in_check_list = self.index[i]
				self.Root.for_grammar_check[_index_in_check_list] = to_update
			i+=1

		for dict_key in self.Root.grammar_index_list:	
			all_index = self.Root.grammar_index_list[dict_key]
			temp_list = []
			for index in all_index:
				temp_list.append(self.Root.for_grammar_check[index])
			self.Root.report_details[dict_key] = ('\n').join(temp_list)
		self.master.destroy()
		self.Root.update_report_elements()
		self.Root.enable_btn()
		#self.Root.GenerateReportCSS()

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
	language_tool = LanguageTool(language)
	#print('sentence_list', sentence_list)
	for sentence in sentence_list:
		corrected_sentence = language_tool.correct(sentence)
		#print('corrected_sentence', corrected_sentence)	
		result_manager.append(corrected_sentence)
	language_tool.language_tool.close()
	return

def ListToString(List):
	Details = ''
	isList = False
	for row in List:
		if (row[0] == "*"):
			if (isList == False):
				isList = True
			Details += row + '\r\n'
		elif(row[0] != "*" and isList == True):
			isList = False
			Details += '\r\n' + row + '\r\n\r\n'
		else:
			Details += row + '\r\n\r\n'
	return Details

#Bug Writer 
 
def Translate_Simple(Object, my_translator, nxlog, secondary_target_language = None):
	to_translate = []
	TextTestReport_index = []
	TextShouldBe_index = []

	TextTestReport = Object['Phenomenon'].replace('\r', '').split('\n')
	TextShouldBe = Object['Expected'].replace('\r', '').split('\n')

	Old_TextTestReport = []
	Old_TextShouldBe = []

	New_TextTestReport = []
	New_TextShouldBe = []

	secondary_TextTestReport = []
	secondary_TextShouldBe = []

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
	
	Lang = my_translator.to_language	
	CssText = ''
	CssText += '*[시점]*'
	CssText += '\r\n\r\n'
	CssText += nxlog[0]
	CssText += '\r\n\r\n'
	CssText += '*[필드]*'
	CssText += '\r\n\r\n'
	CssText += nxlog[1].replace(" ", "\r\n\r\n")
	CssText += '\r\n\r\n'
	CssText += '*[현상]*'
	CssText += '\r\n\r\n'
	CssText += ListToString(New_TextTestReport)
	CssText += '*[기대결과]*'
	CssText += '\r\n\r\n'
	CssText += ListToString(New_TextShouldBe)
	CssText += '*[로그 전문]*'
	CssText += '\r\n\r\n'
	CssText += '{code:java}'
	CssText += '\r\n'
	CssText += nxlog[2]
	CssText += '\r\n'
	CssText += '{code}'
	CssText += '\r\n\r\n'
	CssText += '*제2언어 - Secondary language*'
	CssText += '\r\n\r\n'
	CssText += '*[Table]*'
	CssText += '\r\n\r\n'
	CssText += nxlog[0]
	CssText += '\r\n\r\n'
	CssText += '*[Column]*'
	CssText += '\r\n\r\n'
	CssText += nxlog[1].replace(" ", "\r\n\r\n")
	CssText += '\r\n\r\n'
	CssText += '*[Phenomenon]*'
	CssText += '\r\n\r\n'
	CssText += ListToString(Old_TextTestReport)
	CssText += '*[Expected Result]*'
	CssText += '\r\n\r\n'
	CssText += ListToString(Old_TextShouldBe)
	print('Copy to clipboard')
	pre_defined_words = [nxlog[0], "iOS", "AOS", "PC"]
	for word in pre_defined_words:
		CssText = CssText.replace(word.lower(), word.strip())
	copy(CssText)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
	print('Create shareable Memory variable')
	MyTranslator = Queue()
	return_text = Queue()
	MyManager = Manager()
	grammar_check_result = MyManager.list()
	tm_manager = MyManager.list()

	language_tool_enable = True

	try:
		download_path = os.environ.get('LTP_PATH',os.path.join(os.path.expanduser("~"), ".cache", "language_tool_python"))
		print('Language tool path:', download_path)
		if os.path.isdir(download_path):
			LangTool = LanguageTool('en')
			print(LangTool)
			LangTool.language_tool.close()
		else:
			language_tool_enable = False
	except Exception as e:
		print("Error", e)
		language_tool_enable = False
	global VERSION
	if language_tool_enable:
		VERSION = tool_display_name  + " " +  ver_num + " | Language Tool v5.6"
	else:
		VERSION = tool_display_name  + " " +  ver_num	

	root = Tk()
	#application = MyTranslatorHelper(root, return_text, MyTranslator, grammar_check_result = grammar_check_result, tm_manager = tm_manager, language_tool_enable = language_tool_enable)
		
	try:
		print('Update UI')


		application = MyTranslatorHelper(root, return_text, MyTranslator, grammar_check_result = grammar_check_result, tm_manager = tm_manager, language_tool_enable = language_tool_enable)
		#application.pack(fill="both", expand=True)
				
		icon_path = resource_path('resource/translate_helper.ico')
		print(icon_path)
		if os.path.isfile(icon_path):
			root.iconbitmap(icon_path)
		#root.deiconify()
		#root.configure(**darkmode) 
	
		
		root.mainloop()
		print('Send usage report')
	except Exception as e:
		
		root.withdraw()

		try:
			#from google.cloud import logging
			AppConfig = ConfigLoader(Writer = True)
			Configuration = AppConfig.Config
			license_file_path = Configuration['Translator']['license_file']
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = license_file_path
			client = logging.Client()
		except:
			print('Fail to communicate with logging server')
			print("error message:", e)
			messagebox.showinfo(title='Critical error', message=e)
			return

		log_name = 'critical-error'
		logger = client.logger(log_name)
		try:
			name = os.environ['COMPUTERNAME']
		except:
			print('Fail to get computer name')
			name = 'Anonymous'

		text_log = name + ', ' + str(e) + ', ' + VERSION

		try:
			logger.log_text(text_log)
		except:
			print('Fail to send log to server.')
			
		print("error message:", e)	
		messagebox.showinfo(title='Critical error', message=e)
	try:
		application.MyTranslator.send_tracking_record()
	except:
		pass	
	print('Initial Done')

if __name__ == '__main__':
	if sys.platform.startswith('win'):
		multiprocessing.freeze_support()

	#AIOTracker.GenerateToolUsageEvent(version)
	#AIOTracker.UpdateTrackingData()

	main()