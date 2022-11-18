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
from time import sleep
#function difination
# Copy to clipboard
from pyperclip import copy, paste
#from tkinter import *
#from tkinter.ttk import *
from tkinter.ttk import Entry, Label, Style
from tkinter.ttk import Checkbutton, OptionMenu, Notebook, Radiobutton, LabelFrame, Button, Scale
from tkinter import Tk, Frame, Toplevel

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

from libs.aiotranslator import ver_num as TranslatorVersion
from libs.aiotranslator import generate_translator

from libs.aioconfigmanager import ConfigLoader

from libs.cloudconfig import CloudConfigLoader

#from libs.grammarcheck import LanguageTool

from libs.version import get_version
from libs.tkinter_extension import AutocompleteCombobox, AutocompleteEntry, CustomText

#from openpyxl import load_workbook, worksheet, Workbook

from google.cloud import logging

tool_display_name = "Translate Helper"
tool_name = 'writer'
REV = 4221
ver_num = get_version(REV) 
version = tool_display_name  + " " +  ver_num

DELAY = 20
DELAY_2 = 15000

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

		self.SOURCE_WIDTH = 70
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
		self.Separator = '====================================================='
		self.separator_2 = '\n'
		
		self.language_id_list = ['', 'ko', 'en', 'cn', 'jp', 'vi']
		self.language_list = ['', 'Hangul', 'English', 'Chinese', 'Japanese', 'Vietnamese']
		self.source_text = ''
		self.main_translation = ''
		self.primary_translation = ''

		self.button_event = '' # Used to distinguish clicked buttons

		# Widget list vars to change color via Translate Setting tab.
		self.text_widgets = []
		self.menu_widgets = []
		self.frame_widgets = []

		self.key_press_count = 0
		self.key_release_count = 0

		self.init_App_Setting()
		
		if self.AppLanguage != 'kr':
			from libs.languagepack import LanguagePackEN as LanguagePack
		else:
			from libs.languagepack import LanguagePackKR as LanguagePack

		self.report_details = None

		self.LanguagePack = LanguagePack
		
		self.init_theme()
		self.create_buttom_panel()
		self.init_ui()
		
		self.init_UI_setting()
		
		#self.LoadTempReport()


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
			'''
			MsgBox = messagebox.askquestion ('Bug Writer', self.LanguagePack.ToolTips['LoadReport'],icon = 'info') 
			if MsgBox == 'yes':
				self.parent.withdraw()
				self.parent.update_idletasks()
				self.LoadTempReport()
				self.parent.deiconify()
			else:
				self.parent.withdraw()
				self.parent.update_idletasks()
				self.parent.deiconify()
			'''
			self.parent.withdraw()
			self.parent.update_idletasks()
			self.LoadTempReport()
			self.parent.deiconify()
			
				
		else:
			closed_box = messagebox.askokcancel('Bug Writer', 'No license selected, please select the key in Translate setting.',icon = 'info')

			if closed_box == True:
				#self.Error('No license selected, please select the key in Translate setting.')
				self.TAB_CONTROL.select(self.TranslateSetting)
				#self.flash_btn(self.Browse_License_Btn)
		
		self.parent.minsize(self.parent.winfo_width(), self.parent.winfo_height())
		x_cordinate = int((self.parent.winfo_screenwidth() / 2) - (self.parent.winfo_width() / 2))
		y_cordinate = int((self.parent.winfo_screenheight() / 2) - (self.parent.winfo_height() / 2))
		self.parent.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

		self.after(DELAY_2, self.auto_save)

	def auto_save(self):
		"""Automatically save input every once in awhile."""
		try:
			self.SaveTempReport()
		except Exception as err:
			print('Error when auto saving: ', err)
		finally:
			self.after(DELAY_2, self.auto_save)
		
	# Menu function
	def Error(self, ErrorText):
		messagebox.showinfo('Translate error...', ErrorText)	

	def OpenWeb(self):
		webbrowser.open_new(r"https://confluence.nexon.com/display/NWMQA/AIO+Translator")

	def About(self):
		messagebox.showinfo("About....", "Creator: Evan@nexonnetworks.com")

	def flash_btn(self, btn_widget):
		
		# Change the color of the button
		btn_widget.focus_set()
		#btn_widget.configure(activebackground = "#6f6Fff")
		self.after(100, lambda: btn_widget.focus_set())

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

		self.Generate_Menu_UI()
		self.Generate_Tab_UI()

		#Shared variable
		try:
			self.Generate_BugWriter_UI(self.BugWriter)
			self.generate_bug_writer_v2_ui(self.bug_writer_v2)
			self.Generate_SimpleTranslator_UI(self.SimpleTranslator)
			self.Generate_TranslateSetting_UI(self.TranslateSetting)
			#self.Generate_Search_UI(self.Searcher)

			#self.Init_Translator_Config
			self.apply_theme_color()
		except Exception as e:
			print(f'An error occurs while initializing UI: {e}')
	def create_buttom_panel(self):
		self.bottom_panel = BottomPanel(self)
		
	def Generate_Tab_UI(self):
		MainPanel = Frame(self, name='mainpanel')
		MainPanel.pack(side=TOP, fill=BOTH, expand=Y)
		self.TAB_CONTROL = Notebook(MainPanel, name='notebook')
		# extend bindings to top level window allowing
		#   CTRL+TAB - cycles thru tabs
		#   SHIFT+CTRL+TAB - previous tab
		#   ALT+K - select tab using mnemonic (K = underlined letter)
		self.TAB_CONTROL.enable_traversal()
		#TAB_CONTROL = Notebook(self.parent)
		
		## TAB 1
		self.BugWriter = Frame(self.TAB_CONTROL)
		self.TAB_CONTROL.add(self.BugWriter, text=self.LanguagePack.Tab['BugWriter'])
		
		#self.CustomWriter = Frame(TAB_CONTROL)
		#TAB_CONTROL.add(self.CustomWriter, text=self.LanguagePack.Tab['CustomBugWriter'])

		## TAB 2
		self.SimpleTranslator = Frame(self.TAB_CONTROL)
		self.TAB_CONTROL.add(self.SimpleTranslator, text=self.LanguagePack.Tab['SimpleTranslator'])

		## TAB 3
		self.bug_writer_v2 = Frame(self.TAB_CONTROL)
		self.TAB_CONTROL.add(self.bug_writer_v2, text='Bug Writer_v2')

		## TAB 4
		self.TranslateSetting = Frame(self.TAB_CONTROL)
		self.TAB_CONTROL.add(self.TranslateSetting, text=self.LanguagePack.Tab['Translator'])

		#Tab4
		#self.Searcher = Frame(TAB_CONTROL)
		#TAB_CONTROL.add(self.Searcher, text=  self.LanguagePack.Tab['DBSeacher'])

		#Tab4
		#self.TM_Browser = ttk.Frame(TAB_CONTROL)
		#TAB_CONTROL.add(self.TM_Browser, text=self.LanguagePack.Tab['Utility'])

		#Tab5
		#self.TMEditor = ttk.Frame(TAB_CONTROL)
		#TAB_CONTROL.add(self.TMEditor, text=self.LanguagePack.Tab['TMEditor'])
		self.TAB_CONTROL.pack(side=TOP, fill=BOTH, expand=Y)

		for frame_widget in self.TAB_CONTROL.winfo_children():
			self.frame_widgets.append(frame_widget)

	def Generate_Menu_UI(self):
		menubar = Menu(self.parent)
		self.menubar = []

		menubar.configure(cursor='hand2')

		# Adding File Menu and commands 
		file = Menu(menubar, tearoff = 0)
		# Adding Load Menu  
		menubar.add_cascade(label =  self.LanguagePack.Menu['File'], menu = file) 
		file.add_command(label =  self.LanguagePack.Menu['LoadLicensePath'], command = self.Btn_Select_License_Path) 
		#file.add_command(label =  self.LanguagePack.Menu['LoadDictionary'], command = self.SelectDictionary) 

		#file.add_command(label =  self.LanguagePack.Menu['LoadTM'], command = self.SelectTM) 
		file.add_separator() 
		#file.add_command(label =  self.LanguagePack.Menu['CreateTM'], command = self.SaveNewTM)
		#file.add_separator() 
		file.add_command(label =  self.LanguagePack.Menu['Exit'], command = self.on_closing) 
		# Adding Help Menu
		hotkey = Menu(menubar, tearoff=0)
		menubar.add_cascade(label =  'Hotkey', menu = hotkey) 
		hotkey.add_command(label = 'Save Report - Ctrl + S', command = self._save_report)
		hotkey.add_command(label = 'Load Report - Ctrl + L', command = self._load_report)
		hotkey.add_command(label = 'Reset Report - Ctrl + Q', command = self.ResetReport)
		hotkey.add_separator()
		hotkey.add_command(label = 'Get Title - Ctrl + T', command = self.GetTitle)
		hotkey.add_command(label = 'Get Report - Ctrl + R', command = self.generate_report)
		#hotkey.add_separator()  
		#hotkey.add_command(label = 'Grammar check - Ctrl + Q') 

		help_ = Menu(menubar, tearoff = 0)
		menubar.add_cascade(label =  self.LanguagePack.Menu['Help'], menu = help_) 
		help_.add_command(label =  self.LanguagePack.Menu['GuideLine'], command = self.OpenWeb) 
		help_.add_separator()
		help_.add_command(label =  self.LanguagePack.Menu['About'], command = self.About) 
		self.parent.config(menu = menubar)
		
		# Adding Help Menu
		language = Menu(menubar, tearoff = 0)
		menubar.add_cascade(label =  self.LanguagePack.Menu['Language'], menu = language) 
		language.add_command(label =  self.LanguagePack.Menu['Hangul'], command = self.SetLanguageKorean) 
		language.add_command(label =  self.LanguagePack.Menu['English'], command = self.SetLanguageEnglish) 
		self.parent.config(menu = menubar)

		# To change theme
		for menu_widget in menubar.winfo_children():
			self.menu_widgets.append(menu_widget)

	def Generate_BugWriter_UI(self, Tab):

		Row=1
		Label(Tab, text= self.LanguagePack.Label['SourceLanguage'], width= self.HALF_BUTTON_SIZE).grid(row = Row, column = 1, padx=5, pady=5, stick=E+W)
		Label(Tab, text= self.LanguagePack.Label['MainLanguage'], width= self.HALF_BUTTON_SIZE).grid(row = Row, column = 2, padx=5, pady=5, stick=E+W)
		Label(Tab, text= self.LanguagePack.Label['SecondaryLanguage'], width= self.HALF_BUTTON_SIZE).grid(row = Row, column = 3, padx=5, pady=5, stick=E+W)
		Label(Tab, textvariable=self.Notice).grid(row=Row, column=4, columnspan=7, padx=5, pady=5, stick=E)

		Row += 1

		self.source_language = StringVar()
		self.source_language_select = OptionMenu(Tab, self.source_language, *self.language_list, command = self.set_writer_language)
		self.source_language_select.config(width=self.HALF_BUTTON_SIZE)
		self.source_language_select.grid(row=Row, column=1, padx=0, pady=5, sticky=W)

		self.target_language = StringVar()
		self.target_language_select = OptionMenu(Tab, self.target_language, *self.language_list, command = self.set_writer_language)
		self.target_language_select.config(width=self.HALF_BUTTON_SIZE)
		self.target_language_select.grid(row=Row, column=2, padx=0, pady=5, sticky=W)
		
		self.secondary_target_language = StringVar()
		secondary_language_list = self.language_list + ['']
		self.secondary_target_language_select = OptionMenu(Tab, self.secondary_target_language, *secondary_language_list, command = self.set_writer_language)
		self.secondary_target_language_select.config(width=self.HALF_BUTTON_SIZE)
		self.secondary_target_language_select.grid(row=Row, column=3, padx=0, pady=5, sticky=W)
		
		#Button(Tab, width = self.HALF_BUTTON_SIZE, text= self.LanguagePack.Button['Save'], command= self._save_project_key).grid(row=Row, column=7, padx=5, pady=5, sticky=E)
		self.GetTitleBtn = Button(Tab, text=self.LanguagePack.Button['GetTitle'], width=10, command=self.GetTitle, state=DISABLED)
		self.GetTitleBtn.grid(row=Row, column=10, padx=5, pady=5, stick=W+E)
		
		Row+=1
		Label(Tab, text=self.LanguagePack.Label['BugTitle']).grid(row=Row, column = 1, padx=5, pady=5, stick=W)

		#AutocompleteCombobox
		self.HeaderOptionA = AutocompleteCombobox(Tab)
		self.HeaderOptionA.Set_Entry_Width(self.HALF_BUTTON_SIZE*2)
		self.HeaderOptionA.set_completion_list(self.header_list)
		self.HeaderOptionA.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)
		
		self.TextTitle = CustomText(Tab, width=90, height=3, undo=True, wrap=WORD)
		self.TextTitle.grid(row=Row, column=4, columnspan=7, rowspan=2, padx=5, pady=5, stick=E)

		Row+=1

		self.HeaderOptionB = AutocompleteCombobox(Tab)
		self.HeaderOptionB.Set_Entry_Width(self.HALF_BUTTON_SIZE*2)
		self.HeaderOptionB.set_completion_list(self.header_list)
		self.HeaderOptionB.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)
		
		Row+=1
		Label(Tab, text=self.LanguagePack.Label['Server']).grid(row=Row, column=1, padx=5, pady=5, stick=W)

		self.TextServer = Text(Tab, width=35, height=1, undo=True)
		self.TextServer.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, stick=W)
	
		Label(Tab, text=self.LanguagePack.Label['ReproduceTime']).grid(row=Row, column=4, padx=5, pady=5, stick=W)

		self.TextReprodTime = Text(Tab,width=20, height=1, undo=True)
		self.TextReprodTime.grid(row=Row, column=5, columnspan=3, padx=5, pady=5, stick=W+E)

		
		Checkbutton(Tab, text=self.LanguagePack.Label['TestInfo'], variable = self.SkipTestInfo, command = self.SaveSetting).grid(row=Row, column=8, padx=5, pady=5, stick=W)
		#self.SkipTestInfo.set(1)

		Button(Tab, text=self.LanguagePack.Button['Reset'], width=10, command= self.ResetTestReport).grid(row=Row, column=10, padx=5, pady=5, stick=W+E)


		Row+=1
		Label(Tab, text=self.LanguagePack.Label['Client']).grid(row=Row, column=1, padx=5, pady=5, stick=W)

		self.TextClient = Text(Tab, width=35, height=1, undo=True)
		self.TextClient.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, stick=W)
		self.TextClient.insert("end", "ver.")

		self.TextAccount = Text(Tab,width=20, height=1, undo=True)
		Label(Tab, text=self.LanguagePack.Label['IDChar']).grid(row=Row, column=4, padx=5, pady=5, stick=W)
		
		self.TextAccount.grid(row=Row, column=5, columnspan=3, padx=5, pady=5, stick=W+E)

		Checkbutton(Tab, text= 'Use Simple Template', variable = self.UseSimpleTemplate, command = self.SaveSetting).grid(row=Row, column=8, padx=5, pady=5, stick=W)
		#self.UseSimpleTemplate.set(1)

		Button(Tab, text=self.LanguagePack.Button['Load'], width=10, command= self._load_report).grid(row=Row, column=9, padx=5, pady=5, stick=W+E)
		Button(Tab, text=self.LanguagePack.Button['Save'], width=10, command= self._save_report).grid(row=Row, column=10, padx=5, pady=5, stick=W+E)

		Row+=1
		Label(Tab, width=10, text=self.LanguagePack.Label['Report']).grid(row=Row, column=1, columnspan=2, padx=5, pady=5, stick=W)
		
		Label(Tab, width=10, text=self.LanguagePack.Label['Search']).grid(row=Row, column=4, padx=5, pady=5, stick=W)

		self.search_entry = AutocompleteEntry([], Tab, listboxLength=6, width=100, matchesFunction=matches)
		self.search_entry.grid(row=Row, column=5, columnspan=6, padx=5, pady=5, sticky=E)

		Row+=1
		self.TextTestReport = CustomText(Tab, width=130, height=8, undo=True, wrap=WORD)
		self.TextTestReport.grid(row=Row, column=1, columnspan=10, rowspan=7, padx=5, pady=5, stick=W+E)
		Row+=7
		
		
		Row+=1
		Label(Tab, width=10, text=self.LanguagePack.Label['Steps']).grid(row=Row, column=1, columnspan=2, padx=0, pady=0, stick=W)


		Label(Tab, width=10, text=self.LanguagePack.Label['Expected']).grid(row=Row, column=6, columnspan=2, padx=0, pady=0, stick=W)
		#Button(Tab, text=self.LanguagePack.Button['Load'], width=10, command= self._load_report).grid(row=Row, column=9, padx=5, pady=5, stick=W+E)
		#self.grammar_check = Button(Tab, text="Grammar Check", width=10, command= self.analyze_grammar)
		#self.grammar_check.grid(row=Row, column=9, padx=5, pady=5, stick=W+E)

		#self.db_correction = Button(Tab, text="DB Falt Alarm", width=10	, command= self.analyze_fault_terminology, state=DISABLED)
		#self.db_correction.grid(row=Row, column=8, padx=5, pady=5, stick=W+E)

		self.ReviewReportBtn = Button(Tab, text="Review Report", width=10, command= self.review_report, state=DISABLED, style=self.Btn_Style)
		self.ReviewReportBtn.grid(row=Row, column=9, padx=5, pady=5, stick=W+E)	

		self.GetReportBtn = Button(Tab, text=self.LanguagePack.Button['GetReport'], width=10, command= self.generate_report, state=DISABLED)
		self.GetReportBtn.grid(row=Row, column=10, padx=5, pady=5, stick=W+E)
		

		Row+=1
		self.TextReproduceSteps = CustomText(Tab, width=50, height=7, undo=True, wrap=WORD)
		self.TextReproduceSteps.grid(row=Row, column=1, columnspan=5, rowspan=7, padx=5, pady=5, stick=W+E)
		self.TextShouldBe = CustomText(Tab, width=50, height=7, undo=True, wrap=WORD) 
		self.TextShouldBe.grid(row=Row, column=6, columnspan=5, padx=5, pady=5, stick=W+E)

		# Tab.bind_all('<Key>', self.check_key_press)
		# Tab.bind_all('<KeyRelease>', self.check_key_release)
		Tab.bind_all('<Control-r>', self.generate_report)
		Tab.bind_all('<Control-t>', self.GetTitle)
		Tab.bind_all('<Control-s>', self._save_report)
		Tab.bind_all('<Control-l>', self._load_report)
		Tab.bind_all('<Control-q>', self.ResetReport)

		# Add all Text in the tab to a list to change theme dynamically
		for child in Tab.winfo_children():
			if isinstance(child, Text) or isinstance(child, CustomText):
				self.text_widgets.append(child)
	
	### BUG WRITER_V2 TAB ###
	def generate_bug_writer_v2_ui(self, Tab):
		"""Bug writer for jiralive subdomain."""
		row_size = 8
		field_width = int(self.SOURCE_WIDTH - 17)

		## ROW 1 - LANGUAGE SELECTION LABEL AND NOTICE
		Row=1
		Label(Tab, textvariable=self.Notice)\
			.grid(row=Row, column=1, columnspan=9, padx=5, pady=5, sticky=E)
		Label(
				Tab,
				text=self.LanguagePack.Label['SourceLanguage'],
				width=self.HALF_BUTTON_SIZE)\
			.grid(row=Row, column=1, padx=5, pady=5, stick=E+W)
		Label(
				Tab,
				text=self.LanguagePack.Label['MainLanguage'],
				width=self.HALF_BUTTON_SIZE)\
			.grid(row=Row, column=2, padx=5, pady=5, stick=E+W)
		Label(
				Tab,
				text=self.LanguagePack.Label['SecondaryLanguage'],
				width=self.HALF_BUTTON_SIZE)\
			.grid(row=Row, column=3, padx=5, pady=5, stick=E+W)
		
		secondary_language_list = self.language_list + ['']

		## ROW 2 - LANGUAGE SELECTION
		Row += 1
		# Source Language
		self.simple_source_language = StringVar()
		self.simple_source_language_select = OptionMenu(
			Tab,
			self.simple_source_language,
			*self.language_list,
			command=self.set_simple_language)
		self.simple_source_language_select.config(width=self.HALF_BUTTON_SIZE)
		self.simple_source_language_select.grid(
			row=Row, column=1, padx=0, pady=5, sticky=W+E)
		self.simple_source_language.set('English')

		# Primary Language
		self.simple_target_language = StringVar()
		self.simple_target_language_select = OptionMenu(
			Tab,
			self.simple_target_language,
			*self.language_list,
			command=self.set_simple_language)
		self.simple_target_language_select.config(
			width=self.HALF_BUTTON_SIZE)
		self.simple_target_language_select.grid(
			row=Row, column=2, padx=0, pady=5, sticky=W+E)
		self.simple_target_language.set('Hangul')

		# Secondary Language
		self.simple_secondary_target_language = StringVar()
		self.simple_secondary_target_language_select = OptionMenu(
			Tab,
			self.simple_secondary_target_language,
			*secondary_language_list,
			command=self.set_simple_language)
		self.simple_secondary_target_language_select.config(
			width=self.HALF_BUTTON_SIZE)
		self.simple_secondary_target_language_select.grid(
			row=Row, column=3, padx=0, pady=5, sticky=W+E)
		self.simple_secondary_target_language.set('Japanese')

		self.btn_translate_all_v2 = Button(
			Tab,
			text="Translate All",
			width=self.BUTTON_SIZE,
			command=lambda: self.single_translate('btn_translate_all_v2'),
			state=DISABLED)
		self.btn_translate_all_v2.grid(
			row=Row, column=7, padx=5, pady=5, sticky=W+E)
		# self.btn_translate_all_v2.configure({'b': 'black'})

		## ROW 3
		Row += 1
		Label(Tab, text='Bug Title:').grid(
			row=Row, column=1, padx=5, pady=5, sticky=W+E)
		
		self.header_option_a_v2 = AutocompleteCombobox(Tab)
		self.header_option_a_v2.Set_Entry_Width(self.BUTTON_SIZE)
		self.header_option_a_v2.set_completion_list(self.header_list)
		self.header_option_a_v2.grid(
			row=Row, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)
		
		self.header_option_b_v2 = AutocompleteCombobox(Tab)
		self.header_option_b_v2.Set_Entry_Width(self.BUTTON_SIZE)
		self.header_option_b_v2.set_completion_list(self.header_list)
		self.header_option_b_v2.grid(
			row=Row+1, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)

		self.text_bug_title_v2 = Text(
			Tab,
			width=field_width,
			height=4,
			undo=True,
		)
		self.text_bug_title_v2.grid(
			row=Row, rowspan=2, column=4, columnspan=4, padx=5, pady=0,
			sticky=W+E)

		self.btn_translate_title_v2 = Button(
			Tab,
			text='Translate Title',
			width=self.BUTTON_SIZE,
			command=lambda: self.single_translate('btn_translate_title_v2'),
			state=DISABLED)
		self.btn_translate_title_v2.grid(
			row=Row, column=8, padx=5, pady=0, sticky=E)

		## ROW 4
		Row += 1
		self.btn_copy_bug_title_v2 = Button(
			Tab,
			text='Copy Bug Title',
			width=self.BUTTON_SIZE,
			command=self.get_title_v2)
		self.btn_copy_bug_title_v2.grid(
			row=Row, column=8, padx=5, pady=5, sticky=E)

		## ROW 5
		Row +=1
		Label(Tab, text=self.LanguagePack.Label['SourceText'])\
			.grid(row=Row, column=2, padx=5, pady=5, sticky=W)
		Label(Tab, text=self.LanguagePack.Label['TargetText'])\
			.grid(row=Row, column=5, padx=5, pady=5, sticky=W)
		
		## ROW 6 ~ 17 - REPRODUCE STEPS FIELD
		Row +=1
		Label(
				Tab,
				text="Reproduce Steps",
				width=self.HALF_BUTTON_SIZE)\
			.grid(row=Row, column=1, padx=5, pady=5, stick=E+W)
		self.text_repro_step_source = Text(
			Tab,
			width=field_width,
			height=row_size,
			undo=True)
		self.text_repro_step_source.grid(
			row=Row, column=2, columnspan=3, rowspan=self.ROW_SIZE,
			padx=5, pady=5, sticky=E+W)
		self.text_repro_step_target = Text(
			Tab,
			width=field_width,
			height=row_size,
			undo=True)
		self.text_repro_step_target.grid(
			row=Row, column=5, columnspan=3, rowspan=self.ROW_SIZE,
			padx=5, pady=5, sticky=E)
		
		# Lambda is used to distinguish the clicked buttons
		self.btn_translate_repro_step = Button(
			Tab,
			text=self.LanguagePack.Button['Translate'],
			width=self.BUTTON_SIZE,
			command=lambda: self.single_translate(
				'btn_translate_repro_step_v2'),
			state=DISABLED)
		self.btn_translate_repro_step.grid(
			row=Row, column=8, padx=5, pady=5, sticky=E)
		
		## ROW 7
		Row +=1
		Button(
				Tab,
				text=self.LanguagePack.Button['Bilingual'],
				width=self.BUTTON_SIZE,
				command=lambda: self.btn_bilingual_copy(
					'btn_bicopy_repro_step_v2')) \
			.grid(row=Row, column=8, padx=5, pady=5, sticky=E)

		## ROW 18 ~ 29 - EXPECTED RESULT FIELD
		Row +=self.ROW_SIZE
		Label(
				Tab,
				text="Expected Results",
				width=self.HALF_BUTTON_SIZE) \
			.grid(row=Row, column=1, padx=5, pady=5, stick=E+W)
		self.text_expected_result_source = Text(
			Tab,
			width=field_width,
			height=row_size,
			undo=True) 
		self.text_expected_result_source.grid(
			row=Row, column=2, columnspan=3, rowspan=self.ROW_SIZE,
			padx=5, pady=5, sticky=E+W)
		self.text_expected_result_target = Text(
			Tab,
			width=field_width,
			height=row_size,
			undo=True)
		self.text_expected_result_target.grid(
			row=Row, column=5, columnspan=3, rowspan=self.ROW_SIZE,
			padx=5, pady=5, sticky=E)
		
		# Lambda is used to distinguish the clicked buttons
		self.btn_translate_expected_result = Button(
			Tab,
			text=self.LanguagePack.Button['Translate'],
			width=self.BUTTON_SIZE,
			command=lambda: \
				self.single_translate('btn_translate_expected_result_v2'),
			state=DISABLED)
		self.btn_translate_expected_result.grid(
			row=Row, column=8, padx=5, pady=5, sticky=E)
		
		## ROW 19
		Row +=1
		Button(
				Tab,
				text=self.LanguagePack.Button['Bilingual'],
				width=self.BUTTON_SIZE,
				command=lambda: self.btn_bilingual_copy(
					'btn_bicopy_expected_result_v2')) \
			.grid(row=Row, column=8, padx=5, pady=5, sticky=E)

		## ROW 30 ~ 41 - SYMPTOMs AND DESCRIPTION
		Row +=self.ROW_SIZE
		Label(
				Tab,
				text="Description",
				width=self.HALF_BUTTON_SIZE)\
			.grid(row=Row, column=1, padx=5, pady=5, stick=E+W)
		self.text_description_source = Text(
			Tab,
			width=field_width,
			height=row_size,
			undo=True) 
		self.text_description_source.grid(
			row=Row, column=2, columnspan=3, rowspan=self.ROW_SIZE,
			padx=5, pady=5, sticky=E+W)
		self.text_description_target = Text(
			Tab,
			width=field_width,
			height=row_size,
			undo=True)
		self.text_description_target.grid(
			row=Row, column=5, columnspan=3, rowspan=self.ROW_SIZE,
			padx=5, pady=5, sticky=E)
		
		# Lambda is used to distinguish the clicked buttons
		self.btn_translate_description_v2 = Button(
			Tab,
			text=self.LanguagePack.Button['Translate'],
			width=self.BUTTON_SIZE,
			command=lambda: self.single_translate(
				'btn_translate_description_v2'),
			state=DISABLED)
		self.btn_translate_description_v2.grid(
			row=Row, column=8, padx=5, pady=5, sticky=E)
		
		## ROW 31
		Row +=1
		Button(
				Tab,
				text=self.LanguagePack.Button['Bilingual'],
				width=self.BUTTON_SIZE,
				command=lambda: self.btn_bilingual_copy(
					'btn_bicopy_description_v2')) \
			.grid(row=Row, column=8, padx=5, pady=5, sticky=E)

		# Add all Text in the tab to a list to change color dynamically
		for child in Tab.winfo_children():
			if isinstance(child, Text):
				self.text_widgets.append(child)

	### SIMPLE TRANSLATOR TAB
	def Generate_SimpleTranslator_UI(self, Tab):

		
		Row=1
		Label(Tab, textvariable=self.Notice).grid(row=Row, column=1, columnspan=10, padx=5, pady=5, sticky=E)

		Row +=1
		Label(Tab, text=self.LanguagePack.Label['SourceText']).grid(row=Row, column=1, columnspan = 5, padx=5, pady=0)
		Label(Tab, text=self.LanguagePack.Label['TargetText']).grid(row=Row, column=6, columnspan = 5, padx=0, pady=0)
		#New Row

		Row +=1
		self.SourceText = Text(Tab, width = self.SOURCE_WIDTH, height=self.ROW_SIZE, undo=True) 
		self.SourceText.grid(row=Row, column=1, columnspan=5, rowspan=self.ROW_SIZE, padx=5, pady=5, sticky=E+W)
		self.SourceText.bind("<Double-Tab>", self.BindSwap)

		self.TargetText = Text(Tab, width = self.SOURCE_WIDTH, height=self.ROW_SIZE, undo=True) #
		self.TargetText.grid(row = Row, column=6, columnspan=5, rowspan=self.ROW_SIZE, padx=5, pady=5, sticky=E)
		
		Row +=self.ROW_SIZE

		Label(Tab, text= self.LanguagePack.Label['SourceLanguage'], width= self.HALF_BUTTON_SIZE).grid(row = Row, column = 1, padx=5, pady=5, stick=E+W)
		
		self.simple_source_language = StringVar()
		self.simple_source_language_select = OptionMenu(Tab, self.simple_source_language, *self.language_list, command = self.set_simple_language)
		self.simple_source_language_select.config(width=self.HALF_BUTTON_SIZE)
		self.simple_source_language_select.grid(row=Row, column=2, padx=0, pady=5, sticky=W)
		self.simple_source_language.set('Hangul')



		Button(Tab, text=self.LanguagePack.Button['Swap'], width = 20, command= self.Swap).grid(row=Row, column=8, padx=5, pady=5)	
		
		Button(Tab, text=self.LanguagePack.Button['Copy'], width = self.BUTTON_SIZE, command= self.BtnCopy).grid(row = Row, column=9, padx=5, pady=5, sticky=E)

		self.TranslateBtn = Button(Tab, text=self.LanguagePack.Button['Translate'], width = self.BUTTON_SIZE, command= self.single_translate, state=DISABLED)
		self.TranslateBtn.grid(row=Row, column=10, padx=0, pady=5, sticky=E)		

		Row +=1

		Label(Tab, text= self.LanguagePack.Label['MainLanguage'], width= self.HALF_BUTTON_SIZE).grid(row = Row, column = 1, padx=5, pady=5, stick=E+W)
		
		self.simple_target_language = StringVar()
		self.simple_target_language_select = OptionMenu(Tab, self.simple_target_language, *self.language_list, command = self.set_simple_language)
		self.simple_target_language_select.config(width=self.HALF_BUTTON_SIZE)
		self.simple_target_language_select.grid(row=Row, column=2, padx=0, pady=5, sticky=W)
		self.simple_target_language.set('English')		
		
		Label(Tab, text= self.LanguagePack.Label['SecondaryLanguage'], width= self.HALF_BUTTON_SIZE).grid(row = Row, column = 3, padx=5, pady=5, stick=E+W)
		
		secondary_language_list = self.language_list + ['']

		self.simple_secondary_target_language = StringVar()
		self.simple_secondary_target_language_select = OptionMenu(Tab, self.simple_secondary_target_language, *secondary_language_list, command = self.set_simple_language)
		self.simple_secondary_target_language_select.config(width=self.HALF_BUTTON_SIZE)
		self.simple_secondary_target_language_select.grid(row=Row, column=4, padx=0, pady=5, sticky=W)
		self.simple_secondary_target_language.set('Japanese')
		
		Button(Tab, text= 'Trilingual Copy', width = self.BUTTON_SIZE, command= self.btn_trilingual).grid(row = Row, column=8, padx=5, pady=5)
		
		Button(Tab, text=self.LanguagePack.Button['Bilingual'], width = self.BUTTON_SIZE, command= self.btn_bilingual_copy).grid(row = Row, column=9, padx=5, pady=5, sticky=E)
		self.dual_translate_btn = Button(Tab, text= 'Dual Translate', width = self.BUTTON_SIZE, command= self.dual_translate, state=DISABLED)
		self.dual_translate_btn.grid(row = Row, column=10, padx=0, pady=5, sticky=E)
		#self.Translate_bilingual_Btn = Button(Tab, text=self.LanguagePack.Button['TranslateAndBilingual'], width = self.BUTTON_SIZE, command= self.BtnTranslateAndBilingual)
		#self.Translate_bilingual_Btn.grid(row = Row, column=10, padx=5, pady=5, sticky=E)

		# Add all Text in the tab to a list to change color dynamically
		for child in Tab.winfo_children():
			if isinstance(child, Text):
				self.text_widgets.append(child)

	def Generate_Search_UI(self, Tab):
		Row = 1

		self.search_entry = AutocompleteEntry([], Tab, listboxLength=6, width=32, matchesFunction=matches)
		self.search_entry.grid(row=0, column=0, columnspan = 10, padx=5, pady=5, sticky= W)

	def Generate_TranslateSetting_UI(self, Tab):
		"""Create Translate Setting tab."""
		Row = 1

		Label(Tab, textvariable=self.Notice).grid(row=Row, column=1, columnspan = 10, padx=5, pady=5, sticky= E+W)
		Row += 1

		Label(
			Tab, text= self.LanguagePack.Label['LicensePath']).grid(row=Row, column=1, padx=5, pady=5, sticky=E)
		self.TextLicensePath = Entry(Tab,width = 150, state="readonly", textvariable=self.LicensePath)
		self.TextLicensePath.grid(row=Row, column=3, columnspan=7, padx=5, pady=5, sticky=W+E)
		self.Browse_License_Btn = Button(Tab, width = self.HALF_BUTTON_SIZE, text=  self.LanguagePack.Button['Browse'], command= self.Btn_Select_License_Path)
		self.Browse_License_Btn.grid(row=Row, column=10, padx=5, pady=5, sticky=E)

		Row += 1
		Label(Tab, text= self.LanguagePack.Label['Transparent']) \
			.grid(row=Row, rowspan = 2, column=1, padx=5, pady=5, sticky=W)
		self.TransparentPercent = Scale(
			Tab,
			length=600,
			from_=20,
			to=100,
			variable=self.Transparent,
			command=self.SaveAppTransparency,
			orient=HORIZONTAL,)
		self.TransparentPercent.grid(
			row=Row, rowspan=2, column=3, columnspan=7, padx=5, pady=5,
			sticky=E+W)
		Button(
				Tab,
				width=self.HALF_BUTTON_SIZE,
				text=self.LanguagePack.Button['Reset'],
				command=self.rebuild_UI) \
			.grid(row=Row, column=10, padx=5, pady=5, rowspan=2, sticky=E)

		Row += 2
		Label(Tab, text='Theme name:') \
			.grid(row=Row, rowspan=2, column=1, padx=5, pady=5, sticky=E)
		self.btn_remove_theme = Button(
			Tab,
			width=self.HALF_BUTTON_SIZE,
			text="Remove Theme",
			command=self.remove_theme)
		self.btn_remove_theme.grid(row=Row, column=10)
		self.strvar_theme_name = StringVar()
		col = 3 # to add more buttons horizontally
		for theme_name in self.theme_names:
			self.radiobutton_theme_name = Radiobutton(
				Tab,
				text=theme_name,
				value=theme_name,
				variable=self.strvar_theme_name,
				command=self.select_theme_name)
			self.radiobutton_theme_name.config(width=self.HALF_BUTTON_SIZE)
			self.radiobutton_theme_name.grid(
				row=Row, column=col, padx=0, pady=5, sticky=W)
			# Go to new line when reaching column 8
			if col < 8:
				col += 1
			else:
				col = 3
				Row += 1
		
		# Display selected theme
		config_theme_name = self.Configuration['Bug_Writer']['theme name']
		if config_theme_name in self.theme_names:
			self.strvar_theme_name.set(config_theme_name)

		# Disable [Remove Theme] button if no theme is selected.
		if self.strvar_theme_name.get() not in self.theme_names:
			self.btn_remove_theme.config(state=DISABLED)

	def Btn_Select_License_Path(self):
		filename = filedialog.askopenfilename(title =  self.LanguagePack.ToolTips['SelectDB'],filetypes = (("JSON files","*.json" ), ), )	
		if filename != "":
			LicensePath = self.CorrectPath(filename)
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'Translator', 'license_file', LicensePath, True)
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = LicensePath
			self.LicensePath.set(LicensePath)
			self.rebuild_UI()
		else:
			self.Notice.set("No file is selected")

	def select_theme_name(self):
		"""Save the theme name value to Configuration and change
		the theme based on the selection in the UI.
		
		Args:
			config_theme_name -- str
				Theme name retrieved from config. (Default: '')
		"""
		try:
			style = Style(self.parent) # self.parent is root
			theme_name = self.strvar_theme_name.get()
			
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Bug_Writer',
				'theme name',
				theme_name)
			self.change_theme_color(theme_name)
			style.theme_use(theme_name)
			self.apply_theme_color()
			self.btn_remove_theme.configure(state=NORMAL)
		except Exception as err:
			messagebox.showerror(
				title='Error',
				message=f'Error occurs when selecting theme: {err}')
	
	def change_theme_color(self, theme_name: str):
		"""Change widget color.
		
		Args:
			theme_name -- str
				Theme that is available on the computer. Retrieved
				from config or selection in Translate Setting tab.
		"""
		# if theme_name == 'awdark':
		# 	self.widget_color = {
		# 		'parent_bg': '#191c1d',
		# 		'frame_bg': '#191c1d',
		# 		'menu_bg': '#474D4E',
		# 		'menu_fg': 'white',
		# 		'text_bg': '#191c1d',
		# 		'text_fg': 'white',
		# 		'text_insertbackground': 'white'
		# 	}
		if theme_name == 'awdark':
			self.widget_color = {
				'parent_bg': '#33393b',
				'frame_bg': '#33393b',
				'menu_bg': '#474D4E',
				'menu_fg': '#ffffff',
				'text_bg': '#191c1d',
				'text_fg': '#ffffff',
				'text_insertbackground': '#ffffff'
			}
		elif theme_name == 'awlight':
			self.widget_color = {
				'parent_bg': '#e8e8e7',
				'frame_bg': '#e8e8e7',
				'menu_bg': '#e8e8e7',
				'menu_fg': '#000000',
				'text_bg': '#ffffff',
				'text_fg': '#000000',
				'text_insertbackground': '#000000'
			}
		elif theme_name == 'clam':
			self.widget_color = {
				'parent_bg': '#dcdad5',
				'frame_bg': '#dcdad5',
				'menu_bg': '#dcdad5',
				'menu_fg': '#000000',
				'text_bg': '#ffffff',
				'text_fg': '#000000',
				'text_insertbackground': '#000000'
			}
		else:
			self.widget_color = {
				'parent_bg': '#ffffff',
				'frame_bg': 'SystemButtonFace',
				'menu_bg': 'SystemButtonFace',
				'menu_fg': '#000000', # font color
				'text_bg': '#ffffff',
				'text_fg': '#000000', # font color
				'text_insertbackground': '#000000' # text cursor
			}

	def apply_theme_color(self):
		"""Apply color to widgets."""
		self.parent['bg'] = self.widget_color['parent_bg']
		for frame_widget in self.frame_widgets:
			frame_widget['bg'] = self.widget_color['frame_bg']
		for menu_widget in self.menu_widgets:
			menu_widget['bg'] = self.widget_color['menu_bg']
			menu_widget['fg'] = self.widget_color['menu_fg']
		for text_widget in self.text_widgets:
			text_widget['bg'] = self.widget_color['text_bg']
			text_widget['fg'] = self.widget_color['text_fg']
			text_widget['insertbackground'] = \
				self.widget_color['text_insertbackground']

	def remove_theme(self):
		"""Remove the theme saved in config then restart the app."""
		self.AppConfig.Save_Config(
			self.AppConfig.Writer_Config_Path,
			'Bug_Writer',
			'theme name',
			'')
		
		messagebox.showinfo(
			title='Info',
			message='App will restart to apply the change.')
		self.parent.destroy()
		main()

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

		self.bucket_id = self.Configuration['Translator']['bucket_id']
		self.db_list_uri = self.Configuration['Translator']['db_list_uri']
		self.project_bucket_id = self.Configuration['Translator']['project_bucket_id']

		self.glossary_id = self.Configuration['Translator']['glossary_id']
		
		try:
			cloud_config = CloudConfigLoader()
			cloud_configuration = cloud_config.Config
			self.banning_status = cloud_configuration['banned']
			self.latest_version = cloud_configuration['latest_version']
		except Exception as e:
			print("Error while loading cloud configuration:", e)
			self.banning_status = False
			self.latest_version = 1000
			
		
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
			self.theme_names = ['clam']
			config_theme_name = self.Configuration['Bug_Writer']['theme name']
			style = Style(self.parent) # self.parent is root

			supported_themes = ['awdark', 'awlight']
			# theme_dir = self.AppConfig.theme_loading_path
			theme_dir = os.path.join(os.getcwd() + r'\\theme')
			theme_files = os.listdir(theme_dir)
			# Add to theme selection in Translate Setting tab
			for theme_file in theme_files:
				file_name, file_ext = os.path.splitext(theme_file)
				if file_ext == '.tcl':
					if file_name in supported_themes:
						# Import tcl files
						self.parent.tk.call(
							"source", f'{theme_dir}\\{theme_file}')
						self.theme_names.append(file_name)
				else:
					continue
			# System default color is removed if adding below!!!!
			# style.map(
			# 	'.', #'.' means all ttk widgets
			# 	foreground=fixed_map(style, 'foreground'),
			# 	background=fixed_map(style, 'background'))

			if config_theme_name not in self.theme_names:
				raise Exception('Cannot use the theme saved in the config'
					' because it is not supported or required files have'
					' been removed.')

			# # Add all available theme
			# for theme_name in style.theme_names():
			# 	self.theme_names.append(theme_name)
			self.change_theme_color(config_theme_name)
			style.theme_use(config_theme_name)
		except Exception as err:
			print('Error while initializing theme:\n'
				f'- {err}\n'
				'The system default theme will be used instead.')



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
	
	def SaveAppTransparency(self, transparency):
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'Transparent', transparency)
		self.parent.attributes('-alpha', self.Transparent.get()/100.0)

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
			glossary_list = [""] + self.MyTranslator.glossary_list

			self.bottom_panel.project_id_select.set_completion_list(glossary_list)
			#print('saved gloss:', self.glossary_id)
			#print('list gloss', self.MyTranslator.glossary_list)
			if self.glossary_id in self.MyTranslator.glossary_list:
				self.bottom_panel.project_id_select.set(self.glossary_id)
			else:
				self.bottom_panel.project_id_select.set("")

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
		"""Get the source text from in Simple Translator tab to
		self.source_text.
		"""
		self.source_text = self.SourceText.get("1.0", END)
		if self.source_text.endswith('\n'):
			self.source_text = self.source_text[:-1]

	def get_bug_title_source_text_v2(self):
		"""Get the source text from Reproduce Steps text field in
		Bug Writer_v2 tab to self.source_text as str.
		"""
		self.source_text = self.text_bug_title_v2.get("1.0", END)
		if self.source_text.endswith('\n'):
			self.source_text = self.source_text[:-1]

	def get_repro_step_source_text_v2(self):
		"""Get the source text from Reproduce Steps text field in
		Bug Writer_v2 tab to self.source_text as str.
		"""
		self.source_text = self.text_repro_step_source.get("1.0", END)
		if self.source_text.endswith('\n'):
			self.source_text = self.source_text[:-1]
	
	def get_expected_result_source_text_v2(self):
		"""Get the source text from Expected Results text field in
		Bug Writer_v2 tab to self.source_text as str.
		"""
		self.source_text = self.text_expected_result_source.get("1.0", END)
		if self.source_text.endswith('\n'):
			self.source_text = self.source_text[:-1]

	def get_description_source_text_v2(self):
		"""Get the source text from Description text field in
		Bug Writer_v2 tab to self.source_text as str.
		"""
		self.source_text = self.text_description_source.get("1.0", END)
		if self.source_text.endswith('\n'):
			self.source_text = self.source_text[:-1]
	
	def get_all_source_text_v2(self):
		"""Get the source text from description text fields in
		Bug Writer_v2 tab to self.source_text as dict.
		"""
		self.source_text = {
			'bug_title': self.text_bug_title_v2.get("1.0", END),
			'repro_step': self.text_repro_step_source.get("1.0", END),
			'expected_result': self.text_expected_result_source.get("1.0", END),
			'description': self.text_description_source.get("1.0", END)
		}

	#Execute function
	def single_translate(self, event: str=''):
		"""Translate from source text to target text in
		Simple Translator tab and Bug Writer_v2 tab.
		
		Args:
			event -- str
				Name of the clicked button.
		"""
		self.button_event = event

		if self.LicensePath.get() == "":
			self.Error('Please select License file and relaunch the app!')
			return
			
		self.Notice.set(self.LanguagePack.ToolTips['Translating'])

		target_language = self.language_id_list[
			self.language_list.index(self.simple_target_language.get())]
		source_language = self.language_id_list[
			self.language_list.index(self.simple_source_language.get())]

		if target_language == source_language:
			messagebox.showinfo(
					'Error',
					'Source and Primary Target language is the same.')	
			return
		if target_language != self.MyTranslator.to_language \
				or source_language != self.MyTranslator.from_language:
			self.MyTranslator.set_language_pair(
				source_language=source_language,
				target_language=target_language)
			print(f'Update language pair from: {source_language}'
				f'to {target_language}')		

		if event == 'btn_translate_all_v2':
			self.get_all_source_text_v2()
		elif event == 'btn_translate_title_v2':
			self.get_bug_title_source_text_v2()
		elif event == 'btn_translate_repro_step_v2':
			self.get_repro_step_source_text_v2()
		elif event == 'btn_translate_expected_result_v2':
			self.get_expected_result_source_text_v2()
		elif event == 'btn_translate_description_v2':
			self.get_description_source_text_v2()
		else:
			self.get_source_text()
		#print('Source:', self.source_text)
		# Create a temporary variable to separate paragraphs i.e.
		# paragraph translation.
		if isinstance(self.source_text, str):
			try:
				source_text = []
				_temp_source = self.source_text.split('\n')
				for text in _temp_source:
					if text != "":
						# A list containing paragraphs
						source_text.append(text)
			except:
				pass
		# For [Translate All] button
		# At the end, source_text structure is a dict like this
		# {a:['p1', 'p2', ...], b:[], c:[]}
		elif isinstance(self.source_text, dict):
			source_text = {}
			for field in self.source_text:
				source_text[field] = []
				self.source_text[field] = self.source_text[field].split('\n')
				for paragraph in self.source_text[field]:
					source_text[field].append(paragraph)

		self.p3 = Process(
				target=SimpleTranslate,
				args=(self.return_text, self.MyTranslator, source_text,))
		self.p3.start()
		self.after(DELAY, self.GetSimpleTranslateStatus)

	def GetSimpleTranslateStatus(self):
		"""Insert the translated text to the target text in
		Simple Translator and Bug Writer_v2 tab.
		"""
		if (self.p3.is_alive()):
			self.after(DELAY, self.GetSimpleTranslateStatus)
		else:
			try:
				if self.button_event == 'btn_translate_all_v2':
					bug_title_v2 = self.text_bug_title_v2.get("1.0", END)
					self.text_bug_title_v2.delete("1.0", END)
					self.text_repro_step_target.delete("1.0", END)
					self.text_expected_result_target.delete("1.0", END)
					self.text_description_target.delete("1.0", END)
				elif self.button_event == 'btn_translate_title_v2':
					bug_title_v2 = self.text_bug_title_v2.get("1.0", END)
					self.text_bug_title_v2.delete("1.0", END)
				elif self.button_event == 'btn_translate_repro_step_v2':
					self.text_repro_step_target.delete("1.0", END)
				elif self.button_event == 'btn_translate_expected_result_v2':
					self.text_expected_result_target.delete("1.0", END)
				elif self.button_event == 'btn_translate_description_v2':
					self.text_description_target.delete("1.0", END)
				else:
					self.TargetText.delete("1.0", END)
				
				Translated = self.return_text.get()
				## SINGLE FIELD TRANSLATION
				if isinstance(Translated, list):
					if len(Translated) > 0:
						_index = 0
						_translation = []
						try:
							_temp_source = self.source_text.split('\n')
							for text in _temp_source:
								if text != "":
									_translation.append(Translated[_index])
									_index += 1
								else:
									_translation.append(text)
						except:
							pass
						self.main_translation = "\n".join(_translation)
						self.main_translation = self.main_translation.replace(
							'\r\n', '\n')
						if self.button_event == 'btn_translate_title_v2':
							bug_title_v2 = f'{self.main_translation}'\
								+ f' | {bug_title_v2}'
							self.text_bug_title_v2.insert("1.0", bug_title_v2)
						elif self.button_event == 'btn_translate_repro_step_v2':
							self.text_repro_step_target.insert(
								"end", self.main_translation)
						elif self.button_event == 'btn_translate_expected_result_v2':
							self.text_expected_result_target.insert(
								"end", self.main_translation)
						elif self.button_event == 'btn_translate_description_v2':
							self.text_description_target.insert(
								"end", self.main_translation)
						else:
							self.TargetText.insert(
								"end", self.main_translation)
						self.Notice.set(self.LanguagePack.ToolTips['Translated'])
					else:
						self.Notice.set('There is no text to translate.')
				## MULTIPLE FIELD TRANSLATION
				elif isinstance(Translated, dict):
					translation = {}
					# self.source_text structure becomes {a:[], b:[]}
					# because it has already been processed in the elif
					# statement in single_translate() function.
					for field in Translated:
						_translation = []
						for paragraph in Translated[field]:
							_translation.append(paragraph)
						translation[field] = '\n'.join(_translation)
						translation[field] = translation[field].replace(
							'\r\n', '\n').rstrip('\n')
						
					if self.button_event == 'btn_translate_all_v2':
						bug_title_v2 = f"{translation['bug_title']}"\
							f' | {bug_title_v2}'
						bug_title_v2 = bug_title_v2.rstrip('\n')
						self.text_bug_title_v2.insert("1.0", bug_title_v2)
						self.text_repro_step_target.insert(
							"end", translation['repro_step'])
						self.text_expected_result_target.insert(
							"end", translation['expected_result'])
						self.text_description_target.insert(
							"end", translation['description'])
					
					
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
				# Memory leak prevention
				self.source_text = ''
				self.button_event = ''

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

	def btn_bilingual_copy(self, event: str=''):
		"""Copy the text in Source Text and Target Text to the
		clipboard when clicked.
		
		Used in Bug Writer_v2 and Simple Translator tab

		Args:
			event -- str
				Event to recognize which button is clicked.
		"""
		if event == 'btn_bicopy_repro_step_v2':
			bilingual = self.text_repro_step_target.get("1.0", END)
			bilingual += self.separator_2
			bilingual += self.text_repro_step_source.get("1.0", END)
			bilingual = bilingual.rstrip('\n')
		elif event == 'btn_bicopy_expected_result_v2':
			bilingual = self.text_expected_result_target.get("1.0", END)
			bilingual += self.separator_2
			bilingual += self.text_expected_result_source.get("1.0", END)
			bilingual = bilingual.rstrip('\n')
		elif event == 'btn_bicopy_description_v2':
			bilingual = self.text_description_target.get("1.0", END)
			bilingual += self.separator_2
			bilingual += self.text_description_source.get("1.0", END)
			bilingual = bilingual.rstrip('\n')
		else:
			self.get_source_text()
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
		self.SimpleTranslator = Process(
				target=SimpleTranslate,
				args=(self.return_text, self.MyTranslator, SourceText,))
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
		self.bottom_panel.RenewTranslatorMain.configure(state=DISABLED)
		
		self.secondary_target_language_select.configure(state=DISABLED)
		self.target_language_select.configure(state=DISABLED)
		self.source_language_select.configure(state=DISABLED)

		self.simple_secondary_target_language_select.configure(state=DISABLED)
		self.simple_target_language_select.configure(state=DISABLED)
		self.simple_source_language_select.configure(state=DISABLED)
		
		self.bottom_panel.project_id_select.configure(state=DISABLED)

		#self.Translate_bilingual_Btn.configure(state=DISABLED)
		self.TranslateBtn.configure(state=DISABLED)
		self.btn_translate_repro_step.configure(state=DISABLED)
		self.btn_translate_expected_result.configure(state=DISABLED)
		self.btn_translate_description_v2.configure(state=DISABLED)
		self.btn_translate_all_v2.configure(state=DISABLED)
		self.btn_translate_title_v2.configure(state=DISABLED)

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
		self.bottom_panel.RenewTranslatorMain.configure(state=NORMAL)

		self.secondary_target_language_select.configure(state=NORMAL)
		self.target_language_select.configure(state=NORMAL)
		self.source_language_select.configure(state=NORMAL)

		self.simple_secondary_target_language_select.configure(state=NORMAL)
		self.simple_target_language_select.configure(state=NORMAL)
		self.simple_source_language_select.configure(state=NORMAL)

		self.bottom_panel.project_id_select.configure(state=NORMAL)

		#self.Translate_bilingual_Btn.configure(state=NORMAL)
		self.TranslateBtn.configure(state=NORMAL)
		self.btn_translate_repro_step.configure(state=NORMAL)
		self.btn_translate_expected_result.configure(state=NORMAL)
		self.btn_translate_description_v2.configure(state=NORMAL)
		self.btn_translate_all_v2.configure(state=NORMAL)
		self.btn_translate_title_v2.configure(state=NORMAL)

		if self.strvar_theme_name in self.theme_names:
			self.btn_remove_theme.configure(state=NORMAL)

		#self.db_correction.configure(state=NORMAL)

	def RenewMyTranslator(self):
		
		self.disable_btn()

		del self.MyTranslator
		self.MyTranslator = None

		self.HeaderOptionA.set_completion_list([])
		self.HeaderOptionB.set_completion_list([])
		self.header_option_a_v2.set_completion_list([])
		self.header_option_b_v2.set_completion_list([])
		
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
		self.header_option_a_v2.set_completion_list(self.header_list)
		self.header_option_b_v2.set_completion_list(self.header_list)


	def ResetReport(self,event=None):
		self.ResetTestReport()

	def analyze_terminology(self):
		for term in self.MyTranslator.dictionary:
			if term not in [' ']:
				self.TextTestReport.highlight_fault_pattern(term, 'blue')
				self.TextTitle.highlight_fault_pattern(term, 'blue')
				self.TextReproduceSteps.highlight_fault_pattern(term, 'blue')
				self.TextShouldBe.highlight_fault_pattern(term, 'blue')

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
		target_language = self.language_id_list[self.language_list.index(
			self.target_language.get())]
		source_language = self.language_id_list[self.language_list.index(
			self.source_language.get())]
		if target_language != self.MyTranslator.to_language\
				or source_language != self.MyTranslator.from_language:
			self.MyTranslator.set_language_pair(
				source_language=source_language,
				target_language=target_language)
			print('Update language pair from: ', source_language,\
				' to ',  target_language)
		self.Notice.set(self.LanguagePack.ToolTips['GenerateBugTitle'])
		self.strSourceTitle = self.TextTitle.get("1.0", END).replace('\n', '')
		self.strSourceTitle = self.TextTitle.get("1.0", END).replace('\r\n', '')
		self.Title_Translate = Process(
			target=SimpleTranslate,
			args=(self.return_text, self.MyTranslator, self.strSourceTitle,))
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
					HeaderA_Translated = self.MyTranslator.translate_header(
						HeaderA)
				else:
					HeaderA_Translated = False
					
				HeaderB = self.HeaderOptionB.get()
				if HeaderB != "":
					HeaderB_Translated = self.MyTranslator.translate_header(
						HeaderB)
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

				Title = TargetHeader + " "  +  self.TargetTitle \
					+ " | " + SourceHeader  + " " +  self.strSourceTitle
				
				copy(str(Title))
				self.Notice.set(
					self.LanguagePack.ToolTips['GeneratedBugTitle'])
				self.Title_Translate.join()
			except queue.Empty:
				self.Notice.set(self.LanguagePack.ToolTips[
					'GenerateBugTitleFail'])

			self.enable_btn()	
		return
	
	def get_title_v2(self):
		"""Copy the text in Bug Title field in Bug Writer_v2 tab to
		the clipboard.
		"""
		header_option_a_v2 = self.header_option_a_v2.get()
		header_option_b_v2 = self.header_option_b_v2.get()
		if header_option_b_v2 == '':
			copy(f'[{header_option_a_v2}] '\
				+ self.text_bug_title_v2.get("1.0", END).strip())
		elif header_option_a_v2 == '':
			copy(f'[{header_option_b_v2}] '\
				+ self.text_bug_title_v2.get("1.0", END).strip())
		else:
			copy(f'[{header_option_a_v2}][{header_option_b_v2}] '\
				+ self.text_bug_title_v2.get("1.0", END).strip())

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
		TextTitle = self.TextTitle.get("1.0", END)			
		TextServer = self.TextServer.get("1.0", END)
		TextClient = self.TextClient.get("1.0", END)
		TextReprodTime = self.TextReprodTime.get("1.0", END)
		TextAccount = self.TextAccount.get("1.0", END)
		TextTestReport = self.TextTestReport.get("1.0", END)
		TextReproduceSteps = self.TextReproduceSteps.get("1.0", END)
		TextShouldBe = self.TextShouldBe.get("1.0", END)
		HeaderA = self.HeaderOptionA.get()
		HeaderB = self.HeaderOptionB.get()
		try:
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'TextTitle',
				TextTitle, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'TextServer',
				TextServer, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'TextClient',
				TextClient, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'TextReprodTime',
				TextReprodTime, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'TextAccount',
				TextAccount, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'TextTestReport',
				TextTestReport, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'TextReproduceSteps',
				TextReproduceSteps, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'TextShouldBe',
				TextShouldBe, True)

			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'HeaderA',
				HeaderA)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'BugDetails',
				'HeaderB',
				HeaderB)
		except Exception as e:
			print('Cannot save the report:', e)
			pass

	def check_key_press(self, event=None):
		self.key_press_count += 1
		print(self.key_press_count)

	def check_key_release(self, event=None):
		
		print(f'before sleep: {self.key_press_count}')
		
		self.key_release_count += 1
		print(f'after sleep: {self.key_press_count}')
		if self.key_press_count == self.key_release_count:
			self.SaveTempReport()
		
	
	def SaveTempReport(self, event=None):
		"""Save the text input of all fields every time a key is pressed
		to the config for the next session.
		"""
		# print('Save temp report')
		TextTitle = self.TextTitle.get("1.0", END)			
		TextServer = self.TextServer.get("1.0", END)
		TextClient = self.TextClient.get("1.0", END)
		TextReprodTime = self.TextReprodTime.get("1.0", END)
		TextAccount = self.TextAccount.get("1.0", END)
		TextTestReport = self.TextTestReport.get("1.0", END)
		TextReproduceSteps = self.TextReproduceSteps.get("1.0", END)
		TextShouldBe = self.TextShouldBe.get("1.0", END)
		HeaderA = self.HeaderOptionA.get()
		HeaderB = self.HeaderOptionB.get()

		SourceText = self.SourceText.get("1.0", END)

		try:
			## BUG WRITER TAB
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'TextTitle',
				TextTitle, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'TextServer',
				TextServer, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'TextClient',
				TextClient, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'TextReprodTime',
				TextReprodTime, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'TextAccount',
				TextAccount, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'TextTestReport',
				TextTestReport, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'TextReproduceSteps',
				TextReproduceSteps, True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'TextShouldBe',
				TextShouldBe, True)

			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'HeaderA',
				HeaderA)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'HeaderB',
				HeaderB)

			## SIMPLE TRANSLATOR TAB
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails',
				'SimpleTranslator',
				SourceText, True)
			
			## BUG WRITER_V2 TAB
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails_v2',
				'Header A',
				self.header_option_a_v2.get())
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails_v2',
				'Header B',
				self.header_option_b_v2.get())
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails_v2',
				'Bug Title',
				self.text_bug_title_v2.get("1.0", END), True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails_v2',
				'Reproduce Steps',
				self.text_repro_step_source.get("1.0", END), True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails_v2',
				'Expected Results',
				self.text_expected_result_source.get("1.0", END), True)
			self.AppConfig.Save_Config(
				self.AppConfig.Writer_Config_Path,
				'Temp_BugDetails_v2',
				'Description',
				self.text_description_source.get("1.0", END), True)
		except Exception as e:
			print('SaveTemp cannot save the report:', e)
			pass

	def _save_project_key(self, event=None):
		
		self.glossary_id = self.bottom_panel.project_id_select.get()
		self.glossary_id = self.glossary_id.replace('\n', '')
		if self.glossary_id in self.MyTranslator.glossary_list:
			print('Save current project key: ', self.glossary_id)
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'Translator', 'glossary_id', self.glossary_id)
			self.MyTranslator.glossary_id = self.glossary_id
			self.RenewMyTranslator()
		else:
			messagebox.showinfo('Error', "The selected project doesn't exist.")

	def _load_report(self,event=None):
		print('Load report')
		try:
			self.AppConfig.Refresh_Config_Data()
			self.Configuration = self.AppConfig.Config
			
			TextTitle  = self.Configuration['BugDetails']['TextTitle']
			self.TextTitle.delete("1.0", END)
			self.TextTitle.insert("end", TextTitle)
			
			TextServer  = self.Configuration['BugDetails']['TextServer']
			self.TextServer.delete("1.0", END)
			self.TextServer.insert("end", TextServer)
			
			TextClient  = self.Configuration['BugDetails']['TextClient']
			self.TextClient.delete("1.0", END)
			self.TextClient.insert("end", TextClient)
			
			TextReprodTime  = self.Configuration['BugDetails']['TextReprodTime']
			self.TextReprodTime.delete("1.0", END)
			self.TextReprodTime.insert("end", TextReprodTime)
			
			TextAccount  = self.Configuration['BugDetails']['TextAccount']
			self.TextAccount.delete("1.0", END)
			self.TextAccount.insert("end", TextAccount)
			
			TextTestReport  = self.Configuration['BugDetails']['TextTestReport']
			self.TextTestReport.delete("1.0", END)
			self.TextTestReport.insert("end", TextTestReport)
			
			TextShouldBe  = self.Configuration['BugDetails']['TextShouldBe']
			self.TextShouldBe.delete("1.0", END)
			self.TextShouldBe.insert("end", TextShouldBe)
				
			TextReproduceSteps  = self.Configuration['BugDetails']['TextReproduceSteps']
			self.TextReproduceSteps.delete("1.0", END)
			self.TextReproduceSteps.insert("end", TextReproduceSteps)
	
			self.HeaderOptionA.set(self.Configuration['BugDetails']['HeaderA'])
			self.HeaderOptionB.set(self.Configuration['BugDetails']['HeaderB'])


		except Exception as e:
			print('Fail somewhere:', e)
			pass

	def LoadTempReport(self):
		"""Load the text input from the previous session.
		
		The text is loaded from the config.
		"""
		try:
			self.AppConfig.Refresh_Config_Data()
			self.Configuration = self.AppConfig.Config
			
			TextTitle  = self.Configuration['Temp_BugDetails']['TextTitle']
			self.TextTitle.delete("1.0", END)
			self.TextTitle.insert("end", TextTitle)
			
			TextServer  = self.Configuration['Temp_BugDetails']['TextServer']
			self.TextServer.delete("1.0", END)
			self.TextServer.insert("end", TextServer)
			
			TextClient  = self.Configuration['Temp_BugDetails']['TextClient']
			self.TextClient.delete("1.0", END)
			self.TextClient.insert("end", TextClient)
			
			TextReprodTime  = self.Configuration['Temp_BugDetails']['TextReprodTime']
			self.TextReprodTime.delete("1.0", END)
			self.TextReprodTime.insert("end", TextReprodTime)
			
			TextAccount  = self.Configuration['Temp_BugDetails']['TextAccount']
			self.TextAccount.delete("1.0", END)
			self.TextAccount.insert("end", TextAccount)
			
			TextTestReport  = self.Configuration['Temp_BugDetails']['TextTestReport']
			self.TextTestReport.delete("1.0", END)
			self.TextTestReport.insert("end", TextTestReport)
			
			TextShouldBe  = self.Configuration['Temp_BugDetails']['TextShouldBe']
			self.TextShouldBe.delete("1.0", END)
			self.TextShouldBe.insert("end", TextShouldBe)
				
			TextReproduceSteps  = self.Configuration['Temp_BugDetails']['TextReproduceSteps']
			self.TextReproduceSteps.delete("1.0", END)
			self.TextReproduceSteps.insert("end", TextReproduceSteps)
	
			self.HeaderOptionA.set(self.Configuration['Temp_BugDetails']['HeaderA'])
			self.HeaderOptionB.set(self.Configuration['Temp_BugDetails']['HeaderB'])

			## SIMPLE TRANSLATOR TAB
			SourceText  = self.Configuration['Temp_BugDetails']['SimpleTranslator']
			self.SourceText.delete("1.0", END)
			self.SourceText.insert("end", SourceText)
			
			## BUG WRITER_V2 TAB
			self.header_option_a_v2.set(
				self.Configuration['Temp_BugDetails_v2']['Header A'])
			self.header_option_b_v2.set(
				self.Configuration['Temp_BugDetails_v2']['Header B'])
			
			self.text_bug_title_v2.delete("1.0", END)
			self.text_bug_title_v2.insert(
				"end", self.Configuration['Temp_BugDetails_v2']['Bug Title'])
			
			self.text_repro_step_source.delete("1.0", END)
			self.text_repro_step_source.insert(
				"end", self.Configuration['Temp_BugDetails_v2']['Reproduce Steps'])
			
			self.text_expected_result_source.delete("1.0", END)
			self.text_expected_result_source.insert(
				"end", self.Configuration['Temp_BugDetails_v2']['Expected Results'])
			
			self.text_description_source.delete("1.0", END)
			self.text_description_source.insert(
				"end", self.Configuration['Temp_BugDetails_v2']['Description'])

		except Exception as e:
			print('LoadTemp failed somewhere:', e)

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

class BottomPanel(Frame):
	def __init__(self, master):
		Frame.__init__(self, master)
		#self.pack(side=BOTTOM, fill=X)          # resize with parent
		
		# separator widget
		#Separator(orient=HORIZONTAL).grid(in_=self, row=0, column=1, sticky=E+W, pady=5)
		#Row = 1
		
		#Label(text='Version', width=15).grid(in_=self, row=Row, column=Col, padx=5, pady=5, sticky=W)
		#Col += 1
		#Label(textvariable=master.VersionStatus, width=15).grid(in_=self, row=Row, column=Col, padx=0, pady=5, sticky=W)
		#master.VersionStatus.set('-')
		Col = 1
		Row = 1
		self.Bottom_Frame = LabelFrame(master, text="DB INFO", padding=0,)
		self.Bottom_Frame.pack(side=BOTTOM, fill=X)
		#self.Bottom_Frame = master
		
		Label(text='Update', width=15).grid(in_=self.Bottom_Frame, row=Row, column=Col, padx=5, pady=5, sticky=E)
		Col += 1
		Label(textvariable=master._update_day, width=20).grid(in_=self.Bottom_Frame, row=Row, column=Col, padx=0, pady=5, sticky=E)
		master._update_day.set('-')
		Col += 1
		DictionaryLabelA = Label(text=master.LanguagePack.Label['Database'], width=15)
		DictionaryLabelA.grid(in_=self.Bottom_Frame, row=Row, column=Col, padx=5, pady=5, sticky=E)
		Col += 1
		Label(textvariable=master.DictionaryStatus, width=15).grid(in_=self.Bottom_Frame, row=Row, column=Col, padx=0, pady=5, sticky=E)
		master.DictionaryStatus.set('0')
		Col += 1
		Label(text=master.LanguagePack.Label['Header'], width=15).grid(in_=self.Bottom_Frame, row=Row, column=Col, padx=5, pady=5, sticky=E)
		Col += 1
		Label(textvariable=master.HeaderStatus, width=15).grid(in_=self.Bottom_Frame, row=Row, column=Col, padx=0, pady=5, sticky=E)
		master.HeaderStatus.set('0')
		Col += 1
		Label(text= master.LanguagePack.Label['ProjectKey'], width=15).grid(in_=self.Bottom_Frame, row=Row, column=Col, padx=5, pady=5, sticky=E)
		Col += 2
		self.project_id_select = AutocompleteCombobox()
		self.project_id_select.Set_Entry_Width(30)
		self.project_id_select.set_completion_list([])
		self.project_id_select.grid(in_=self.Bottom_Frame, row=Row, column=Col, padx=5, pady=5, stick=E)
		self.project_id_select.bind("<<ComboboxSelected>>", master._save_project_key)
		self.project_id_select.bind("<Return>", master._save_project_key)
		Col += 1
		self.RenewTranslatorMain = Button(text=master.LanguagePack.Button['RenewDatabase'], width=15, command= master.RenewMyTranslator, state=DISABLED, style= master.Btn_Style)
		self.RenewTranslatorMain.grid(in_=self.Bottom_Frame, row=Row, column=Col, padx=5, pady=5, stick=E)

		self.rowconfigure(0, weight=1)
		#self.columnconfigure(0, weight=1)
		self.Bottom_Frame.grid_columnconfigure(7, minsize=200)

#Simple Translator
def SimpleTranslate(queue, MyTranslator, source_text):
	"""Put the translated text requested from single_translate()
	to process queue for later use.
	
	Args:
		Text --- list
			Source text which is processed in single_translate() func.
	"""
	#Translated = MyTranslator.translate(Text)
	try:
		# To determine whether or not [Translate All] button is used
		if isinstance(source_text, dict):
			Translated = MyTranslator.multifield_translate(source_text)
		else:
			Translated = MyTranslator.translate(source_text)
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
			Details += '\r\n<p><b>'+ str(x) + ')</b>&nbsp;' + row + '&nbsp;</p>'
			x += 1
		Details += '\r\n================================================='
		x = 1
		for row in Text_List_Old:
			Details += '\r\n<p><b>' + str(x) + ')</b>&nbsp;' + row + '&nbsp;</p>'
			x += 1
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			x = 1
			for row in Text_List_Secondary:
				Details += '\r\n<p><b>' + str(x) + ')</b>&nbsp;' + row + '&nbsp;</p>'
				x += 1	
	else:
		for row in Text_List_Old:
			Details += '\r\n<p><b>'+ str(x) + ')</b>&nbsp;' + row + '&nbsp;</p>'
			x += 1
		Details += '\r\n================================================='
		x = 1
		for row in Text_List:
			Details += '\r\n<p><b>' + str(x) + ')</b>&nbsp;' + row + '&nbsp;</p>'
			x += 1
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			x = 1
			for row in Text_List_Secondary:
				Details += '\r\n<p><b>' + str(x) + ')</b>&nbsp;' + row + '&nbsp;</p>'
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
			Details += '\r\n' + str(x) + ') ' + row
			x += 1
		Details += '\r\n================================================='
		x = 1
		for row in Text_List_Old:
			Details += '\r\n' + str(x) + ') ' + row
			x += 1
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n' + str(x) + ') ' + row
				x += 1
	else:
		for row in Text_List_Old:
			Details += '\r\n' + str(x) + ') ' + row
			x += 1
		Details += '\r\n================================================='
		x = 1
		for row in Text_List:
			Details += '\r\n' + str(x) + ') ' + row
			x += 1
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n' + str(x) + ') ' + row
				x += 1
	return Details

def Simple_Row_CSS_Template(Lang, Title, Text_List, Text_List_Old, Text_List_Secondary = []):
	print('Text_List_Secondary', Text_List_Secondary)
	Details = ''
	if Lang == 'ko':		
		for row in Text_List:
			Details += '\r\n<p>'+ row + '&nbsp;</p>'
		Details += '\r\n================================================='
		for row in Text_List_Old:
			Details += '\r\n<p>' + row + '&nbsp;</p>'
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n<p>' + row + '&nbsp;</p>'
	else:
		for row in Text_List_Old:
			Details += '\r\n<p>'+ row + '&nbsp;</p>'
		Details += '\r\n================================================='
		for row in Text_List:
			Details += '\r\n<p>' + row + '&nbsp;</p>'
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n<p>' + row + '&nbsp;</p>'
	
	Details = AddCssLayout(Title, Details)
	return Details

def Simple_Row_Template(Lang, Title, Text_List, Text_List_Old, Text_List_Secondary = []):
	#print('Text_List_Secondary', Text_List_Secondary)
	Details = "\r\n"
	Details += Add_Style(Title)
	if Lang == 'ko':		
		for row in Text_List:
			Details += '\r\n'+ row
		Details += '\r\n================================================='
		for row in Text_List_Old:
			Details += '\r\n'+ row
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n'+ row

	else:
		for row in Text_List_Old:
			Details += '\r\n'+ row
		Details += '\r\n================================================='
		for row in Text_List:
			Details += '\r\n'+ row
		if len(Text_List_Secondary) > 0:
			Details += '\r\n================================================='
			for row in Text_List_Secondary:
				Details += '\r\n'+ row
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

def matches(fieldValue, acListEntry):
	pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
	return re.match(pattern, acListEntry)

def fixed_map(style, option):
	# Fix for setting text colour for Tkinter 8.6.9
	# From: https://core.tcl.tk/tk/info/509cafafae
	#
	# Returns the style map for 'option' with any styles starting with
	# ('!disabled', '!selected', ...) filtered out.
	# style.map() returns an empty list for missing options, so this
	# should be future-safe.
	return [elm for elm in style.map('Treeview', query_opt=option) if
	  elm[:2] != ('!disabled', '!selected')]

def main():

	MyTranslator = Queue()
	return_text = Queue()
	MyManager = Manager()
	grammar_check_result = MyManager.list()
	tm_manager = MyManager.list()
	language_tool_enable = False

	try:
		AppConfig = ConfigLoader(Writer = True)
		Configuration = AppConfig.Config
		Transparency  = Configuration['Bug_Writer']['Transparent']
	except Exception as e:
		print("Error while getting Tranparency: ", e)
		Transparency = 97
	
	root = Tk()
	root.attributes("-alpha", (Transparency/100))

	# root.geometry("400x350+300+300")
	# application = MyTranslatorHelper(root, return_text, MyTranslator, grammar_check_result = grammar_check_result, tm_manager = tm_manager, language_tool_enable = language_tool_enable)

	try:
		root.attributes('-topmost', True)
		application = MyTranslatorHelper(
			root, return_text, MyTranslator,
			grammar_check_result=grammar_check_result,
			tm_manager=tm_manager,
			language_tool_enable=language_tool_enable)
		root.attributes('-topmost', False)
		root.mainloop()
		application.MyTranslator.send_tracking_record()
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