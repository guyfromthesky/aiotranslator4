#System variable and io handling
import sys, getopt
import os
import string
import re

import configparser
#Regular expression handling
import copy
import multiprocessing
#from multiprocessing import Process, Queue, Pool
from multiprocessing import Process , Queue, Manager
import queue 

from urllib.parse import urlparse

import subprocess
#Get timestamp
import time
from datetime import datetime
#function difination
import codecs
import pyperclip
import base64
import pickle
import unicodedata

#from urllib.parse import urlparse

#GUI
from tkinter.ttk import Entry, Combobox, Label, Treeview, Scrollbar
from tkinter.ttk import Radiobutton, Checkbutton, Button
from tkinter.ttk import Progressbar, Style

from tkinter import Tk, Frame
from tkinter import Menu, filedialog, messagebox, ttk
from tkinter import Text
from tkinter import IntVar, StringVar
from tkinter import W, E, S, N, END, RIGHT, HORIZONTAL
from tkinter import WORD, NORMAL, ACTIVE, INSERT
from tkinter import DISABLED

from tkinter import colorchooser
from tkinter import scrolledtext 
from tkinter import simpledialog


import webbrowser

from libs.aiotranslator_v2 import Translator
from libs.aiotranslator_v2 import ver_num as TranslatorVersion
from libs.aioconfigmanager import ConfigLoader
from libs.documentprocessing import translateDocx, translateDPF, translateMsg
from libs.documentprocessing import TranslatePresentation, translateWorkbook
from libs.documentprocessing import ShowProgress

from google.cloud import logging
import json

ToolDisplayName = "Document Translator"
tool_name = 'document'
rev = 4000

a,b,c,d = list(str(rev))
VerNum = a + '.' + b + '.' + c + chr(int(d)+97)

version = ToolDisplayName  + " " +  VerNum + " | " + "Translator lib " + TranslatorVersion

DELAY1 = 20
StatusLength = 120



#**********************************************************************************
# UI handle ***********************************************************************
#**********************************************************************************

class DocumentTranslator(Frame):
	def __init__(self, Root, ProcessQueue = None, ResultQueue = None, StatusQueue = None,
	MyTranslatorQueue = None, MyDB_Queue = None, MyTranslatorAgent = None, TMManager = None, ):
		
		Frame.__init__(self, Root) 
		#super().__init__()
		self.parent = Root 

		# Queue
		self.ProcessQueue = ProcessQueue
		self.ResultQueue = ResultQueue
		self.StatusQueue = StatusQueue
		self.MyTranslator_Queue = MyTranslatorQueue
		self.MyDB_Queue = MyDB_Queue
		self.TMManager = TMManager
		# Translator Class
		self.MyTranslator = None
		self.MyTranslatorAgent = MyTranslatorAgent
		
		self.Usage = 0

		self.Options = {}

		# Temporary Data
		self.ListFile = []
		# Tool option
		self.SourcePatch = ""
		self.LastDocument = ""
		self.ShallowMode = ""
		self.SourceLanguage = ""
		self.Translator = ""
		self.TurboMode = ""
		self.to_language = ""
		self.from_language = ""
		self.Shallow = True	
		self.AppLanguage = "en"
		
		self.GlossaryList = []

		self.My_DB = None

		self.ButtonWidth = 20
		self.HalfButtonWidth = 15

		self.LanguagePack = {}
		self.init_App_Setting()

		if self.AppLanguage != 'kr':
			from libs.languagepack import LanguagePackEN as LanguagePack
		else:
			from libs.languagepack import LanguagePackKR as LanguagePack

		self.LanguagePack = LanguagePack
	
		# Init function
		self.initUI()
		
		self.init_UI_setting()

		#Create Translator
		if self.LicensePath.get() != "":
			self.GenerateTranslatorEngine()
		else:
			self.Error('No license selected, please select the key in Translate setting.')	

	# UI init
	def initUI(self):
		#print('Current app language: ', self.AppLanguage)
		#if self.AppLanguage != 'kr':
		#	from languagepack import LanguagePackEN as LanguagePack
		#else:
		#	from languagepack import LanguagePackKR as LanguagePack


		self.parent.resizable(False, False)
		self.parent.title(version)
		
		# Creating Menubar 
		self.Generate_Menu_UI()
		self.Generate_Tab_UI()
		
		
		#**************New row#**************#
		self.Notice = StringVar()
		self.Debug = StringVar()
		self.Progress = StringVar()
		
		self.Generate_MainTab_UI(self.MainTab)
		self.Generate_TranslateSetting_UI(self.TranslateSetting)
		#self.Generate_Excel_Option_UI(self.ExcelSetting)
		self.Generate_Utility_UI(self.Utility)
		#self.Generate_Comparison_UI(self.Comparison)
		
		self.Generate_TM_Manager_UI(self.TM_Manager)
		self.Generate_DB_Uploader_UI(self.DB_Uploader)
		self.Generate_Debugger_UI(self.Process)

		#self.init_App_Setting()
		
	def Generate_MainTab_UI(self, Tab):
		Row=1
		Label(Tab, textvariable=self.Progress, width= 40).grid(row=Row, column=1, columnspan=3, padx=5, pady=5, sticky=W)
		Label(Tab, textvariable=self.Notice, justify=RIGHT).grid(row=Row, column=3, columnspan=8, padx=5, pady=5, sticky= E)

		#**************New row#**************#
		Row+=1
		# Translator
		
		# Target language
		Label(Tab, text=  self.LanguagePack.Label['Language'], width= 10, font='calibri 11 bold').grid(row=Row, column=1, padx=5, pady=5, sticky=W)
		self.Language = IntVar()	
		Radiobutton(Tab, width= 10, text=  self.LanguagePack.Option['Hangul'], value=1, variable=self.Language).grid(row=Row, column=2, padx=0, pady=5, sticky=W)
		Radiobutton(Tab, width= 10, text=  self.LanguagePack.Option['English'], value=2, variable=self.Language).grid(row=Row, column=3, padx=0, pady=5, sticky=W)

				
		Label(Tab, text= self.LanguagePack.Label['ProjectKey']).grid(row=Row, column=4, padx=5, pady=5, sticky=W)
		self.Text_glossary_id = AutocompleteCombobox(Tab)
		self.Text_glossary_id.Set_Entry_Width(20)
		
		self.Text_glossary_id.set_completion_list([])

		if self.glossary_id != None:
			self.Text_glossary_id.set(self.glossary_id )

		self.Text_glossary_id.grid(row=Row, column=5, columnspan=2, padx=5, pady=5, stick=W)
		self.Text_glossary_id.bind("<<ComboboxSelected>>", self.SaveProjectKey)

		#Label(Tab, text=  self.LanguagePack.Label['Translator'], width= 10, font='calibri 11 bold').grid(row=Row, column=4, padx=10, pady=5, sticky=W)
		#self.TranslatorAgent = IntVar()	
		#Radiobutton(Tab, width= 10, text=  self.LanguagePack.Option['Google'], value=1, variable=self.TranslatorAgent, command = self.SetTranslatorAgent).grid(row=Row, column=5, padx=0, pady=5, sticky=W)
		#Radiobutton(Tab, width= 10, text=  self.LanguagePack.Option['Kakao'], value=2, variable=self.TranslatorAgent, command = self.SetTranslatorAgent).grid(row=Row, column=6, padx=0, pady=5, sticky=W)
		#self.TranslatorAgent.set(1)
		
		Button(Tab, width = 20, text=  self.LanguagePack.Button['RenewDatabase'], command= self.RenewMyTranslator).grid(row=Row, column=7, columnspan=2, padx=5, pady=5, sticky=E)
		Button(Tab, width = 20, text=  self.LanguagePack.Button['OpenOutput'], command= self.OpenOutput).grid(row=Row, column=9, columnspan=1, padx=5, pady=5, sticky=E)

		#**************New row#**************#
		Row+=1
		Label(Tab, width= 10, text=  self.LanguagePack.Label['Source'], font='calibri 11 bold').grid(row=Row, column=1, padx=5, pady=5, sticky=W)
		self.CurrentSourceFile = StringVar()
		self.TextFilePath = Entry(Tab,width = 120, text= self.LanguagePack.ToolTips['SelectSource'], state="readonly", textvariable=self.CurrentSourceFile)
		self.TextFilePath.grid(row=Row, column=2, columnspan=7, padx=5, pady=5, sticky=E)
		Button(Tab, width = 20, text=  self.LanguagePack.Button['Browse'], command= self.BtnLoadDocument).grid(row=Row, column=9, columnspan=1, padx=5, pady=5, sticky=E)
		
		Row += 1
		Label(Tab, text=  self.LanguagePack.Label['ToolOptions']).grid(row=Row, column=1, padx=5, pady=5, sticky= W)
		Label(Tab, text= self.LanguagePack.Label['TMOptions']).grid(row=Row, column=3, columnspan=2, padx=5, pady=5, sticky=W)
		Label(Tab, text= self.LanguagePack.Label['TranslateOptions']).grid(row=Row, column=5, columnspan=2, padx=5, pady=5, sticky=W)
		Label(Tab, text= self.LanguagePack.Label['OtherOptions']).grid(row=Row, column=7, columnspan=2, padx=5, pady=5, sticky=W)

		Row += 1
		self.TranslateFileName = IntVar()
		TranslateFileNameBtn = Checkbutton(Tab, text=  self.LanguagePack.Option['TranslateFileName'], variable = self.TranslateFileName)
		TranslateFileNameBtn.grid(row=Row, column=1, columnspan=2,padx=5, pady=5, sticky=W)
		TranslateFileNameBtn.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['TranslateFileName']))
		self.TranslateFileName.set(1)

		self.TMUpdate = IntVar()
		TMUpdateBtn = Checkbutton(Tab, text=  self.LanguagePack.Option['UpdateTMFile'], variable = self.TMUpdate)
		TMUpdateBtn.grid(row=Row, column=3, columnspan=2,padx=0, pady=5, sticky=W)
		TMUpdateBtn.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['UpdateTMFile'])) 
		self.TMUpdate.set(1)

		self.DataOnly = IntVar()
		DataOnlyBtn = Checkbutton(Tab, text=  self.LanguagePack.Option['DataOnly'], variable = self.DataOnly)
		DataOnlyBtn.grid(row=Row, column=5,padx=0, pady=5, sticky=W)
		DataOnlyBtn.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['DataOnly'])) 


		Row+=1

		self.TranslateSheetName = IntVar()
		TranslateSheetNameBtn = Checkbutton(Tab, text=  self.LanguagePack.Option['TranslateSheetName'], variable = self.TranslateSheetName)
		TranslateSheetNameBtn.grid(row=Row, column=1, columnspan=2,padx=5, pady=5, sticky=W)	
		TranslateSheetNameBtn.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['TranslateSheetName']))
		self.TranslateSheetName.set(1)

		self.TMTranslate = IntVar()
		TMTranslateBtn = Checkbutton(Tab, text=  self.LanguagePack.Option['TMTranslate'], variable = self.TMTranslate, command=self.TMTranslateModeToggle)
		TMTranslateBtn.grid(row=Row, column=3, columnspan=2, padx=0, pady=5, sticky=W)
		TMTranslateBtn.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['TMTranslate']))
		self.TMTranslate.set(1)

		self.TurboTranslate = IntVar()
		TurboTranslateBtn = Checkbutton(Tab, text=  self.LanguagePack.Option['TurboTranslate'], variable = self.TurboTranslate)
		TurboTranslateBtn.grid(row=Row, column=5,padx=0, pady=5, sticky=W)
		TurboTranslateBtn.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['TurboTranslate']))

		Row+=1

		self.FixCorruptFileName = IntVar()
		FixCorruptFileNameBtn = Checkbutton(Tab, text=  self.LanguagePack.Option['CorruptFileName'], variable = self.FixCorruptFileName)
		FixCorruptFileNameBtn.grid(row=Row, column=1, columnspan=2,padx=5, pady=5, sticky=W)	
		FixCorruptFileNameBtn.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['FixCorruptedName']))
		self.FixCorruptFileName.set(1)	

		self.SheetRemoval = IntVar() 
		SheetRemoveBtn = Checkbutton(Tab, text=  self.LanguagePack.Option['SheetRemoval'], variable = self.SheetRemoval)
		SheetRemoveBtn.grid(row=Row, column=5, columnspan=2,padx=0, pady=5, sticky=W)
		SheetRemoveBtn.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['SheetRemoval']))
		Row+=1

		Label(Tab, text="Sheet: ").grid(row=Row, column=1, padx=5, pady=5, sticky=W)
		self.SheetList = Text(Tab, width = 110, height=1) #
		self.SheetList.grid(row=Row, column=2, columnspan=8, padx=5, pady=5, sticky=E)

		Row+=1
		self.progressbar = Progressbar(Tab, orient=HORIZONTAL, length=1000,  mode='determinate')
		self.progressbar["maximum"] = 1000
		self.progressbar.grid(row=Row, column=1, columnspan=9, padx=5, pady=5, sticky=W)
		
		Row+=1
		DictionaryLabel = Label(Tab, text=  self.LanguagePack.Label['Dictionary'])
		DictionaryLabel.grid(row=Row, column=1, padx=5, pady=5, sticky=W)
		#Label(Tab, text='Version').grid(row=Row, column=1, padx=5, pady=5, sticky=W)
		Label(Tab, textvariable=self.VersionStatus).grid(row=Row, column=2, padx=0, pady=5)
		self.VersionStatus.set('-')

		#Label(Tab, text='Update').grid(row=Row, column=3, padx=5, pady=5)
		Label(Tab, textvariable=self.UpdateDay).grid(row=Row, column=3, padx=0, pady=5)
		self.VersionStatus.set('-')

		#DictionaryLabel = Label(Tab, text=  self.LanguagePack.Label['Dictionary'])
		#DictionaryLabel.grid(row=Row, column=4, padx=5, pady=5, sticky=W)
		Label(Tab, width= 10, textvariable=self.DictionaryStatus).grid(row=Row, column=4, padx=0, pady=5)
		self.DictionaryStatus.set('-')

		TMLabel=Label(Tab, text=  self.LanguagePack.Label['TM'])
		TMLabel.grid(row=Row, column=5, padx=5, pady=5, sticky=W)
		TMLabel.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['FilePath'] + self.TMPath.get()))
		Label(Tab, width= 10, textvariable=self.TMStatus).grid(row=Row, column=6, padx=0, pady=5, sticky=W)
		self.TMStatus.set('-')


		Button(Tab, width = 20, text=  self.LanguagePack.Button['Stop'], command= self.Stop).grid(row=Row, column=7, columnspan=2,padx=0, pady=5)	
		self.TranslateBtn = Button(Tab, width = 20, text=  self.LanguagePack.Button['Translate'], command= self.Translate, state=DISABLED)
		self.TranslateBtn.grid(row=Row, column=9, columnspan=1, padx=5, pady=0, sticky=E)


	def Generate_TranslateSetting_UI(self, Tab):
		Row = 1
		Label(Tab, text= self.LanguagePack.Label['LicensePath']).grid(row=Row, column=1, padx=5, pady=5, sticky=W)
		self.TextLicensePath = Entry(Tab,width = 120, state="readonly", textvariable=self.LicensePath)
		self.TextLicensePath.grid(row=Row, column=3, columnspan=5, padx=5, pady=5, sticky=W)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Browse'], command= self.Btn_Select_License_Path).grid(row=Row, column=8, columnspan=2, padx=5, pady=5, sticky=E)

		
		#Row += 1
		#Label(Tab, width = 30, text= self.LanguagePack.Label['DBSourcePath']).grid(row=Row, column=1, columnspan=2, padx=5, pady=5, sticky=W)
		#self.TextFilePath = Entry(Tab, width = 120, text="Select your document", state="readonly", textvariable=self.DictionaryPath.get())
		#self.TextFilePath.grid(row=Row, column=3, columnspan=7, padx=5, pady=5, sticky=W)
		##Button(Tab, width = 20, text=  self.LanguagePack.Button['Browse'], command= self.BtnLoadDocument).grid(row=Row, column=9, columnspan=2, padx=5, pady=5, sticky=E)
		#Button(Tab, width = self.HalfButtonWidth, text= self.LanguagePack.Button['Save'], command= self.SaveProjectKey).grid(row=Row, column=8, columnspan=2, padx=5, pady=5, sticky=E)

	def Generate_Utility_UI(self, Tab):
		# Utility option
		Row = 1
		Label(Tab, textvariable=self.Notice).grid(row=Row, column=1, columnspan = 10, padx=5, pady=5, sticky= W)
		#Row += 1
		#self.DocxCompare = IntVar()
		#DocxCompareBtn = Checkbutton(Tab, text=  self.LanguagePack.Option['DocxCompare'], variable = self.DocxCompare, command= None)
		#DocxCompareBtn.grid(row=Row, column=1,padx=5, pady=5, sticky=W)
		#DocxCompareBtn.bind("<Enter>", lambda event : self.Notice.set(self.LanguagePack.ToolTips['TMPrepare']))
		#self.DocxCompare.set(0)
		
		Row += 1
		self.RawTMSource = StringVar()
		Label(Tab, text=  self.LanguagePack.Label['FixTM']).grid(row=Row, column=1, columnspan=2, padx=5, pady=5, sticky= W)
		self.TextRawTMPath = Entry(Tab,width = 100, state="readonly", textvariable=self.RawTMSource)
		self.TextRawTMPath.grid(row=Row, column=3, columnspan=4, padx=4, pady=5, sticky=W)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Browse'], command= self.BtnLoadRawTM).grid(row=Row, column=7, columnspan=2, padx=5, pady=5, sticky=E)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Execute'], command= self.BtnOptimizeTM).grid(row=Row, column=9, columnspan=2,padx=5, pady=5, sticky=W)
	
		Row += 1
		self.RawSource = StringVar()
		Label(Tab, text=  self.LanguagePack.Label['OptimizeDatafile']).grid(row=Row, column=1, columnspan=2, padx=5, pady=5, sticky= W)
		self.TextRawSourcePath = Entry(Tab,width = 100, state="readonly", textvariable=self.RawSource)
		self.TextRawSourcePath.grid(row=Row, column=3, columnspan=5, padx=5, pady=5, sticky=W)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Browse'], command= self.BtnLoadRawSource).grid(row=Row, column=8, columnspan=2, padx=5, pady=5, sticky=E)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Execute'], command= self.BtnOptimizeXLSX).grid(row=Row, column=10, columnspan=2,padx=5, pady=5, sticky=W)
		'''
		Row += 1
		self.TMSource = StringVar()
		Label(Tab, text=  self.LanguagePack.Label['MergeTM']).grid(row=Row, column=1, columnspan=2, padx=5, pady=5, sticky= W)
		self.TextTMSourcePath = Entry(Tab,width = 100, state="readonly", textvariable=self.TMSource)
		self.TextTMSourcePath.grid(row=Row, column=3, columnspan=5, padx=5, pady=5, sticky=W)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Browse'], command= self.BtnBrowseTMSource).grid(row=Row, column=8, columnspan=2, padx=5, pady=5, sticky=E)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Save'], command= self.BtnMergeTM).grid(row=Row, column=10, columnspan=2,padx=5, pady=5, sticky=W)		
		'''

	def Generate_Debugger_UI(self, Tab):	

		Row = 1
		#self.Debugger = Text(Tab, width=120, height=20, undo=True, wrap=WORD)
		self.Debugger = scrolledtext.ScrolledText(Tab, width=125, height=19, undo=True, wrap=WORD, )
		self.Debugger.grid(row=Row, column=1, columnspan=20, padx=5, pady=5)

	def Generate_TM_Manager_UI(self, Tab):
		self.pair_list = []
		self.removed_list = []
		Max_Size = 10
		Row = 1
		Label(Tab, width = 100, text= "").grid(row=Row, column=1, columnspan=Max_Size, padx=5, pady=5, sticky = (N,S,W,E))
		Row += 1
		self.search_text = Text(Tab, width = (125- self.HalfButtonWidth*3), height=1) #
		self.search_text.grid(row=Row, column=1, columnspan=Max_Size-4, padx=5, pady=5, stick=W)

		#self.search_text.bind("<Enter>", self.search_tm_event)

		print('Btn size', self.HalfButtonWidth)
		Button(Tab, text= self.LanguagePack.Button['Load'], width= self.HalfButtonWidth, command= self.load_tm_list).grid(row=Row, column=Max_Size-3, sticky=E)
		Button(Tab, text= self.LanguagePack.Button['Save'], width= self.HalfButtonWidth, command= self.save_tm).grid(row=Row, column=Max_Size-2, sticky=E)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Search'] , command= self.search_tm_list).grid(row=Row, column=Max_Size-1,sticky=E)
		Row +=1
		#self.Debugger = Text(Tab, width=120, height=20, undo=True, wrap=WORD)
		#self.List = scrolledtext.ScrolledText(Tab, width=125, height=20, undo=True, wrap=WORD, )
		#self.List.grid(row=Row, column=1, columnspan=5, padx=5, pady=5)
		#style = Style()
		#style.configure('Treeview', background ="silver", foreground = "black")
		#style.map('Treeview', background = [('seleted', 'green')])
		
		self.Treeview = Treeview(Tab)
		self.Treeview.grid(row=Row, column=1, columnspan=Max_Size, padx=5, pady=5, sticky = (N,S,W,E))
		verscrlbar = Scrollbar(Tab, orient ="vertical", command = self.Treeview.yview)
		#verscrlbar.pack(side ='right', fill ='x') 
		self.Treeview.configure(  yscrollcommand=verscrlbar.set)

		self.Treeview.Scrollable = True
		self.Treeview['columns'] = ('status')
		#self.Treeview.heading("#0", text='Hangul', anchor='w')
		self.Treeview.heading("#0", text='Hangul')
		#self.Treeview.column("#0", anchor="w")
		self.Treeview.column("#0", anchor='center', width=500)
		self.Treeview.heading('status', text='English')
		self.Treeview.column('status', anchor='center', width=500)

		self.Treeview.tag_configure('pass', background= 'green')
		self.Treeview.tag_configure('fail', background= 'red')
		self.Treeview.tag_configure('na', background= '')

		
		
		verscrlbar.grid(row=Row, column=Max_Size,  sticky = (N,S,E))
		Tab.grid_columnconfigure(Max_Size, weight=0, pad=0)
		styles = Style()
		styles.configure('Treeview',rowheight=22)

		self.Treeview.bind("<Delete>", self.Delete_Line)	
		self.Treeview.bind("<Double-1>", self.DoubleRightClick)	

		
		#Row +=1
		#self.Debugger = scrolledtext.ScrolledText(Tab, width=125, height=6, undo=True, wrap=WORD, )
		#self.Debugger.grid(row=Row, column=1, columnspan=Max_Size, padx=5, pady=5, sticky = (N,S,W,E))

	def Generate_DB_Uploader_UI(self, Tab):
		
		Row =1
		self.Str_DB_Path = StringVar()
		#self.Str_DB_Path.set('C:\\Users\\evan\\OneDrive - NEXON COMPANY\\[Demostration] V4 Gacha test\\DB\\db.xlsx')
		Label(Tab, text=  self.LanguagePack.Label['MainDB']).grid(row=Row, column=1, columnspan=2, padx=5, pady=5, sticky= W)
		self.Entry_Old_File_Path = Entry(Tab,width = 130, state="readonly", textvariable=self.Str_DB_Path)
		self.Entry_Old_File_Path.grid(row=Row, column=3, columnspan=6, padx=4, pady=5, sticky=E)
		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Browse'], command= self.Btn_DB_Uploader_Browse_DB_File).grid(row=Row, column=9, columnspan=2, padx=5, pady=5, sticky=E)
		
		Row += 1
		Label(Tab, text= self.LanguagePack.Label['ProjectKey']).grid(row=Row, column=1, padx=5, pady=5, sticky=W)
		
		self.ProjectList = AutocompleteCombobox(Tab)
		self.ProjectList.Set_Entry_Width(30)
		self.ProjectList.set_completion_list([])
		if self.glossary_id != None:
			self.ProjectList.set(self.glossary_id)

		self.ProjectList.grid(row=Row, column=3, columnspan=2, padx=5, pady=5, stick=W)

		Button(Tab, width = self.HalfButtonWidth, text=  self.LanguagePack.Button['Execute'], command= self.Btn_DB_Uploader_Execute_Script).grid(row=Row, column=9, columnspan=2,padx=5, pady=5, sticky=E)

		Row += 1
		self.Debugger = Text(Tab, width=125, height=14, undo=True, wrap=WORD, )
		self.Debugger.grid(row=Row, column=1, columnspan=10, padx=5, pady=5, sticky=W+E+N+S)


	def search_tm_event(self, event):
		self.search_tm_list()

	def Delete_Line(self, event):
		focused = self.Treeview.focus()
		child = self.Treeview.item(focused)
		text = child["text"]
		try:
			index = self.MyTranslator.KO.index(text)
			print('Item to remove: ' + self.MyTranslator.KO[index] + " " + self.MyTranslator.EN[index])
			self.removed_list.append(index)
			self.MyTranslator.KO[index] = None
			self.MyTranslator.EN[index] = None
		except Exception as e:
			print('Error:', e)	
		print(child["text"])
		self.Treeview.delete(focused)
		#self.save_app_config()

	def DoubleRightClick(self, event):
		focused = self.Treeview.focus()
		child = self.Treeview.item(focused)
		self.Debugger.insert("end", "\n")
		self.Debugger.insert("end", 'Korean: ' + str(child["text"]))
		self.Debugger.insert("end", "\n")
		self.Debugger.insert("end", 'English: ' + str(child["values"][0]))
		self.Debugger.yview(END)
		#self.pair_list.delete("1.0", END)
		#self.pair_list.insert("end", text)
		#print(child)

	def load_tm_list(self):
		self.remove_treeview()
		tm_size = len(self.MyTranslator.EN)
		print('Total TM:', tm_size)
		for i in range(tm_size):
			en_str = self.MyTranslator.EN[i]
			ko_str = self.MyTranslator.KO[i]
			if ko_str != None:
				#print("Pair:", ko_str, en_str)
				try:
					self.Treeview.insert('', 'end', text= str(ko_str), values=([str(en_str)]))
					#print('Inserted id:', id)
				except:
					pass	
	
	def search_tm_list(self):
		text = self.search_text.get("1.0", END).replace("\n", "").replace(" ", "")
		self.remove_treeview()
		print("Text to search: ", text)
		if text != None:
			tm_size = len(self.MyTranslator.EN)
			for i in range(tm_size):
				en_str = self.MyTranslator.EN[i]
				ko_str = self.MyTranslator.KO[i]
				if text in en_str or text in ko_str:
					if ko_str != None:
						#print("Pair:", ko_str, en_str)
						try:
							self.Treeview.insert('', 'end', text= str(ko_str), values=([str(en_str)]))
							#print('Inserted id:', id)
						except:
							pass	

	def remove_treeview(self):
		for i in self.Treeview.get_children():
			self.Treeview.delete(i)
	

	def save_tm(self):
		print('Saving config')
		self.MyTranslator.remove_tm_pair(self.removed_list)
		UpdateProcess = Process(target=self.MyTranslator.remove_tm_pair, args=(self.removed_list,))
		UpdateProcess.start()
		self.removed_list = []

	def Generate_Menu_UI(self):
		menubar = Menu(self.parent) 
		# Adding File Menu and commands 
		file = Menu(menubar, tearoff = 0)
		# Adding Load Menu 
		menubar.add_cascade(label =  self.LanguagePack.Menu['File'], menu = file) 
		file.add_command(label =  self.LanguagePack.Menu['SaveSetting'], command = self.save_app_config) 
		#file.add_command(label =  self.LanguagePack.Menu['LoadException'], command = self.SelectException) 
		file.add_separator() 
		file.add_command(label =  self.LanguagePack.Menu['LoadTM'], command = self.SelectTM) 
		file.add_command(label =  self.LanguagePack.Menu['CreateTM'], command = self.SaveNewTM)
		file.add_separator() 
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

	def Generate_Tab_UI(self):
		TAB_CONTROL = ttk.Notebook(self.parent)
		#Tab1
		self.MainTab = ttk.Frame(TAB_CONTROL)
		TAB_CONTROL.add(self.MainTab, text=  self.LanguagePack.Tab['Main'])
		#Tab2
		self.TranslateSetting = ttk.Frame(TAB_CONTROL)
		TAB_CONTROL.add(self.TranslateSetting, text=  self.LanguagePack.Tab['Translator'])
		#Tab3
		#self.ExcelSetting = ttk.Frame(TAB_CONTROL)
		#TAB_CONTROL.add(self.ExcelSetting, text=  self.LanguagePack.Tab['Excel'])
		#Tab4
		self.Utility = ttk.Frame(TAB_CONTROL)
		TAB_CONTROL.add(self.Utility, text=  self.LanguagePack.Tab['Utility'])
		#Tab5
		#self.Comparison = ttk.Frame(TAB_CONTROL)
		#TAB_CONTROL.add(self.Comparison, text=  self.LanguagePack.Tab['Comparison'])
		#Tab6
		self.TM_Manager = ttk.Frame(TAB_CONTROL)
		TAB_CONTROL.add(self.TM_Manager, text=  self.LanguagePack.Tab['TMManager'])

		self.DB_Uploader = ttk.Frame(TAB_CONTROL)
		TAB_CONTROL.add(self.DB_Uploader, text=  self.LanguagePack.Tab['DBUploader'])

		self.Process = ttk.Frame(TAB_CONTROL)
		TAB_CONTROL.add(self.Process, text=  self.LanguagePack.Tab['Debug'])

		TAB_CONTROL.pack(expand=1, fill="both")


	# Menu Function
	def About(self):
		messagebox.showinfo("About....", "Creator: Giang\r\nUI/UX Improve: Ally")

	def Error(self, ErrorText):
		messagebox.showinfo('Tool error...', ErrorText)	

	def SaveAppLanguage(self, language):
		self.Notice.set(self.LanguagePack.ToolTips['AppLanuageUpdate'] + " "+ language) 
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'app_lang', language)

	def save_app_config(self):
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'target_lang', self.Language.get())
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'speed_mode', self.TurboTranslate.get())
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'value_only', self.DataOnly.get())
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'file_name_correct', self.TranslateFileName.get())
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'file_name_translate', self.TranslateFileName.get())
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'sheet_name_translate', self.TranslateSheetName.get())
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'tm_translate', self.TMTranslate.get())
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'tm_update', self.TMUpdate.get())
		self.AppConfig.Save_Config(self.AppConfig.Doc_Config_Path, 'Document_Translator', 'remove_unselected_sheet', self.SheetRemoval.get())


	def SetLanguageKorean(self):
		self.AppLanguage = 'kr'
		self.SaveAppLanguage(self.AppLanguage)
		#self.initUI()
	
	def SetLanguageEnglish(self):
		self.AppLanguage = 'en'
		self.SaveAppLanguage(self.AppLanguage)
		#self.initUI()

	def OpenWeb(self):
		webbrowser.open_new(r"https://confluence.nexon.com/display/NWMQA/AIO+Translator")

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

	def SelectDictionary(self):
		filename = filedialog.askopenfilename(title = "Select Database file",filetypes = (("Dictionary files","*.xlsx *.xlsm"), ), )	
		if filename != "":
			NewDictionary = self.CorrectPath(filename)	
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'Database', 'path', NewDictionary, True)
			self.Notice.set(self.LanguagePack.ToolTips['DocumentLoaded'])
		else:
			self.Notice.set(self.LanguagePack.ToolTips['SourceDocumentEmpty'])

	def Btn_Select_License_Path(self):
		filename = filedialog.askopenfilename(title =  self.LanguagePack.ToolTips['SelectDB'],filetypes = (("JSON files","*.json" ), ), )	
		if filename != "":
			LicensePath = self.CorrectPath(filename)
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'license_file', 'path', LicensePath, True)
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = LicensePath
			self.LicensePath.set(LicensePath)
		else:
			self.Notice.set("No file is selected")


	def SelectTM(self):
		filename = filedialog.askopenfilename(title = "Select Translation Memory file", filetypes = (("TM files","*.pkl"), ),)
		if filename != "":
			NewTM = self.CorrectPath(filename)
			self.TMPath.set(NewTM)
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'translation_memory', 'path', NewTM, True)
			self.RenewMyTranslator()
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
			with open(NewTM, 'wb') as pickle_file:
				pickle.dump([], pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
			self.TMPath.set(NewTM)
			self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'translation_memory', 'path', NewTM, True)
			self.RenewMyTranslator()

	def SaveProjectKey(self, event):
		glossary_id = self.Text_glossary_id.get()
		glossary_id = glossary_id.replace('\n', '')
		self.AppConfig.Save_Config(self.AppConfig.Translator_Config_Path, 'glossary_id', 'value', glossary_id)
		self.MyTranslator.glossary_id = glossary_id
		
		self.RenewMyTranslator()

	def OpenOutput(self):
		Source = self.ListFile[0]
		Outputdir = os.path.dirname(Source)
		BasePath = str(os.path.abspath(Outputdir))
		subprocess.Popen('explorer ' + BasePath)
		
	def BtnLoadDocument(self):
		filename = filedialog.askopenfilename(title =  self.LanguagePack.ToolTips['SelectSource'],filetypes = (("All type files","*.docx *.xlsx *.xlsm *.pptx *.msg"), ("Workbook files","*.xlsx *.xlsm"), ("Document files","*.docx"), ("Presentation files","*.pptx"), ("Email files","*.msg"), ("PDF files","*.pdf")), multiple = True)	
		if filename != "":
			self.ListFile = list(filename)
			self.CurrentSourceFile.set(str(self.ListFile[0]))
			self.Notice.set(self.LanguagePack.ToolTips['SourceSelected'])
		else:
			self.Notice.set(self.LanguagePack.ToolTips['SourceDocumentEmpty'])
		return

	def BtnLoadRawSource(self):
		#filename = filedialog.askopenfilename(title =  self.LanguagePack.ToolTips['SelectSource'],filetypes = (("Workbook files","*.xlsx *.xlsm *xlsb"), ("Document files","*.docx")), multiple = True)	
		FolderName = filedialog.askdirectory(title =  self.LanguagePack.ToolTips['SelectSource'])	
		if FolderName != "":
			self.RawFile = FolderName
			self.RawSource.set(str(FolderName))
			
			self.Notice.set(self.LanguagePack.ToolTips['SourceSelected'])
		else:
			self.Notice.set(self.LanguagePack.ToolTips['SourceDocumentEmpty'])
		return

	def BtnLoadRawTM(self):
		filename = filedialog.askopenfilename(title =  self.LanguagePack.ToolTips['SelectSource'],filetypes = (("TM file","*.pkl"),), multiple = True)	
		if filename != "":
			self.RawTMFile = list(filename)
			Display = self.CorrectPath(self.RawTMFile[0])
			self.RawTMSource.set(Display)
			
			self.Notice.set(self.LanguagePack.ToolTips['SourceSelected'])
		else:
			self.Notice.set(self.LanguagePack.ToolTips['SourceDocumentEmpty'])
		return
	

###########################################################################################
# DB UPLOADER 
###########################################################################################

	def Btn_DB_Uploader_Browse_DB_File(self):
			
		filename = filedialog.askopenfilename(title =  self.LanguagePack.ToolTips['SelectSource'],filetypes = (("Workbook files", "*.xlsx *.xlsm"), ), multiple = False)	
		if filename != "":
			self.DB_Path = self.CorrectPath(filename)
			self.Str_DB_Path.set(self.DB_Path)
			self.Notice.set(self.LanguagePack.ToolTips['SourceSelected'])
		else:
			self.Notice.set(self.LanguagePack.ToolTips['SourceDocumentEmpty'])
		return

	def Btn_Browse_Glossary_File(self):
			
		filename = filedialog.askopenfilename(title =  self.LanguagePack.ToolTips['SelectSource'],filetypes = (("Workbook files", "*.svg"), ), multiple = False)	
		if filename != "":
			self.DB_Path = self.CorrectPath(filename)
			self.Str_DB_Path.set(self.DB_Path)
			self.Notice.set(self.LanguagePack.ToolTips['SourceSelected'])
		else:
			self.Notice.set(self.LanguagePack.ToolTips['SourceDocumentEmpty'])
		return

	def Btn_Execute_Creator_Script(self):
		DB = self.Str_DB_Path.get()
		glossary_id = self.Text_New_glossary_id.get()
		URI = self.Text_URI_ID.get()

		self.Automation_Processor = Process(target=Function_Execute_Create_Script, args=(self.StatusQueue, DB, glossary_id, URI,))
		self.Automation_Processor.start()
		self.after(DELAY1, self.Wait_For_Automation_Creator_Processor)	

	def Wait_For_Automation_Creator_Processor(self):
		if (self.Automation_Processor.is_alive()):
			'''
			try:
				percent = self.ProcessQueue.get(0)
				self.CompareProgressbar["value"] = percent
				self.progressbar.update()
				#self.Progress.set("Progress: " + str(percent/10) + '%')
			except queue.Empty:
				pass	
			'''
			try:
				Status = self.StatusQueue.get(0)
				if Status != None:
					self.Notice.set(Status)
					self.Debugger.insert("end", "\n\r")
					self.Debugger.insert("end", Status)
			except queue.Empty:
				pass	
			self.after(DELAY1, self.Wait_For_Automation_Creator_Processor)
		else:
			try:
				Status = self.StatusQueue.get(0)
				if Status != None:	
					self.Notice.set('Compare complete')
					print(Status)
					self.Debugger.insert("end", "\n\r")
					self.Debugger.insert("end", Status)
			except queue.Empty:
				pass
			self.Wait_For_Automation_Creator_Processor.terminate()

	def Btn_DB_Uploader_Execute_Script(self):
		DB = self.Str_DB_Path.get()
		glossary_id = self.ProjectList.get()
		
		result = self.Confirm_Popup(glossary_id, 'Are you sure you want to replace the DB of '+ glossary_id + "?")
		
		if result == True:
			
			self.Automation_Processor = Process(target=Function_Execute_Script, args=(self.StatusQueue, DB, glossary_id,))
			self.Automation_Processor.start()
			self.after(DELAY1, self.Wait_For_Automation_Processor)	

	def Wait_For_Automation_Processor(self):
		if (self.Automation_Processor.is_alive()):
			'''
			try:
				percent = self.ProcessQueue.get(0)
				self.CompareProgressbar["value"] = percent
				self.progressbar.update()
				#self.Progress.set("Progress: " + str(percent/10) + '%')
			except queue.Empty:
				pass	
			'''
			try:
				Status = self.StatusQueue.get(0)
				if Status != None:
					self.Notice.set(Status)
					self.Debugger.insert("end", "\n\r")
					self.Debugger.insert("end", Status)
			except queue.Empty:
				pass	
			self.after(DELAY1, self.Wait_For_Automation_Processor)
		else:
			try:
				Status = self.StatusQueue.get(0)
				if Status != None:	
					self.Notice.set('Compare complete')
					print(Status)
					self.Debugger.insert("end", "\n\r")
					self.Debugger.insert("end", Status)
			except queue.Empty:
				pass
			self.Automation_Processor.terminate()

	def Confirm_Popup(self, Request, Message):
		MsgBox = simpledialog.askstring(title="Input project ID", prompt="What's your Project ID?")

		if MsgBox == Request:
			return True
		else:
			return False

###########################################################################################


	def onExit(self):
		self.quit()

	def init_App_Setting(self):

		self.LicensePath = StringVar()
		self.DictionaryPath = StringVar()
		self.TMPath = StringVar()

		self.CurrentDataSource = StringVar()
		self.Notice = StringVar()
		self.DictionaryStatus = StringVar()
		
		self.TMStatus  = StringVar()
		#self.HeaderStatus = StringVar()
		self.VersionStatus  = StringVar()
		self.UpdateDay = StringVar()

		self.AppConfig = ConfigLoader()
		self.Configuration = self.AppConfig.Config
		self.AppLanguage  = self.Configuration['Document_Translator']['app_lang']
		
		self.LicensePath.set(self.Configuration['license_file']['path'])
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.Configuration['license_file']['path']

		self.TMPath.set(self.Configuration['translation_memory']['path'])
		self.glossary_id = self.Configuration['glossary_id']['value']

	def init_UI_setting(self):
		self.Language.set(self.Configuration['Document_Translator']['target_lang'])
		self.TurboTranslate.set(self.Configuration['Document_Translator']['speed_mode'])
		self.DataOnly.set(self.Configuration['Document_Translator']['value_only'])
		self.FixCorruptFileName.set(self.Configuration['Document_Translator']['file_name_correct'])
		self.TranslateFileName.set(self.Configuration['Document_Translator']['file_name_translate'])
		self.TranslateSheetName.set(self.Configuration['Document_Translator']['sheet_name_translate'])
		self.TMTranslate.set(self.Configuration['Document_Translator']['tm_translate'])
		self.TMUpdate.set(self.Configuration['Document_Translator']['tm_update'])
		self.SheetRemoval.set(self.Configuration['Document_Translator']['remove_unselected_sheet'])
		
		try:
			self.Usage = self.Configuration['Document_Translator']['usage']
		except:
			self.Usage = 0

		

	

	def RenewMyTranslator(self):
		self.MyTranslator = None
		del self.My_DB
		self.My_DB = None
		self.TranslateBtn.configure(state=DISABLED)
		self.GenerateTranslatorEngine()

	def Stop(self):
		try:
			if self.TranslatorProcess.is_alive():
				self.TranslatorProcess.terminate()
		except:
			pass
		self.progressbar["value"] = 0
		self.progressbar.update()
		self.Notice.set('Translate Process has been stop')
		return

	def GenerateTranslatorEngine(self):
		self.Notice.set(self.LanguagePack.ToolTips['AppInit'])
		if self.Language.get() == 1:
			to_language = 'ko'
			from_language = 'en'
		else:
			to_language = 'en'
			from_language = 'ko'

		self.glossary_id = self.Text_glossary_id.get()
		self.glossary_id = self.glossary_id.replace('\n', '')
		tm_path = self.TMPath.get()
		self.TranslatorProcess = Process(target=GenerateTranslator, args=(self.MyTranslator_Queue, self.TMManager, from_language, to_language, self.glossary_id, tm_path,))
		self.TranslatorProcess.start()
		self.after(DELAY1, self.GetMyTranslator)
		return

	def GetMyTranslator(self):
		try:
			st = time.time()
			self.MyTranslator = self.MyTranslator_Queue.get_nowait()
			print('Get Translator',time.time()- st)
		except queue.Empty:
			self.after(DELAY1, self.GetMyTranslator)

		#print("self.MyTranslator: ", self.MyTranslator)	
		if self.MyTranslator != None:	
			print("My translator is created")
			#self.MyTranslator.Convert_Translation_Memory()
			self.TranslateBtn.configure(state=NORMAL)

			DBLength = len(self.MyTranslator.dictionary)
			self.DictionaryStatus.set(str(DBLength))
			self.TMStatus.set(str(self.MyTranslator.translation_memory_size))

			glossary_list = [""] + self.MyTranslator.glossary_list
			self.Text_glossary_id.set_completion_list(glossary_list)
			self.ProjectList.set_completion_list(glossary_list)

			if self.glossary_id in self.MyTranslator.glossary_list:
				self.Text_glossary_id.set(self.glossary_id)
				self.ProjectList.set(self.glossary_id)
			else:
				self.Text_glossary_id.set("")
				self.ProjectList.set(self.glossary_id)
				#self.Error('No Valid Project selected, please update the project key and try again.')	
			
			if isinstance(self.MyTranslator.Version, str):
				version = self.MyTranslator.Version[0:10]
			else:
				version = '-'

			if isinstance(self.MyTranslator.UpdateDay, str):
				Date = self.MyTranslator.UpdateDay[0:10]
			else:
				Date = '-'

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

			self.VersionStatus.set(version)
			self.UpdateDay.set(Date)
			
			self.Notice.set(self.LanguagePack.ToolTips['AppInitDone'])
			self.TranslatorProcess.join()
		else:
			self.Notice.set(self.LanguagePack.ToolTips['AppInit']) 

	

	def TMTranslateModeToggle(self):
		if self.TMTranslate.get() == 1:
			self.MyTranslator.TMModeEnable(True)
		else:
			self.MyTranslator.TMModeEnable(False)

	def GetOptions(self):
		#Get and set language
		if self.Language.get() == 1:
			self.Options['to_language'] = 'ko'
			self.Options['LanguageName'] = self.LanguagePack.Option['Hangul']
			self.Options['from_language'] = 'en'
		else:
			self.Options['to_language'] = 'en'
			self.Options['LanguageName'] = self.LanguagePack.Option['English']
			self.Options['from_language'] = 'ko'
		
		self.MyTranslator.SetTargetLanguage(self.Options['to_language'])
		self.MyTranslator.SetSourceLanguage(self.Options['from_language'])
		self.Notice.set(self.LanguagePack.ToolTips['SetLanguage'] + self.Options['LanguageName'])
		#Set translator engine
		self.MyTranslator.SetTranslatorAgent(self.MyTranslatorAgent)

		
		#Add Subscription key
		#self.MyTranslator.SetSubscriptionKey(self.SubscriptionKey)	

		#Set TM Update Mode
		if self.TMUpdate.get() == 1:
			self.MyTranslator.TMUpdateModeEnable(True)
		else:
			self.MyTranslator.TMUpdateModeEnable(False)

		#Set Predict mode 
		if self.TurboTranslate.get() == 1:
			self.MyTranslator.PredictModeEnable(True)
		else:
			self.MyTranslator.PredictModeEnable(False)

		#Set Data Mode
		if self.DataOnly.get() == 1:
			self.Options['DataMode']  = True
		else:
			self.Options['DataMode'] = False	

		#Set Skip Mode
		'''
		if self.SkipEmptyRow.get() == 1:
			self.Options['SkipMode'] = True
		else:
			self.Options['SkipMode'] = False
		'''
		self.Options['SkipMode'] = False
		#Set Sheet removal mode
		if self.SheetRemoval.get() == 1:
			self.Options['SheetRemovalMode'] = True
		else:
			self.Options['SheetRemovalMode'] = False

		# Set Update Mode
		if self.TMUpdate.get() == 1:
			self.Options['TMUpdateMode'] = True
		else:
			self.Options['TMUpdateMode'] = False



		#Set TM Translate Mode
		#print('self.TMTranslate', self.TMTranslate.get())
		if self.TMTranslate.get() == 1:
			self.Options['MemoryTranslate']  = True
		else:
			self.Options['MemoryTranslate'] = False

		#Set Translate File name option
		if self.TranslateFileName.get() == 1:
			self.Options['TranslateFileName'] = True
		else:
			self.Options['TranslateFileName'] = False
		
		#Set Translate Sheet name option
		if self.TranslateSheetName.get() == 1:
			self.Options['TranslateSheetName'] = True
		else:
			self.Options['TranslateSheetName'] = False

		#Set Name fixer mode
		if self.FixCorruptFileName.get() == 1:
			self.Options['FixCorruptFileName'] = True
		else:
			self.Options['FixCorruptFileName'] = False	

		#Get sheet list
		try:
			Raw = self.SheetList.get("1.0", END).replace("\n", "").replace(" ", "")	
			self.Options['Sheet'] = Raw.split(",")
		except:
			self.Options['Sheet'] = []

		# Get Documents list
		self.Options['SourceDocument'] = self.ListFile
		if self.Options['SourceDocument'] == "":
			self.Notice.set(self.LanguagePack.ToolTips['SourceNotSelected']) 
			return
		else:
			self.Notice.set(self.LanguagePack.ToolTips['DocumentLoad']) 


	def Translate(self):

		self.GetOptions()


		self.progressbar["value"] = 0
		self.progressbar.update()
		#SourceDocument = self.TextFilePath.get()
		
		
		
		# Kill exist Translator Process
		try:
			if self.TranslatorProcess.is_alive():
				self.TranslatorProcess.terminate()
		except:
			pass

		self.TranslateBtn.configure(state=DISABLED)

		# Clear exist queue
		try:
			while True:
				percent = self.ProcessQueue.get_nowait()
				print("Remain percent: ", percent)
		except queue.Empty:
			pass

		#self.TranslatorProcess = Process(target=Execuser, args=(self.MyTranslator, self.ProcessQueue ,self.ResultQueue, self.StatusQueue, SourceDocument, 
		#Multiple, TranslateFileName, TranslateSheetName, FixCorruptFileName, Sheet, DataMode, SheetRemovalMode, TMUpdateMode, SkipMode, TMTranslate,LastDocument, ))
		self.TranslatorProcess = Process(target=execute_document_translate, args=(self.MyTranslator, self.ProcessQueue ,self.ResultQueue, self.StatusQueue, self.Options,))
		self.TranslatorProcess.start()
		self.after(DELAY1, self.GetCompleteStatus)

	def BtnOptimizeXLSX(self):
		SourceDocument = self.RawFile

		self.p4 = Process(target=Optimize, args=(SourceDocument, self.StatusQueue,))
		self.p4.start()
		self.after(DELAY1, self.GetOptimizeStatus)	

	def GetOptimizeStatus(self):
		if (self.p4.is_alive()):
			try:
				Status = self.StatusQueue.get(0)
				if Status != None:
					SafeStatus = Status[0:StatusLength]
					self.Notice.set(SafeStatus)
					self.Debugger.insert("end", "\n")
					self.Debugger.insert("end", Status)
					self.Debugger.yview(END)
			except queue.Empty:
				pass	
			self.after(DELAY1, self.GetOptimizeStatus)
		else:
			try:
				Status = self.StatusQueue.get(0)
				if Status != None:	
					SafeStatus = Status[0:StatusLength]
					self.Notice.set(SafeStatus)
					self.Debugger.insert("end", "\n")
					self.Debugger.insert("end", Status)
					self.Debugger.yview(END)
			except queue.Empty:
				pass
			self.p4.terminate()

	def BtnOptimizeTM(self):
		SourceDocument = self.RawTMFile

		self.p4 = Process(target=OptimizeTM, args=(SourceDocument, self.StatusQueue,))
		self.p4.start()
		self.after(DELAY1, self.GetOptimizeTMStatus)	

	def GetOptimizeTMStatus(self):
		if (self.p4.is_alive()):
			try:
				Status = self.StatusQueue.get(0)
				if Status != None:
					SafeStatus = Status[0:StatusLength]
					self.Notice.set(SafeStatus)
					self.Debugger.insert("end", "\n")
					self.Debugger.insert("end", Status)
					self.Debugger.yview(END)
			except queue.Empty:
				pass	
			self.after(DELAY1, self.GetOptimizeStatus)
		else:
			try:
				Status = self.StatusQueue.get(0)
				if Status != None:	
					SafeStatus = Status[0:StatusLength]
					self.Notice.set(SafeStatus)
					self.Debugger.insert("end", "\n")
					self.Debugger.insert("end", Status)
					self.Debugger.yview(END)
			except queue.Empty:
				pass
			self.p4.terminate()

	def GetCompleteStatus(self):
		if (self.TranslatorProcess.is_alive()):
			try:
				percent = self.ProcessQueue.get(0)
				self.progressbar["value"] = percent
				self.progressbar.update()
				self.Progress.set("Progress: " + str(percent/10) + '%')
			except queue.Empty:
				pass
			try:
				Status = self.StatusQueue.get(0)
				if Status != None:
					SafeStatus = Status[0:StatusLength]
					self.Notice.set(SafeStatus)
					self.Debugger.insert("end", "\n")
					self.Debugger.insert("end", Status)
					self.Debugger.yview(END)

			except queue.Empty:
				pass		

			self.after(DELAY1, self.GetCompleteStatus)
		else:
			try:
				Result = self.ResultQueue.get(0)		
				if Result == True:
					self.progressbar["value"] = 1000
					self.progressbar.update()
					Status = self.StatusQueue.get(0)
					self.Progress.set("Progress: " + str(100) + '%')
					if Status != None:	
						SafeStatus = Status[0:StatusLength]
						self.Notice.set(SafeStatus)
						self.Debugger.insert("end", "\n")
						self.Debugger.insert("end", Status)
						self.Debugger.yview(END)
				elif '[Errno 13] Permission denied' in Result:
					self.Notice.set(self.LanguagePack.ToolTips['TranslateFail'])
					Result = Result.replace('[Errno 13] Permission denied','File is being in used')
					self.Error(str(Result))
					self.progressbar["value"] = 0
					self.progressbar.update()
					self.Progress.set("Progress: " + str(0) + '%')
				elif 'Package not found at' in Result:
					self.Notice.set(self.LanguagePack.ToolTips['TranslateFail'])
					Result = Result.replace(' Package not found at ','File is being in used: ')
					self.Error(str(Result))
					self.progressbar["value"] = 0
					self.progressbar.update()
					self.Progress.set("Progress: " + str(0) + '%')
				else:	
					self.Notice.set(self.LanguagePack.ToolTips['TranslateFail'])
					self.Error(str(Result))
					self.progressbar["value"] = 0
					self.progressbar.update()
					self.Progress.set("Progress: " + str(0) + '%')

				self.TranslatorProcess.terminate()
				self.TranslateBtn.configure(state=NORMAL)
			
			except queue.Empty:
				self.TranslateBtn.configure(state=NORMAL)
				pass
			while True:
				try:
					percent = self.ProcessQueue.get(0)
					self.progressbar["value"] = percent
					self.progressbar.update()
					self.Progress.set("Progress: " + str(percent/10) + '%')
				except queue.Empty:
					break

			if self.TMUpdate.get() == 1:
				self.RenewMyTranslator()
				#self.TMStatus.set(str(self.MyTranslator.translation_memory_size))

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
		if self._hits:
			self.delete(0,END)
			self.insert(0,self._hits[self._hit_index])
			self.select_range(self.position,END)

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
			#self.autocomplete()			
			self.autofill()		

def SortDictionary(List):
	return(sorted(List, key = lambda x: (len(x[1]), x[1]), reverse = True))

def Importtranslation_memory(TMPath):
	if TMPath == None:
		return []
	elif os.path.isfile(TMPath):
		print('TM exist')
		try:
			with open(TMPath, 'rb') as pickle_load:
				TM = pickle.load(pickle_load)
			print('TM loaded, pair found: ', len(TM))
			return TM
		except:
			#print('TM is corrupted.')
			return []
	else:
		print('TM not exist')
		return []

# Function for Document Translator
def GenerateTranslator(Mqueue, TMManager, from_language = 'ko', to_language = 'en', glossary_id = "", tm_path= None,):	
	print("Generate my Translator")
	MyTranslator = Translator(from_language = from_language, to_language = to_language, glossary_id =  glossary_id, tm_path = tm_path, used_tool = tool_name, tool_version = VerNum,)
	Mqueue.put(MyTranslator)

def Optimize(SourceDocument, StatusQueue):
	from openpyxl import load_workbook, worksheet, Workbook
	from openpyxl.styles import Font
	#print(SourceDocument)
	FileList = os.listdir(SourceDocument)
	#print(FileList)
	for FileName in FileList:

		if FileName != None:
			File = SourceDocument + '//' + FileName
			try:
				xlsx = load_workbook(File, data_only=True)
			except:
				continue
			
			Outputdir = os.path.dirname(File) + '/Optimized/'
			baseName = os.path.basename(File)
			sourcename, ext = os.path.splitext(baseName)
			TranslatedName	= sourcename

			StatusQueue.put('Optimizing file: ' + TranslatedName)
			

			if not os.path.isdir(Outputdir):
				try:
					os.mkdir(Outputdir)
					output_file = Outputdir + sourcename + ext
				except OSError:
					print ("Creation of the directory %s failed" % Outputdir)
					output_file = os.path.dirname(File) + '/' + sourcename + '_Optmized' + ext
			else:
				output_file = Outputdir + sourcename + ext	
			
			try:
				xlsx.save(output_file)
				#StatusQueue.put('Optimized done.')
			except Exception as e:
				StatusQueue.put('Failed to save the result: ' + str(e))
	StatusQueue.put('Optimized done.')	


###########################################################################################

###########################################################################################
def Function_Execute_Script(StatusQueue, DB_Path, glossary_id, **kwargs):

	Output = Function_Create_CSV_DB(StatusQueue, DB_Path)
	StatusQueue.put("CSV DB created:" + str(Output))
	if glossary_id != '':
		
		client = logging.Client()
		log_name = 'db-update'
		logger = client.logger(log_name)
		try:
			account = os.getlogin()
		except:
			account = 'Anonymous'
		
		try:
			name = os.environ['COMPUTERNAME']
		except:
			name = 'Anonymous'	
		# Update new format later
		'''
		data_object = {
				'device': self.pc_name,
				'project': self.glossary_id,
				'tool': self.used_tool,
				'tool_ver': self.tool_version,
				'translator_ver': ver_num,
				'api_usage': self.last_section_api_usage,
				'tm_usage': self.last_section_tm_request,
				'invalid_request': self.last_section_invalid_request,
				'tm_size': self.translation_memory_size,
				'tm_path': self.tm_path
			}
		if 	file_name != None:
			data_object['file_name'] = file_name

		tracking_object = {
			'user': self.user_name,
			'details': data_object
		}
		
		logger.log_struct(tracking_object)
		'''
		text_log = account + ', ' + name + ', ' + glossary_id + ', ' + DB_Path
		logger.log_text(text_log)

		myTranslator = Translator('ko', 'en', None, None, False, False, False, glossary_id, )
		
		myTranslator.update_glob(glossary_id, Output)

		StatusQueue.put("DB updated.")

def Function_Execute_Create_Script(StatusQueue, DB_Path, glossary_id, URI, **kwargs):

	Output = Function_Create_CSV_DB(StatusQueue, DB_Path)
	StatusQueue.put("CSV DB created:" + str(Output))
	myTranslator = Translator('ko', 'en', None, None, False, False, False, glossary_id, )
	
	myTranslator.Update_Glob(glossary_id, Output)	
	StatusQueue.put("DB created.")

def Function_Update_Glossary(self):

	return

def Function_Create_CSV_DB(
		StatusQueue, DB_Path, **kwargs
):
	from openpyxl import load_workbook, worksheet, Workbook
	import csv
	
	DatabasePath = DB_Path

	Outputdir = os.path.dirname(DatabasePath)
	baseName = os.path.basename(DatabasePath)
	sourcename, ext = os.path.splitext(baseName)

	#output_file = Outputdir + '/' + sourcename + '_SingleFile.xlsx'
	output_file_csv = Outputdir + '/' + sourcename + '.csv'
	SpecialSheets = ['info']

	RowCount = 0

	if DatabasePath != None:
		if (os.path.isfile(DatabasePath)):
			xlsx = load_workbook(DatabasePath)
			DictList = []
			Dict = []
			with open(output_file_csv, 'w', newline='', encoding='utf_8_sig') as csv_file:
				writer = csv.writer(csv_file, delimiter=',')
				writer.writerow(['Description', 'ko', 'en'])
				for sheet in xlsx:
					sheetname = sheet.title.lower()
					
					if sheetname not in SpecialSheets:	
					
						EN_Coll = ""
						KR_Coll = ""
						database = None
						ws = xlsx[sheet.title]
						for row in ws.iter_rows():
							for cell in row:
								if cell.value == "KO":
									KR_Coll = cell.column_letter
									KR_Row = cell.row
									database = ws
								elif cell.value == "EN":
									EN_Coll = cell.column_letter
								if KR_Coll != "" and EN_Coll != "":
									DictList.append(sheet.title)
									break	
							if database!=  None:
								break		

						if database != None:
							
							for i in range(KR_Row, database.max_row): 
								KRAddress = KR_Coll + str(i+1)
								ENAddress = EN_Coll + str(i+1)
								KRCell = database[KRAddress]
								KRValue = KRCell.value
								ENCell = database[ENAddress]
								ENValue = ENCell.value
								if KRValue in [None, 'KO'] or ENValue in [None, 'EN']:
									continue
								elif KRValue not in  ["", 'KO'] and ENValue not in ["", 'EN']:
									KRValue = KRCell.value.replace('\r', '').replace('\n', '')
									ENValue = ENCell.value.replace('\r', '').replace('\n', '')
									if sheetname != 'header':
										ENValue = ENValue.lower()
									writer.writerow([sheetname, KRValue, ENValue])
									RowCount+=1
					elif sheetname == 'info':
						ws = xlsx[sheet.title]
						for row in ws.iter_rows():
							for cell in row:
								if cell.value == "i_version":
									temp_Col = chr(ord(cell.column_letter) + 1)
									temp_Row = cell.row
									temp_Add = temp_Col + str(temp_Row)	
									temp_Cel = ws[temp_Add]
									temp_Val = temp_Cel.value
									writer.writerow(['info', 'i_version', temp_Val])
								elif cell.value == "i_date":
									temp_Col = chr(ord(cell.column_letter) + 1)
									temp_Row = cell.row
									temp_Add = temp_Col + str(temp_Row)	
									temp_Cel = ws[temp_Add]
									temp_Val = temp_Cel.value
									writer.writerow(['info', 'i_date', temp_Val])

		StatusQueue.put("Successfully load dictionary from: " +  str(DictList))

	return output_file_csv


###########################################################################################

def OptimizeTM(SourceDocument, StatusQueue):

	KO = []
	EN = []
	to_remove = []
	for File in SourceDocument:
		if File != None:
			try:
				with open(File, 'rb') as pickle_load:
					TM = pickle.load(pickle_load)
				if isinstance(TM, list):
					print('Old TM format')
					for Pair in TM:
						KO.append(Pair[0])
						EN.append(Pair[1])
					#self.en_tm = np.array(en)
					#self.ko_tm = np.array(ko)
				elif isinstance(TM, dict):
					print('New TM format')
					KO = TM['KO']
					EN = TM['EN']
					#self.en_tm = np.array(TM['en'])
					#self.ko_tm = np.array(TM['ko'])
			except:
				print('Fail to load tm')
				return
			en_to_remove = []
			ko_to_remove = []
			for index in range(len(EN)):
				word = EN[index]
				if word == "":
					en_to_remove.append(word)
				elif not ValidateEnglishSource(word):
					en_to_remove.append(word)

			for index in range(len(KO)):
				word = KO[index]
				if word == "":
					ko_to_remove.append(word)
				elif not ValidateKoreanSource(word):
					ko_to_remove.append(word)	
			
			to_remove = list(dict.fromkeys(to_remove))

			for word in en_to_remove:
				index = EN.index(word)
				try:
					if index != -1:
						print('Removing: ', '\r\nEN: ', EN[index], '\r\nKO: ', KO[index])
						del EN[index]
						del KO[index]
				except:
					continue	
			for word in ko_to_remove:
				try:
					index = KO.index(word)
					if index != -1:
						print('Removing: ', '\r\nEN: ', EN[index], '\r\nKO: ', KO[index])
						del EN[index]
						del KO[index]
				except:
					continue		

			print("Total removed: " , len(en_to_remove) + len(ko_to_remove))
			Message = "Total removed: " + str(len(en_to_remove) + len(ko_to_remove))
			StatusQueue.put(Message)
			'''
			Outputdir = os.path.dirname(File)
			baseName = os.path.basename(File)
			sourcename, ext = os.path.splitext(baseName)
			TranslatedName	= sourcename
			output_file = Outputdir + '/' + TranslatedName + '_Optmized' + ext
			'''
			translation_memory = {}
			translation_memory['EN'] = EN
			translation_memory['KO'] = KO

			with open(File, 'wb') as pickle_file:
				pickle.dump(translation_memory, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)


# Function for processor	
def MergeTMSource(SourceDocument, OutputDocument, StatusQueue):
	NewTM = []

	for File in SourceDocument:
		if File != None:
			
			with open(File, 'rb') as pickle_load:
				TempPickle = pickle.load(pickle_load)
			for Pair in TempPickle:
				NewTM.append(Pair)
			StatusQueue.put('Finish adding ' + str(File) + ' to new TM.')	

	StatusQueue.put('Total TM load: ' + str(len(NewTM)))

	if len(NewTM) != 0:	
		b_set = set(tuple(x) for x in NewTM)
		SortedTM = [ list(x) for x in b_set ]
		print('Total TM sentence has been added: ', str(len(SortedTM)))
		with open(OutputDocument, 'wb') as pickle_file:
			print("Saving pickle file....", OutputDocument)
			pickle.dump(SortedTM, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

	StatusQueue.put('Saving TM successful, total duplicated Pair: ' + str(len(NewTM)- len(SortedTM)))
			
def OldalidateEnglishSource(string):
	try:
		string.encode('ascii')
	except UnicodeEncodeError :
		return False
	else:

		return True

def ValidateEnglishSource(string):
	for i in range(len(string)):
		c = string[i]
		if unicodedata.category(c)[0:2] == 'Ll' : # other characters
			try:
				if 'LATIN' in unicodedata.name(c) : return True
			except:
				continue
	return False
		

def ValidateKoreanSource(string):
	for i in range(len(string)):
		c = string[i]
		if unicodedata.category(c)[0:2] == 'Lo' : # other characters
			try:
				if 'HANGUL' in unicodedata.name(c) : return True
			except:
				continue
	return False



def ValidateURL(string):
	
	Result = urlparse(string)
	
	try:
		if Result.scheme == "" or Result.netloc == "":
			return False
		else:
			#print(Result)
			return True	
	except:
		return False

def execute_document_translate(MyTranslator, ProgressQueue, ResultQueue, StatusQueue, Options,):
	print('Creating process for Translator...')
	Start = time.time()

	SourceDocument = Options['SourceDocument']


	Preflix = ""
	Preflix	+= MyTranslator.To_Language.upper() + '_'
	
	Result = False

	if Options['TMUpdateMode']:
			#print(MyTranslator.LanguagePack.ToolTips['TMUpdating']) 
			#MyTranslator.ProactiveTMTranslate = False
			MyTranslator.TMUpdate = True
	try:
		ProgressQueue.get_nowait()
	except queue.Empty:
		pass
	
	for File in SourceDocument:
		if File != None:
			
			Outputdir = os.path.dirname(File)
			baseName = os.path.basename(File)
			sourcename, ext = os.path.splitext(baseName)

			try:
				Newsourcename = sourcename.encode('cp437').decode('euc_kr')
				StatusQueue.put('Correct name: ' + Newsourcename)
				
			except:
				Newsourcename = sourcename
				StatusQueue.put('fail to create new name: ' + Newsourcename)

			if Options['FixCorruptFileName'] == True:	
				try:
					fixed_name = sourcename.encode('cp437').decode('euc_kr')
					newPath = Outputdir + '/'+ fixed_name + ext
				except:
					newPath = File
				try:
					os.rename(File, newPath)
					StatusQueue.put('Fixed name: ' + fixed_name)
				except:
					newPath = File
			else:
				newPath = File

			now = datetime.now()

			timestamp = str(int(datetime.timestamp(now)))

			if Options['TranslateFileName']:
				Translated = MyTranslator.translate(Newsourcename)
				if Translated != False:
					TranslatedName = re.sub(r'[\\/\:*"<>\|\.%\$\^&£]', '', Translated)
				else:
					TranslatedName = Newsourcename
			else:
				TranslatedName	= Newsourcename
			output_file = Outputdir + '/' + Preflix + TranslatedName + '_' + timestamp + ext
			#print('Output file name: ', output_file)
		
		Options['SourceDocument'] = newPath
		Options['OutputDocument'] = output_file
		if ext == '.docx':
			#Result = translateDocx(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			try:
				Result = translateDocx(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			except Exception as e:
				ErrorMsg = ('Error message: ' + str(e))
				print(ErrorMsg)
				StatusQueue.put(str(e))
				Result = str(e)
				
		elif ext in ['.xlsx', '.xlsm']:
			#Result = translateWorkbook(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			try:
				Result = translateWorkbook(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			except Exception as e:
				ErrorMsg = ('Error message: ' + str(e))
				print(ErrorMsg)
				StatusQueue.put(str(e))
				Result = str(e)
		elif ext == '.msg':
			#Result = translateMsg(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			try:
				Result = translateMsg(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			except Exception as e:
				ErrorMsg = ('Error message: ' + str(e))
				print(ErrorMsg)
				StatusQueue.put(str(e))
				Result = str(e)
		elif ext == '.pdf':
			#Result = translateDPF(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			try:
				Result = translateDPF(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			except Exception as e:
				ErrorMsg = ('Error message: ' + str(e))
				print(ErrorMsg)
				StatusQueue.put(str(e))
				Result = str(e)
		
		elif ext == '.pptx':
			#Result = TranslatePresentation(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			try:
				Result = TranslatePresentation(ProgressQueue=ProgressQueue, ResultQueue=ResultQueue, StatusQueue=StatusQueue, Mytranslator=MyTranslator, Options=Options)
			except Exception as e:
				ErrorMsg = ('Error message: ' + str(e))
				StatusQueue.put(str(e))
				print(ErrorMsg)
				Result = str(e)

		if Result == True:
			ResultQueue.put(Result)
			End = time.time()
			Total = End - Start
			StatusQueue.put('Total time spent: ' + str(Total) + ' second.')
			StatusQueue.put('Translated file: ' + Preflix + ' ' + TranslatedName + '_' + timestamp + ext)
		else:
			ResultQueue.put(str(Result))
		try:
			mem_tm = len(MyTranslator.TMManager)
			newTM = MyTranslator.Appendtranslation_memory()
			MyTranslator.send_tracking_record(file_name = baseName)
			StatusQueue.put('Source: ' + str(baseName))
			StatusQueue.put('TM usage: ' + str(MyTranslator.Last_Section_TM_Request))
			StatusQueue.put('API usage: ' + str(MyTranslator.Last_Section_API_Usage))
			StatusQueue.put('Invalid request: ' + str(MyTranslator.Last_Section_Invalid_Request))
			StatusQueue.put('TM In-memory: ' + str(mem_tm))
			StatusQueue.put('TM append this section: ' + str(newTM))
			#StatusQueue.put('TM In-memory: ' + str(len(MyTranslator.TMManager)))

		except:
			pass

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
	ProcessQueue = Queue()
	ResultQueue = Queue()
	StatusQueue = Queue()
	MyTranslatorQueue = Queue()
	
	MyManager = Manager()
	TMManager = MyManager.list()
	MyDB = Queue()
	root = Tk()

	style = Style(root)
	style.map('Treeview', foreground=fixed_map(style, 'foreground'), background=fixed_map(style, 'background'))

	try:
		DocumentTranslator(root, ProcessQueue = ProcessQueue, ResultQueue = ResultQueue, StatusQueue = StatusQueue
		, MyTranslatorQueue = MyTranslatorQueue, MyDB_Queue = MyDB, TMManager = TMManager)
		root.mainloop()
		
	except Exception as e:
		root.withdraw()

		try:
			from google.cloud import logging
			AppConfig = ConfigLoader()
			Configuration = AppConfig.Config
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Configuration['license_file']['path']
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
			print('Docuement tool: Fail to send log to server.')
			return
		print("error message:", e)	
		messagebox.showinfo(title='Critical error', message=e)


if __name__ == '__main__':
	if sys.platform.startswith('win'):
		multiprocessing.freeze_support()
	
	main()
