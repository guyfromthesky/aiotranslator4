#System variable and io handling
import sys
import os
import re
#import signal
import configparser
import string
#Regular expression handling

#Object copy, handle excel style
import copy
#Get timestamp
import datetime
from datetime import date
import time
#function difination
import pyperclip

#from tkinter import *
#from tkinter.ttk import *
from tkinter.ttk import Entry, Combobox, Label, Style, Treeview, Scrollbar
from tkinter.ttk import Radiobutton, Checkbutton, Button

from tkinter import Tk, Frame
from tkinter import Menu, filedialog, messagebox, ttk
from tkinter import Text
from tkinter import IntVar, StringVar
from tkinter import W, E, S, N, END
from tkinter import WORD, NORMAL, ACTIVE, INSERT
from tkinter import DISABLED
from tkinter import scrolledtext 
from tkinter import PhotoImage
#from tkinter import filedialog
#from tkinter import messagebox
#from tkinter import ttk

import base64
import configparser
import multiprocessing
from multiprocessing import Queue, Process, Manager

import pickle
import queue 

import webbrowser

from libs.aiotranslator import Translator
from libs.aiotranslator import ver_num as TranslatorVersion
from libs.aioconfigmanager import ConfigLoader

from libs.version import get_version

from openpyxl import load_workbook, worksheet, Workbook

from google.cloud import logging
import json

tool_display_name = "Translator Helper"
tool_name = 'writer'
rev = 4000
ver_num = get_version(rev) 
version = tool_display_name  + " " +  ver_num + " | " + "Translator lib " + TranslatorVersion

DELAY = 20




#**********************************************************************************
# UI handle ***********************************************************************
#**********************************************************************************

class MyTranslatorHelper(Frame):
	def __init__(self, parent, report_queue, step_queue, info_queue, title_queue, csscode_queue, TranslationQueue = None, MyTranslator_Queue = None, MyDB_Queue = None, TMManager = None,):

		Frame.__init__(self, parent)
		
		self.parent = parent
		self.MyTranslator_Queue = MyTranslator_Queue
		self.MyDB_Queue = MyDB_Queue
		self.MyTranslator = None
		self.My_DB = None

		self.TMManager = TMManager
		self.ReturnedText = TranslationQueue

		self.SourceWidth = 62
		self.ButtonSize = 20
		self.RowSize = 20

		self.strTestVersion = ""
		self.strTestInfo = ""
		self.strReport = ""
		self.strReprodSteps = ""
		self.strShouldBe = ""
		self.strTitle = ""
		self.strTitleEN = ""
		self.HeaderList = ['']
		self.HeaderA = ""
		self.HeaderB = ""

		self.ButtonWidth = 20
		self.HalfButtonWidth = 15

		self.report = report_queue
		self.steps = step_queue
		self.info = info_queue
		self.title = title_queue
		self.csscode_queue = csscode_queue



		self.init_App_Setting()

		if self.AppLanguage != 'kr':
			from libs.languagepack import LanguagePackEN as LanguagePack
		else:
			from libs.languagepack import LanguagePackKR as LanguagePack

		self.LanguagePack = LanguagePack

		self.initUI()

		#self.LoadTempReport()

		self.GenerateTranslatorEngine()
		
	# Menu function
	def Error(self, ErrorText):
		messagebox.showinfo('Translate error...', ErrorText)	

	def OpenWeb(self):
		webbrowser.open_new(r"https://confluence.nexon.com/display/NWMQA/AIO+Translator")

	def About(self):
		messagebox.showinfo("About....", "Creator: Evan@nexonnetworks.com")

	def initUI(self):
		self.parent.resizable(False, False)
		self.parent.title(version)

		self.Generate_Menu_UI()
		self.Generate_Tab_UI()

		#Shared variable

		self.Generate_BugWriter_UI(self.BugWriter)
		self.Generate_SimpleTranslator_UI(self.SimpleTranslator)
		self.Generate_TranslateSetting_UI(self.TranslateSetting)
		#self.Generate_TM_Browser_UI(self.TM_Browser)
		#self.Generate_TMEditor_UI(self.TMEditor)

		#self.Init_Translator_Config

	def Generate_Tab_UI(self):
		TAB_CONTROL = ttk.Notebook(self.parent)
		
		#Tab1
		self.BugWriter = ttk.Frame(TAB_CONTROL)
		TAB_CONTROL.add(self.BugWriter, text=self.LanguagePack.Tab['BugWriter'])
		
		#Tab2
		self.SimpleTranslator = ttk.Frame(TAB_CONTROL)
		TAB_CONTROL.add(self.SimpleTranslator, text=self.LanguagePack.Tab['SimpleTranslator'])

		#Tab3
		self.TranslateSetting = ttk.Frame(TAB_CONTROL)
		TAB_CONTROL.add(self.TranslateSetting, text=  self.LanguagePack.Tab['Translator'])

		#Tab4
		#self.TM_Browser = ttk.Frame(TAB_CONTROL)
		#TAB_CONTROL.add(self.TM_Browser, text=self.LanguagePack.Tab['Utility'])

		#Tab5
		#self.TMEditor = ttk.Frame(TAB_CONTROL)
		#TAB_CONTROL.add(self.TMEditor, text=self.LanguagePack.Tab['TMEditor'])

		TAB_CONTROL.pack(expand=1, fill="both")	

	def Generate_Menu_UI(self):
		menubar = Menu(self.parent) 
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
		file.add_command(label =  self.LanguagePack.Menu['Exit'], command = self.parent.destroy) 
		# Adding Help Menu
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

	def Generate_BugWriter_UI(self, Tab):
		Row=1
		#Label(self.BugWriter, text="Translator: ").grid(row=Row, column=1, padx=5, pady=5, sticky=W)
		#self.TranslatorAgent = IntVar()	
		#Radiobutton(self.BugWriter, width=10, text='Google', value=1, variable=self.TranslatorAgent, command = self.SetTranslatorAgent).grid(row=Row, column=2, padx=5, pady=5)
		#Radiobutton(self.BugWriter, width=10, text='Kakao', value=2, variable=self.TranslatorAgent, command = self.SetTranslatorAgent).grid(row=Row, column=3, padx=5, pady=5)
		#self.TranslatorAgent.set(1)
		
		Label(Tab, text= self.LanguagePack.Label['Language'], width= 10).grid(row = Row, column = 1, padx=5, pady=10, stick=W)
		self.BugWriterLanguage = IntVar()
		Radiobutton(Tab, text=self.LanguagePack.Option['Hangul'], value=1, variable=self.BugWriterLanguage, command = self.UpdateHeaderList).grid(row = Row, column=2, padx=5, pady=10)	
		Radiobutton(Tab, text=self.LanguagePack.Option['English'], value=2, variable=self.BugWriterLanguage, command = self.UpdateHeaderList).grid(row = Row, column=3, padx=5, pady=10)
		if self.AppLanguage != 'kr':
			self.BugWriterLanguage.set(1)
		else:
			self.BugWriterLanguage.set(2)
	
		Label(Tab, text= self.LanguagePack.Label['ProjectKey']).grid(row=Row, column=4, padx=5, pady=5, sticky=W)
		self.Text_GlossaryID = AutocompleteCombobox(Tab)
		self.Text_GlossaryID.Set_Entry_Width(20)
		self.Text_GlossaryID.set_completion_list([])
		self.Text_GlossaryID.grid(row=Row, column=5, columnspan=2, padx=5, pady=5, stick=W)

		self.Text_GlossaryID.bind("<<ComboboxSelected>>", self.SaveProjectKey)
		#Button(Tab, width = self.HalfButtonWidth, text= self.LanguagePack.Button['Save'], command= self.SaveProjectKey).grid(row=Row, column=7, padx=5, pady=5, sticky=E)
		


		Label(Tab, textvariable=self.Notice).grid(row=Row, column=6, columnspan=5, padx=5, pady=5, stick=E)

		Row+=1
		Label(Tab, text=self.LanguagePack.Label['BugTitle']).grid(row=Row, column = 1, padx=5, pady=5, stick=W)
		#self.HeaderList = ['','Pizza','Lasagne','Fries','Fish','Potatoe']

		#AutocompleteCombobox
		self.HeaderOptionA = AutocompleteCombobox(Tab)
		self.HeaderOptionA.Set_Entry_Width(30)
		self.HeaderOptionA.set_completion_list(self.HeaderList)
		self.HeaderOptionA.grid(row=Row, column=2, padx=5, pady=5, sticky=W)
		
		self.TextTitle = Text(Tab, width=90, height=3, undo=True, wrap=WORD)
		self.TextTitle.grid(row=Row, column=3, columnspan=8, rowspan=2, padx=5, pady=5, stick=E)

		Row+=1

		self.HeaderOptionB = AutocompleteCombobox(Tab)
		self.HeaderOptionB.Set_Entry_Width(30)
		self.HeaderOptionB.set_completion_list(self.HeaderList)
		self.HeaderOptionB.grid(row=Row, column=2, padx=5, pady=5, sticky=W)
		
		Row+=1
		Label(Tab, text=self.LanguagePack.Label['Server']).grid(row=Row, column=1, padx=5, pady=5, stick=W)

		self.TextServer = Text(Tab, width=35, height=1, undo=True)
		self.TextServer.grid(row=Row, column=2, columnspan=3, padx=5, pady=5, stick=W)
	
		Label(Tab, text=self.LanguagePack.Label['ReproduceTime']).grid(row=Row, column=5, padx=5, pady=5, stick=W)

		self.TextReprodTime = Text(Tab,width=20, height=1, undo=True)
		self.TextReprodTime.grid(row=Row, column=6, columnspan=2, padx=5, pady=5)

		
		Checkbutton(Tab, text=self.LanguagePack.Label['TestInfo'], variable = self.SkipTestInfo, command = self.SaveSetting).grid(row=Row, column=8, padx=5, pady=5, stick=W)
		#self.SkipTestInfo.set(1)

		Button(Tab, text=self.LanguagePack.Button['Reset'], width=10, command= self.ResetTestReport).grid(row=Row, column=9, padx=5, pady=5)

		self.GetTitleBtn = Button(Tab, text=self.LanguagePack.Button['GetTitle'], width=10, command=self.GetTitle, state=DISABLED)
		self.GetTitleBtn.grid(row=Row, column=10, padx=5, pady=5)

		Row+=1
		Label(Tab, text=self.LanguagePack.Label['Client']).grid(row=Row, column=1, padx=5, pady=5, stick=W)

		self.TextClient = Text(Tab, width=35, height=1, undo=True)
		self.TextClient.grid(row=Row, column=2, columnspan=3, padx=5, pady=5, stick=W)
		self.TextClient.insert("end", "ver.")

		self.TextAccount = Text(Tab,width=20, height=1, undo=True)
		Label(Tab, text=self.LanguagePack.Label['IDChar']).grid(row=Row, column=5, padx=5, pady=5, stick=W)
		
		self.TextAccount.grid(row=Row, column=6, columnspan=2, padx=5, pady=5)

		Checkbutton(Tab, text= 'Use Simple Template', variable = self.UseSimpleTemplate, command = self.SaveSetting).grid(row=Row, column=8, padx=5, pady=5, stick=W)
		#self.UseSimpleTemplate.set(1)

		Button(Tab, text=self.LanguagePack.Button['Load'], width=10, command= self.LoadReport).grid(row=Row, column=9, padx=5, pady=5)
		Button(Tab, text=self.LanguagePack.Button['Save'], width=10, command= self.SaveReport).grid(row=Row, column=10, padx=5, pady=5)

		Row+=1
		Label(Tab, width=10, text=self.LanguagePack.Label['Report']).grid(row=Row, column=1, columnspan=2, padx=5, pady=5, stick=W)
		
		Label(Tab, width=10, text=self.LanguagePack.Label['Search']).grid(row=Row, column=3, padx=5, pady=5, stick=E)


		self.SearchBox = AutocompleteCombobox(Tab)
		self.SearchBox.Set_Entry_Width(100)
		self.SearchBox.set_completion_list([])
		self.SearchBox.grid(row=Row, column=4, columnspan=7, padx=5, pady=5, sticky=E)

		Row+=1
		self.TextTestReport = Text(Tab, width=130, height=7, undo=True, wrap=WORD)
		self.TextTestReport.grid(row=Row, column=1, columnspan=10, rowspan=7, padx=5, pady=5, stick=W)
		Row+=7
		
		
		Row+=1
		Label(Tab, width=10, text=self.LanguagePack.Label['Steps']).grid(row=Row, column=1, columnspan=2, padx=5, pady=5, stick=W)
		Label(Tab, width=10, text=self.LanguagePack.Label['Expected']).grid(row=Row, column=6, columnspan=2, padx=0, pady=5, stick=W)

		
		self.GetReportBtn = Button(Tab, text=self.LanguagePack.Button['GetReport'], width=10, command= self.GenerateReportCSS, state=DISABLED)
		self.GetReportBtn.grid(row=Row, column=10, padx=5, pady=5)

		Row+=1
		self.TextReproduceSteps = Text(Tab, width=60, height=7, undo=True, wrap=WORD)
		self.TextReproduceSteps.grid(row=Row, column=1, columnspan=5, rowspan=7, padx=5, pady=5, stick=W)
		self.TextShouldBe = Text(Tab, width=60, height=7, undo=True, wrap=WORD) 
		self.TextShouldBe.grid(row=Row, column=6, columnspan=5, padx=5, pady=5, stick=E)
		Row+=7

		Row+=1

		Label(Tab, text='Version').grid(row=Row, column=1, padx=5, pady=5, sticky=W)
		Label(Tab, textvariable=self.VersionStatus).grid(row=Row, column=2, padx=0, pady=5, sticky=W)
		self.VersionStatus.set('-')

		Label(Tab, text='Update').grid(row=Row, column=3, padx=5, pady=5)
		Label(Tab, textvariable=self.UpdateDay).grid(row=Row, column=4, padx=0, pady=5)
		self.VersionStatus.set('-')
	
		DictionaryLabelA = Label(Tab, text=self.LanguagePack.Label['Database'])
		DictionaryLabelA.grid(row=Row, column=5, padx=5, pady=5)
		Label(Tab, textvariable=self.DictionaryStatus).grid(row=Row, column=6, padx=0, pady=5)
		self.DictionaryStatus.set('0')

		Label(Tab, text=self.LanguagePack.Label['Header']).grid(row=Row, column=7, padx=5, pady=5)
		Label(Tab, textvariable=self.HeaderStatus).grid(row=Row, column=8, padx=0, pady=5)
		self.HeaderStatus.set('0')


		self.RenewTranslatorMain = Button(Tab, text=self.LanguagePack.Button['RenewDatabase'], command= self.RenewMyTranslator, state=DISABLED)
		self.RenewTranslatorMain.grid(row=Row, column=10, padx=5, pady=5)
		
	def Generate_SimpleTranslator_UI(self, Tab):

		Row=1
		Label(Tab, textvariable=self.Notice).grid(row=Row, column=1, columnspan=10, padx=5, pady=5, sticky=E)
		#New Row
		Row +=1
		Label(Tab, text=self.LanguagePack.Label['SourceText'], width=10).grid(row=Row, column=1, columnspan = 5, padx=10, pady=0)
		Label(Tab, text=self.LanguagePack.Label['TargetText'], width=10).grid(row=Row, column=6, columnspan = 5, padx=10, pady=0)
		#New Row

		

		Row +=1
		self.SourceText = CustomText(Tab, width = self.SourceWidth, height=self.RowSize, undo=True) 
		#self.SourceText.tag_configure('blue', foreground="#0e2433")
		self.SourceText.tag_configure('blue', foreground= "blue")
		
		self.SourceText.grid(row=Row, column=1, columnspan=5, rowspan=self.RowSize, padx=15, pady=10, sticky=N+S+E+W)
		self.SourceText.bind("<Double-Return>", self.BindTranslate)
		self.SourceText.bind("<Double-Tab>", self.BindSwap)
		self.TargetText = Text(Tab, width = self.SourceWidth, height=10, undo=True) #
		self.TargetText.grid(row = Row, column=6, columnspan=5, rowspan=self.RowSize, padx=15, pady=10, sticky=N+S+E+W)
		Row +=self.RowSize
		Row +=1
		Button(Tab, text=self.LanguagePack.Button['Swap'], width = 20, command= self.Swap).grid(row=Row, column=5, columnspan=2, padx=0, pady=5)	
		
		#self.RenewTranslatorButton(Tab, text=self.LanguagePack.Button['RenewDatabase'], width = self.ButtonSize, command= self.RenewMyTranslator).grid(row = Row, column=8, padx=10, pady=5)
		self.RenewTranslator = Button(Tab, text=self.LanguagePack.Button['RenewDatabase'], width = self.ButtonSize, command= self.RenewMyTranslator, state=DISABLED)
		self.RenewTranslator.grid(row = Row, column=8, padx=10, pady=5)
		
		self.TranslateBtn = Button(Tab, text=self.LanguagePack.Button['Translate'], width = self.ButtonSize, command= self.Translate, state=DISABLED)
		self.TranslateBtn.grid(row=Row, column=10, columnspan=1,pady=5)		
		#New Row
		Row +=1
		Label(Tab, text=self.LanguagePack.Label['TargetLanguage'], width= 20).grid(row = Row, column = 1, padx=5, pady=10)
		
		self.SimpleTranslatorLanguage = IntVar()	
		Radiobutton(Tab, text=self.LanguagePack.Option['Hangul'], value=1, variable=self.SimpleTranslatorLanguage, command = None).grid(row = Row, column=2, padx=5, pady=10)	
		Radiobutton(Tab, text=self.LanguagePack.Option['English'], value=2, variable=self.SimpleTranslatorLanguage, command = None).grid(row = Row, column=3, padx=5, pady=10)
		self.SimpleTranslatorLanguage.set(2)
		
		Button(Tab, text=self.LanguagePack.Button['Bilingual'], width = self.ButtonSize, command= self.BtnBilingual).grid(row = Row, column=8, padx=10, pady=5)
		Button(Tab, text=self.LanguagePack.Button['TranslateAndBilingual'], width = self.ButtonSize, command= self.BtnTranslateAndBilingual).grid(row = Row, column=10, padx=10, pady=5)
		Row+=1
		Row+=1
		DictionaryLabelB = Label(Tab, text=self.LanguagePack.Label['Database'])
		DictionaryLabelB.grid(row=Row, column=1, padx=5, pady=5)
		#DictionaryLabelB.bind("<Enter>", lambda event : self.Notice.set( self.LanguagePack.Label['Database'] + ': ' + self.DictionaryPath.get()))
		
		Label(Tab, textvariable=self.DictionaryStatus).grid(row=Row, column=2, padx=0, pady=5, sticky=W)
		self.DictionaryStatus.set('0')

		Button(Tab, text=self.LanguagePack.Button['Copy'], width = self.ButtonSize, command= self.BtnCopy).grid(row = Row, column=10, padx=10, pady=5)

		#Tab.update()
		#Tab.minsize(self.SimpleTranslator.winfo_width(), self.SimpleTranslator.winfo_height())
		#self.parent.bind("<Configure>", self.UpdateSize)

		#Simple Translator UI

	def Generate_TranslateSetting_UI(self, Tab):
		Row = 1
		Label(Tab, textvariable=self.Notice).grid(row=Row, column=1, columnspan = 10, padx=5, pady=5, sticky= W)

		Row += 1
		Label(Tab, text= self.LanguagePack.Label['ProjectKey']).grid(row=Row, column=1, padx=5, pady=5, sticky=W)

		Row += 1

		Label(Tab, text= self.LanguagePack.Label['LicensePath']).grid(row=Row, column=1, padx=5, pady=5, sticky=E)
		self.TextLicensePath = Entry(Tab,width = 120, state="readonly", textvariable=self.LicensePath)
		self.TextLicensePath.grid(row=Row, column=3, columnspan=5, padx=5, pady=5, sticky=W)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Browse'], command= self.Btn_Select_License_Path).grid(row=Row, column=8, columnspan=2, padx=5, pady=5, sticky=E)


		
	def Generate_Utility_UI(self, Tab):
		Row = 1
		Label(Tab, textvariable=self.Notice).grid(row=Row, column=1, columnspan = 10, padx=5, pady=5, sticky= W)
		
		Row += 1
		Label(Tab, text="Data table lookup: ", width= 20, font='calibri 11 bold').grid(row=Row, column=1, padx=10, pady=5, sticky=W)
		
		Row += 1
		Label(Tab, text='Source Data: ', width= 20, font='calibri 11 bold').grid(row=Row, column=1, padx=5, pady=5, sticky=W)

		#self.CurrentDataSource.set(self.DictionaryPath)
		self.TextDataTableSource = Entry(Tab,width = 120, state="readonly", textvariable=self.CurrentDataSource)
		self.TextDataTableSource.grid(row=Row, column=2, columnspan=7, padx=5, pady=5, sticky=W)
		Button(Tab, width = 20, text=  self.LanguagePack.Button['Browse'], command= self.SelectDataTableSource).grid(row=Row, column=9, columnspan=2, padx=5, pady=5, sticky=E)

		Row +=1
		Label(Tab, text="ID: ", width=10).grid(row=Row, column=1, columnspan = 5, padx=10, pady=0, sticky= W)
		#Label(Tab, text="Target: ", width=10).grid(row=Row, column=6, columnspan = 5, padx=10, pady=0)

		self.SourceTM = Text(Tab, width = self.SourceWidth, height=1, undo=True) 
		self.SourceTM.grid(row=Row, column=2, columnspan=7, rowspan=self.RowSize, padx=5, pady=0, sticky=W)
		#self.SourceTM.bind("<Double-Return>", lambda event : self.Notice.set(self.BtnTMTranslate()))

	

	def Btn_Select_License_Path(self):
		filename = filedialog.askopenfilename(title =  self.LanguagePack.ToolTips['SelectDB'],filetypes = (("JSON files","*.json" ), ), )	
		if filename != "":
			LicensePath = self.CorrectPath(filename)
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'License_File', 'path', LicensePath, True)
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = LicensePath
			self.LicensePath.set(LicensePath)
		else:
			self.Notice.set("No file is selected")


	# Init functions
	# Some option is saved for the next time use
	def init_App_Setting(self):

		self.SkipTestInfo = IntVar()
		self.UseSimpleTemplate = IntVar()

		self.LicensePath = StringVar()
		#self.DictionaryPath = StringVar()
		self.TMPath = StringVar()

		self.CurrentDataSource = StringVar()
		self.Notice = StringVar()
		self.DictionaryStatus = StringVar()
		
		#self.TMStatus  = StringVar()
		self.HeaderStatus = StringVar()

		self.VersionStatus  = StringVar()
		self.UpdateDay = StringVar()

		self.AppConfig = ConfigLoader()
		self.Configuration = self.AppConfig.Config
		self.AppLanguage  = self.Configuration['Bug_Writer']['app_lang']

		self.SkipTestInfo.set(self.Configuration['Bug_Writer']['test_info_inable'])
		#print(self.Configuration['Bug_Writer']['test_info_inable'])
		self.UseSimpleTemplate.set(self.Configuration['Bug_Writer']['use_simple_template'])
		#print(self.Configuration['Bug_Writer']['use_simple_template'])


		self.LicensePath.set(self.Configuration['License_File']['path'])
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.Configuration['License_File']['path']
		#self.DictionaryPath.set(self.Configuration['Database']['path'])
		self.TMPath.set(self.Configuration['TranslationMemory']['path'])

		self.GlossaryID = self.Configuration['Glossary_ID']['value']
	
		
		


	# Menu function
	def SetLanguageKorean(self):
		self.AppLanguage = 'kr'
		self.SaveAppLanguage(self.AppLanguage)
		#self.initUI()
	
	def SetLanguageEnglish(self):
		self.AppLanguage = 'en'
		self.SaveAppLanguage(self.AppLanguage)
		#self.initUI()

	def SaveAppLanguage(self, language):

		self.Notice.set(self.LanguagePack.ToolTips['AppLanuageUpdate'] + " "+ language) 
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'app_lang', language)
	
	def SelectDictionary(self):
		filename = filedialog.askopenfilename(title = "Select Database file",filetypes = (("Dictionary files","*.xlsx *.xlsm"), ), )	
		if filename != "":
			NewDictionary = self.CorrectPath(filename)	
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'Database', 'path', NewDictionary, True)
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
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'TranslationMemory', 'path', NewTM, True)
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
				
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'TranslationMemory', 'path', NewTM, True)

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


	def SetLanguage(self):
		if self.SimpleTranslatorLanguage.get() == 1:
			to_language = 'ko'
			from_language = 'en'
			self.Notice.set(self.LanguagePack.ToolTips['AppLanuageUpdate'] +'Hangul')
		else:
			to_language = 'en'
			from_language = 'ko'
			self.Notice.set(self.LanguagePack.ToolTips['AppLanuageUpdate'] + 'English')
		
		self.MyTranslator.SetTargetLanguage(to_language)
		self.MyTranslator.SetSourceLanguage(from_language)

	def GenerateTranslatorEngine(self):
		self.Notice.set(self.LanguagePack.ToolTips['AppInit'])
		if self.BugWriterLanguage.get() == 1:
			to_language = 'ko'
			from_language = 'en'
		else:
			to_language = 'en'
			from_language = 'ko'

		#self.GlossaryID = self.Text_GlossaryID.get()
		tm_path = self.TMPath.get()
		#self.TranslatorProcess = Process(target=GenerateTranslator, args=(self.MyTranslator_Queue, self.TMManager, from_language, to_language, self.GlossaryID,))
		self.TranslatorProcess = Process(target=GenerateTranslator, args=(self.MyTranslator_Queue, self.TMManager, from_language, to_language, self.GlossaryID,))
		self.TranslatorProcess.start()
		self.after(DELAY, self.GetMyTranslator)
		
	def GetMyTranslator(self):
		try:
			self.MyTranslator = self.MyTranslator_Queue.get_nowait()
		except queue.Empty:
			self.after(DELAY, self.GetMyTranslator)

		if self.MyTranslator != None:
			self.Notice.set(self.LanguagePack.ToolTips['AppInitDone'])

			#self.MyTranslator.Convert_Translation_Memory()

			self.GetTitleBtn.configure(state=NORMAL)
			self.GetReportBtn.configure(state=NORMAL)
			self.TranslateBtn.configure(state=NORMAL)
			#self.BtnTranslateTM.configure(state=NORMAL)
			self.RenewTranslator.configure(state=NORMAL)
			self.RenewTranslatorMain.configure(state=NORMAL)

			try:
				header_count = str(len(self.MyTranslator.Header))
			except:
				header_count = 0

			self.HeaderStatus.set(header_count)
			self.UpdateHeaderList()
			self.UpdatePredictionList()

			try:
				db_count = str(len(self.MyTranslator.Dictionary))
			except:
				db_count = 0
			
			self.DictionaryStatus.set(db_count)
			glossary_list = [""] + self.MyTranslator.GlossaryList
			self.Text_GlossaryID.set_completion_list(glossary_list)
			
			if self.GlossaryID in self.MyTranslator.GlossaryList:
				self.Text_GlossaryID.set(self.GlossaryID)
			else:
				self.Text_GlossaryID.set("")

			if isinstance(self.MyTranslator.Version, str):
				version = self.MyTranslator.Version[0:10]
			else:
				version = '-'

			if isinstance(self.MyTranslator.UpdateDay, str):
				Date = self.MyTranslator.UpdateDay[0:10]
			else:
				Date = '-'

			self.VersionStatus.set(version)
			self.UpdateDay.set(Date)

			if isinstance(self.MyTranslator.latest_version, str):
				if rev < int(self.MyTranslator.latest_version):
					self.Error('Current version is lower than the minimal version allowed. Please update.')	
					webbrowser.open_new(r"https://confluence.nexon.com/display/NWMQA/AIO+Translator")
					self.quit()
					return

			if isinstance(self.MyTranslator.banned, bool):
				if self.MyTranslator.banned:
					self.Error('You\'re not allowed to use the tool. If you feel that it\'s unfair, please contact with your manager for more information.')	
					self.quit()
					return

				#self.Error('No Valid Project selected, please update the project ID in Translate Setting tab')	
			#DBLength = self.MyTranslator.get_glossary_length()
			#self.DictionaryStatus.set(str(DBLength))

			self.TranslatorProcess.join()
		else:
			self.Notice.set(self.LanguagePack.ToolTips['AppInit'])

	#Execute function
	def Translate(self):
		if self.LicensePath.get() == "":
			self.Error('Please select License file and relaunch the app!')
			return
			
		self.Notice.set(self.LanguagePack.ToolTips['Translating'])
		if self.SimpleTranslatorLanguage.get() == 1:
			self.MyTranslator.SetTargetLanguage('ko')
			self.MyTranslator.SetSourceLanguage('en')
		else:
			self.MyTranslator.SetTargetLanguage('en')
			self.MyTranslator.SetSourceLanguage('ko')

		SourceText = self.SourceText.get("1.0", END)
		try:
			SourceText = SourceText.split('\n')
		except:
			pass
		try:
			for text in SourceText:
				if text == "":
					SourceText.remove(text)
		except:
			pass
		
		self.p3 = Process(target=SimpleTranslate, args=(self.ReturnedText, self.MyTranslator, SourceText,))
		self.p3.start()
		self.after(DELAY, self.GetCompleteStatus)

	def GetCompleteStatus(self):
		if (self.p3.is_alive()):
			self.after(DELAY, self.GetCompleteStatus)
		else:
			try:
				Translated = self.ReturnedText.get()
				self.TargetText.delete("1.0", END)
				if Translated[0] != False:
					Show = "\n".join(Translated)
					Show = Show.replace('\r\n', '\n')
					self.TargetText.insert("end", Show)
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

	#Execute function
	def BtnTMTranslate(self):
		self.Notice.set(self.LanguagePack.ToolTips['Translating'])
		self.CurrentPair = None
		if self.SimpleTranslatorLanguage.get() == 1:
			x = 1
			y = 0
		else:
			x = 0
			y = 1

		self.CurrentPair = None
		SourceText = self.SourceTM.get("1.0", END)
		self.TargetTM.delete("1.0", END)

		try:
			SourceText = SourceText.split('\n')
		except:
			pass
		Translated = []
		for Text in SourceText:
	
			for pair in self.MyTranslator.TranslationMemory:
				if pair[x] == Text:
					Translated.append(pair[y])
					self.CurrentPair = pair
					self.Notice.set(self.LanguagePack.ToolTips['TMResultFound'])
					break

		if(self.CurrentPair == None):
			self.Notice.set(self.LanguagePack.ToolTips['TMResultNotFound'])
		Show = "\n".join(Translated)
		print('CurrentPair: ', self.CurrentPair)
		self.TargetTM.insert("end", Show)

	#Execute function
	def BtnRegularSearch(self):
		self.Notice.set(self.LanguagePack.ToolTips['Translating'])

		if self.SimpleTranslatorLanguage.get() == 1:
			x = 1
			y = 0
		else:
			x = 0
			y = 1

		SourceText = self.SourceTM.get("1.0", END)
		self.TargetTM.delete("1.0", END)

		try:
			SourceText = SourceText.split('\n')
		except:
			pass
		Translated = []
		for Text in SourceText:
			if Text != "":
				for pair in self.MyTranslator.TranslationMemory:
					if pair[x].find(Text) != -1:
						Translated.append(pair[y])

		
		#print('CurrentPair: ', self.CurrentPair)
		
		if len(Translated) < 1:
			self.Notice.set(self.LanguagePack.ToolTips['TMResultNotFound'])
		else:
			Show = "\n".join(Translated)
			self.TargetTM.insert("end", Show)	
		return

	def BtnCopy(self):
		Translated = self.TargetText.get("1.0", END)
		Translated = Translated.replace('\r', '')
		pyperclip.copy(Translated)
		self.Notice.set(self.LanguagePack.ToolTips['Copied'])
		return

	def BtnBilingual(self):
		SourceText = self.SourceText.get("1.0", END)
		SourceText = SourceText.replace('\r\n', '\n')
		TempList = SourceText.split('\n')
		SourceText = ('\n').join(TempList)

		Translated = self.TargetText.get("1.0", END)
		Translated = Translated.replace('\r\n', '\n')
		Bilingual = Translated + "\r\n" + "================================================" + "\r\n" + SourceText
		pyperclip.copy(Bilingual)
		self.Notice.set(self.LanguagePack.ToolTips['Copied'])
		return

	def BtnTranslateAndBilingual(self):
		pyperclip.copy("")
		try:
			if (self.SimpleTranslator.is_alive()):
				self.SimpleTranslator.terminate()
		except:
			pass
		self.Notice.set(self.LanguagePack.ToolTips['Translating'])
		self.TargetText.delete("1.0", END)

		if self.SimpleTranslatorLanguage.get() == 1:
			self.MyTranslator.SetTargetLanguage('ko')
			self.MyTranslator.SetSourceLanguage('en')
		else:
			self.MyTranslator.SetTargetLanguage('en')
			self.MyTranslator.SetSourceLanguage('ko')

		SourceText = self.SourceText.get("1.0", END)
		try:
			SourceText = SourceText.split('\n')
		except:
			pass
		self.SimpleTranslator = Process(target=SimpleTranslate, args=(self.ReturnedText, self.MyTranslator, SourceText,))
		self.SimpleTranslator.start()
		self.after(DELAY, self.Generate_Bilingual_Text)
		return
		
	def Generate_Bilingual_Text(self):
		if (self.SimpleTranslator.is_alive()):
			self.after(DELAY, self.Generate_Bilingual_Text)
			return
		else:
			try:
				Translated = self.ReturnedText.get()
				#Translated = Translated.replace('\r\n', '\n')
				if Translated[0] != False:
					Show = "\n".join(Translated)
					Show = Show.replace('\r\n', '\n')
					self.TargetText.insert("end", Show)
					self.Notice.set(self.LanguagePack.ToolTips['Translated'])
				
				SourceText = self.SourceText.get("1.0", END)
				SourceText = SourceText.replace('\r\n', '\n')
				
				Bilingual = Show + "\r\n" + "================================================" + "\r\n" + SourceText
				pyperclip.copy(Bilingual)
				self.Notice.set(self.LanguagePack.ToolTips['Copied'])
				self.SimpleTranslator.join()
			except queue.Empty:
				self.Notice.set(self.LanguagePack.ToolTips['TranslateFail'])
		return
	

	def BindSwap(self, event):
		self.Swap()
		return "break"

	def Swap(self):
		SourceText = self.SourceText.get("1.0", END)
		print(SourceText.encode('utf-8'))

		Translated = self.TargetText.get("1.0", END)
		print(Translated.encode('utf-8'))

		self.SourceText.delete("1.0", END)
		self.TargetText.delete("1.0", END)

		self.TargetText.insert("end", SourceText)
		self.SourceText.insert("end", Translated)
		
		if self.SimpleTranslatorLanguage.get() == 1:
			self.SimpleTranslatorLanguage.set(2)
			self.Notice.set(self.LanguagePack.ToolTips['LanguageSet'] + 'English')
		else:
			self.SimpleTranslatorLanguage.set(1)
			self.Notice.set(self.LanguagePack.ToolTips['LanguageSet'] + 'Hangul')

		self.MyTranslator.SwapLanguage()
		return

	def BindTranslate(self,event):
		self.Translate()
		return "break"

	def RenewMyTranslator(self):
		
		self.GetTitleBtn.configure(state=DISABLED)
		self.GetReportBtn.configure(state=DISABLED)
		self.TranslateBtn.configure(state=DISABLED)
		#self.BtnTranslateTM.configure(state=DISABLED)
		self.RenewTranslator.configure(state=DISABLED)
		self.RenewTranslatorMain.configure(state=DISABLED)

		#self.init_App_Setting()

		del self.MyTranslator
		self.MyTranslator = None
	

		#self.MyTranslator_Queue.clear()

		self.HeaderOptionA.set_completion_list([])
		self.HeaderOptionB.set_completion_list([])
		self.SearchBox.set_completion_list([])

		self.HeaderStatus.set('0')

		self.GenerateTranslatorEngine()

	#Option functions

	def UpdatePredictionList(self):
		#print('self.HeaderList', self.HeaderList)
		Autolist = []
		for item in self.MyTranslator.Dictionary:
			Autolist.append(item[0])
			Autolist.append(item[1])
		
		'''
		for item in self.MyTranslator.NameList:
			Autolist.append("\"" + item[0] + "\"")
			Autolist.append("\"" + item[1] + "\"")
		'''
		#set_completion_list
		#self.SearchBox.autocompleteList = Autolist
		self.SearchBox.set_completion_list(Autolist)
		#self.SearchBox.specialList = SpecialList



	def UpdateHeaderList(self):

		#AutocompleteCombobox
		
		self.HeaderListFull = self.MyTranslator.Header
		
		self.HeaderList = [""]

		if self.BugWriterLanguage.get() == 1:
			x = 1
			#y = 0
		else: 
			x = 0
			#y = 1

		for Header in self.HeaderListFull:
			self.HeaderList.append(Header[x])
		self.HeaderOptionA.set_completion_list(self.HeaderList)
		self.HeaderOptionB.set_completion_list(self.HeaderList)


	def ResetReport(self, event):
		self.ResetTestReport()

	def GetTitle(self):
		pyperclip.copy("")

		if self.BugWriterLanguage.get() == 1:
			self.MyTranslator.SetTargetLanguage('ko')
			self.MyTranslator.SetSourceLanguage('en')
		else:
			self.MyTranslator.SetTargetLanguage('en')
			self.MyTranslator.SetSourceLanguage('ko')

		self.Notice.set(self.LanguagePack.ToolTips['GenerateBugTitle'])
		self.strSourceTitle = self.TextTitle.get("1.0", END).replace('\n', '')
		self.strSourceTitle = self.TextTitle.get("1.0", END).replace('\r\n', '')
		self.Title_Translate = Process(target=TranslateTitle, args=(self.title, self.strSourceTitle, self.MyTranslator,))
		self.Title_Translate.start()
		self.after(DELAY, self.TextTitleGet)
		return

	def TextTitleGet(self):
		if (self.Title_Translate.is_alive()):
			self.after(DELAY, self.TextTitleGet)
			return
		else:
			try:
				TempTitle  = self.title.get(0)
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
					HeaderA_Translated = self.MyTranslator.TranslateHeader(HeaderA)
				else:
					HeaderA_Translated = False
					
				HeaderB = self.HeaderOptionB.get()
				if HeaderB != "":
					HeaderB_Translated = self.MyTranslator.TranslateHeader(HeaderB)
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
				
				pyperclip.copy(str(Title))
				self.Notice.set(self.LanguagePack.ToolTips['GeneratedBugTitle'])
				self.Title_Translate.join()
			except queue.Empty:
				self.Notice.set(self.LanguagePack.ToolTips['GenerateBugTitleFail'])
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
	def GenerateReportCSS(self):
		self.Notice.set(self.LanguagePack.ToolTips['GenerateBugReport'])
		pyperclip.copy("")

		if self.BugWriterLanguage.get() == 1:
			self.MyTranslator.SetTargetLanguage('ko')
			self.MyTranslator.SetSourceLanguage('en')
		else:
			self.MyTranslator.SetTargetLanguage('en')
			self.MyTranslator.SetSourceLanguage('ko')	

		TextTestServer = self.TextServer.get("1.0", END).replace('\n', '')
		TextTestClient = self.TextClient.get("1.0", END).replace('\n', '')

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

		Simple_Template = self.UseSimpleTemplate.get()

		To_Translate['TextTestReport'] = self.TextTestReport.get("1.0", END)
		To_Translate['TextShouldBe'] = self.TextShouldBe.get("1.0", END)
		To_Translate['TextReproduceSteps'] = self.TextReproduceSteps.get("1.0", END)

		self.BugWriter = Process(target=Translate_Simple, args=(self.report, To_Translate, Simple_Template, self.MyTranslator,))
		self.BugWriter.start()

		self.after(DELAY, self.GetBugDetails)

	def GetBugDetails(self):

		self.Notice.set(self.LanguagePack.ToolTips['ClipboardRemoved'])

		if (self.BugWriter.is_alive()):
			self.after(DELAY, self.GetBugDetails)
		else:
			self.Notice.set(self.LanguagePack.ToolTips['GeneratedBugReport'])
			self.BugWriter.join()

	def SaveReport(self):
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
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'TextTitle', TextTitle)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'TextServer', TextServer)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'TextClient', TextClient)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'TextReprodTime', TextReprodTime)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'TextAccount', TextAccount)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'TextTestReport', TextTestReport)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'TextReproduceSteps', TextReproduceSteps)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'TextShouldBe', TextShouldBe)

			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'HeaderA', HeaderA)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'BugDetails', 'HeaderB', HeaderB)
		except:
			pass

	def SaveTempReport(self):
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
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'TextTitle', TextTitle)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'TextServer', TextServer)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'TextClient', TextClient)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'TextReprodTime', TextReprodTime)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'TextAccount', TextAccount)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'TextTestReport', TextTestReport)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'TextReproduceSteps', TextReproduceSteps)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'TextShouldBe', TextShouldBe)

			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'HeaderA', HeaderA)
			self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Temp_BugDetails', 'HeaderB', HeaderB)
		except:
			pass



	def SaveProjectKey(self, event=None):
		
		self.GlossaryID = self.Text_GlossaryID.get()
		self.GlossaryID = self.GlossaryID.replace('\n', '')
		print('Save current project key: ', self.GlossaryID)
		self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'Glossary_ID', 'value', self.GlossaryID)
		self.MyTranslator.GlossaryID = self.GlossaryID
		self.RenewMyTranslator()

	def LoadReport(self):
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


		except:
			print('Fail somewhere')
			pass

	def LoadTempReport(self):
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


		except:
			print('Fail somewhere')
			pass		


	def SaveSetting(self):

		#self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'test_info_inable', 'path', self.SkipTestInfo.get())
		#self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'use_simple_template', 'path', self.UseSimpleTemplate.get())
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'test_info_inable', self.SkipTestInfo.get())
		self.AppConfig.Save_Config(self.AppConfig.Writer_Config_Path, 'Bug_Writer', 'use_simple_template', self.UseSimpleTemplate.get())
# Class

class CustomText(Text):
	'''A text widget with a new method, highlight_pattern()

	example:

	text = CustomText()
	text.tag_configure("red", foreground="#ff0000")
	text.highlight_pattern("this should be red", "red")

	The highlight_pattern method is a simplified python
	version of the tcl code at http://wiki.tcl.tk/3246
	'''
	def __init__(self, *args, **kwargs):
		Text.__init__(self, *args, **kwargs)

	def highlight_pattern(self, pattern, tag, start="1.0", end="end",
						  regexp=False):
		'''Apply the given tag to all text that matches the given pattern

		If 'regexp' is set to True, pattern will be treated as a regular
		expression according to Tcl's regular expression syntax.
		'''
		start = self.index(start)
		end = self.index(end)
		self.mark_set("matchStart", start)
		self.mark_set("matchEnd", start)
		self.mark_set("searchLimit", end)

		count = IntVar()

		while True:
			index = self.search(pattern, "matchEnd","searchLimit",
								count=count, regexp=regexp)
			if index == "": break
			if count.get() == 0: break # degenerate pattern which matches zero-length strings
			real_index = index.split('.')
			start_pos = index
			end_pos = str(real_index[0]) + '.' + str(int(real_index[1]) + count.get())
			self.mark_set("matchStart", str(start_pos))	
			self.mark_set("matchEnd", str(end_pos))
			#self.mark_set("matchStart", str('1.'+ str(start_pos)))
			#self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
			self.tag_add(tag, "matchStart", "matchEnd")


class AutocompleteCombobox(Combobox):

	def set_completion_list(self, completion_list):
		"""Use our completion list as our drop down selection menu, arrows move through menu."""
		self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
		self._hits = []
		self._hit_index = 0
		self.position = 0
		self.bind('<KeyRelease>', self.handle_keyrelease)
		self['values'] = self._completion_list  # Setup our popup menu
		#self._w = 10
		self.delete(0,END)	

	def Set_Entry_Width(self, width):
		self.configure(width=width)

	def Set_DropDown_Width(self, width):
		print('Change size: ', width)
		style = Style()
		style.configure('TCombobox', postoffset=(0,0,width,0))
		self.configure(style='TCombobox')

	def autofill(self, delta=0):
		"""autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
		if delta: # need to delete selection otherwise we would fix the current position
			self.delete(self.position, END)
		else: # set position to end so selection starts where textentry ended
			self.position = len(self.get())
		# collect hits
		_hits = []
		for element in self._completion_list:
			if self.get().lower() in element: # Match case insensitively
				_hits.append(element)
		# if we have a new hit list, keep this in mind
		if _hits != self._hits:
			self._hit_index = 0
			self._hits=_hits
		# only allow cycling if we are in a known hit list
		if _hits == self._hits and self._hits:
			self._hit_index = (self._hit_index + delta) % len(self._hits)
		# now finally perform the auto completion
		'''
		if self._hits:
			self.delete(0,END)
			self.insert(0,self._hits[self._hit_index])
			self.select_range(self.position,END)
		'''

	def autocomplete(self, delta=0):
		"""autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
		if delta: # need to delete selection otherwise we would fix the current position
			self.delete(self.position, END)
		else: # set position to end so selection starts where textentry ended
			self.position = len(self.get())
		# collect hits
		_hits = []
		for element in self._completion_list:
			if element.lower().startswith(self.get().lower()): # Match case insensitively
				_hits.append(element)
		# if we have a new hit list, keep this in mind
		if _hits != self._hits:
			self._hit_index = 0
			self._hits=_hits
		# only allow cycling if we are in a known hit list
		if _hits == self._hits and self._hits:
			self._hit_index = (self._hit_index + delta) % len(self._hits)
		# now finally perform the auto completion
		if self._hits:
			self.delete(0,END)
			self.insert(0,self._hits[self._hit_index])
			self.select_range(self.position,END)

	def handle_keyrelease(self, event):
		"""event handler for the keyrelease event on this widget"""
		if event.keysym == "BackSpace":
			self.delete(self.index(INSERT), END)
			self.position = self.index(END)
		if event.keysym == "Left":
			if self.position < self.index(END): # delete the selection
				self.delete(self.position, END)
			else:
				self.position = self.position-1 # delete one character
				self.delete(self.position, END)
		if event.keysym == "Right":
			self.position = self.index(END) # go to end (no selection)
		if len(event.keysym) == 1:
			self.autocomplete()
			#self.autofill()
				
# Function for Document Translator
def GenerateTranslator(Mqueue, TMManager, from_language = 'ko', to_language = 'en', GlossaryID = "", tm_path= None,):	
	
	MyTranslator = Translator(From_Language = from_language, To_Language = to_language, GlossaryID =  GlossaryID, 
		TMManager = TMManager, PredictMode = True, ProactiveTMTranslate=True, Tool = tool_name, ToolVersion = ver_num, TMUpdate=True, )
	#MyTranslator = Translator(from_language, to_language, GlossaryID =  GlossaryID, TMManager = TMManager, TM_Path = tm_path,)
	print('Put to Queue')
	Mqueue.put(MyTranslator)

#Simple Translator
def SimpleTranslate(queue, MyTranslator, Text):
	try:
		Translated = MyTranslator.translate(Text)
		queue.put(Translated)
	except Exception as e:
		Error = ['Error to translate:' + str(e)]
		queue.put(Error)
	
#Bug Writer Get title
def TranslateTitle(qin, Text, MyTranslator):
	Translated = MyTranslator.translate(Text)
	qin.put(Translated)

#Bug Writer 
def Translate_Simple(queue, Object, simple_template, my_translator):

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
			
	translation = my_translator.translate(to_translate)

	for index in TextTestReport_index:
		New_TextTestReport.append(translation[index])

	for index in TextShouldBe_index:
		New_TextShouldBe.append(translation[index])

	for index in TextReproduceSteps_index:
		New_TextReproduceSteps.append(translation[index])	

	Lang = my_translator.To_Language
	
	if simple_template != 1:
		strReport = Simple_Row_CSS_Template(Lang, "Report", New_TextTestReport, Old_TextTestReport,)	
		strReprodSteps = Simple_Step_CSS_Template(Lang, "Reproduce Steps", New_TextReproduceSteps, Old_TextReproduceSteps, )	
		strShouldBe = Simple_Row_CSS_Template(Lang, "Should Be", New_TextShouldBe, Old_TextShouldBe, )	
	else:	
		strReport = Simple_Row_Template(Lang,  "Report", New_TextTestReport, Old_TextTestReport,)	
		strReprodSteps = Simple_Step_Template(Lang, "Reproduce Steps", New_TextReproduceSteps, Old_TextReproduceSteps, )	
		strShouldBe = Simple_Row_Template(Lang, "Should Be", New_TextShouldBe, Old_TextShouldBe, )	
		
	CssText = strTestVersion
	#print("Skip info:", self.SkipTestInfo.get())
	if skip_test_info == False:
		CssText += strTestInfo
	CssText += strReport
	CssText += strReprodSteps
	CssText += strShouldBe
	print('Copy to clipboard')
	pyperclip.copy(CssText)

	#queue.put(to_return)

def Simple_Step_CSS_Template(Lang, Title, Text_List, Text_List_Old):
		
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
	else:
		for row in Text_List_Old:
			Details += '\r\n<p><b>'+ str(x) + ')</b>&nbsp;' + row + '&nbsp;</p>'
			x += 1
		Details += '\r\n================================================='
		x = 1
		for row in Text_List:
			Details += '\r\n<p><b>' + str(x) + ')</b>&nbsp;' + row + '&nbsp;</p>'
			x += 1
	Details = AddCssLayout(Title, Details)
	return Details

def Simple_Step_Template(Lang, Title, Text_List, Text_List_Old):
	
	Details = "\r\n"
	Details += Add_Style(Title)
	x = 1
	if Lang == 'ko':		
		for row in Text_List:
			Details += '\r\n' + str(x) + ') ' + row
			x += 1
		Details += '\r\n================================================='
		for row in Text_List_Old:
			Details += '\r\n' + str(x) + ') ' + row
			x += 1
	else:
		for row in Text_List_Old:
			Details += '\r\n' + str(x) + ') ' + row
			x += 1
		Details += '\r\n================================================='
		for row in Text_List:
			Details += '\r\n' + str(x) + ') ' + row
			x += 1

	return Details

def Simple_Row_CSS_Template(Lang, Title, Text_List, Text_List_Old):
	Details = ''
	if Lang == 'ko':		
		for row in Text_List:
			Details += '\r\n<p>'+ row + '&nbsp;</p>'
		Details += '\r\n================================================='
		for row in Text_List_Old:
			Details += '\r\n<p>' + row + '&nbsp;</p>'
	else:
		for row in Text_List_Old:
			Details += '\r\n<p>'+ row + '&nbsp;</p>'
		Details += '\r\n================================================='
		for row in Text_List:
			Details += '\r\n<p>' + row + '&nbsp;</p>'
	
	Details = AddCssLayout(Title, Details)
	return Details

def Simple_Row_Template(Lang, Title, Text_List, Text_List_Old):
	Details = "\r\n"
	Details += Add_Style(Title)
	if Lang == 'ko':		
		for row in Text_List:
			Details += '\r\n'+ row
		Details += '\r\n================================================='
		for row in Text_List_Old:
			Details += '\r\n'+ row
	else:
		for row in Text_List_Old:
			Details += '\r\n'+ row
		Details += '\r\n================================================='
		for row in Text_List:
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

def MainLoop():
	report_queue = Queue()
	step_queue = Queue()
	info_queue = Queue()
	title_queue = Queue()
	csscode_queue = Queue()
	MyTranslator = Queue()
	MyDB = Queue()
	ReturnedText = Queue()
	MyManager = Manager()
	TMManager = MyManager.list()

	root = Tk()

	style = Style(root)
	style.map('Treeview', foreground=fixed_map(style, 'foreground'), background=fixed_map(style, 'background'))
	#root.geometry("400x350+300+300")
	
	try:
		MyTranslatorHelper(root, report_queue, step_queue, info_queue, title_queue, csscode_queue, ReturnedText, MyTranslator, MyDB, TMManager = TMManager,)
		root.mainloop()
	except Exception as e:
		
		root.withdraw()

		try:
			from google.cloud import logging
			AppConfig = ConfigLoader()
			Configuration = AppConfig.Config
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Configuration['License_File']['path']
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

	MainLoop()