
import copy
import os

import multiprocessing
import queue 
#from multiprocessing import Process, Queue, Pool
from multiprocessing import Process , Queue, Manager
import subprocess
import time
from datetime import datetime



# Functions used for processor
def CheckList(item, list):
	if list == [] or list == [""]:
		return True
	for text in list:
		if item == text:
			return True
	return False

# Functions used for processor
def GenerateSheetList(SheetList, TranslateList):
	if TranslateList == [] or TranslateList == [""]:
		return SheetList
	#TotalSheet = len(SheetList)
	IndexList = []
	for sheet in TranslateList:
		print("Sheet: ", sheet)
		if sheet.isnumeric():
			IndexList.append(int(sheet))
		else:	
			tempList = sheet.split('-')
			#print('tempList: ', tempList)
			#print('Len tempList: ', len(tempList))
			invalid = False
			if len(tempList) == 2:
				for tempIndex in tempList:
					#print("Item: ",  tempIndex)
					if tempIndex.isnumeric() != True:
						invalid = True
			else:
				invalid = True
			if invalid == False:
				
				A = int(tempList[0])
				B = int(tempList[1])
				
				if A < B:
					Min = A
					Max = B
				else:
					Min = B
					Max = A	
				#print('Min max: ', Min, Max)
				i = Min
				while i >= Min and i <= Max:
					IndexList.append(i)
					i+=1
			else:
				i = 0
				for source in SheetList:
					if source == sheet:
						IndexList.append(i)		
					i+=1

	toReturn = []

	i = 1
	for toTranslate in SheetList:
		for num in IndexList:
			if i == num:
				toReturn.append(toTranslate)
		i+=1
	return toReturn

def ShowProgress(Counter, TotalProcess):
	#os.system('CLS') 
	percent = int(1000 * Counter / TotalProcess)
	#print("Current progress: " +  str(Counter) + '/ ' + str(TotalProcess))
	return percent

#Para Translate
def paraTranslate(tasks_to_accomplish, tasks_that_are_done, Mytranslator):
	while True:
		#print('paraTranslate is running')
		try:
			Task = tasks_to_accomplish.get_nowait()
		except queue.Empty:
			break
		else:
			if Task != None:
				ToTranslate = Task.Text
				Task.Fail = 0
				#print('Current text: ', ToTranslate)
				SourceText = ToTranslate.split('\n')
				Translated = Mytranslator.translate(SourceText)
				#print('Para Translated', Translated)
				i = 0
				for string in Translated:
					if string == False:
						Translated[i] = SourceText[i]
						#print('Fail to translate....')
						Task.Fail+=1
						i+=1
			
				Merged = "\n".join(Translated)
				Task.Text = Merged
				tasks_that_are_done.put(Task)
			else:
				tasks_that_are_done.put(None)
	return True

def cell_translate(MyTranslator, tasks_to_accomplish):

	List = []
	Length = []
	for task in tasks_to_accomplish:
		Input = task.Text
		
		if isinstance(Input, list):
			Length.append(len(Input))
			List += Input
		elif isinstance(Input, str):
			Length.append(1)
			List.append(Input)
	Result = MyTranslator.translate(List)
	#for i in range(len(List)):
	#	print(List[i], ":", Result[i])

	current_index = 0
	for i in range(len(tasks_to_accomplish)):
		temp_result = Result[current_index:current_index+Length[i]]
		tasks_to_accomplish[i].Text = temp_result
		current_index+=Length[i]
	return tasks_to_accomplish



# xlsx object
# Add a cell as a task with an address
class CellData:
	def __init__(self, SheetName, CellAddress, Text):
		self.Sheet = SheetName
		self.Address = CellAddress
		self.Text = Text
		self.Fail = 0

# pptx object
# Add a Paragraph as a task with an address
class TextFrameData:
	def __init__(self, ParagraphsNum, RunsNum, String):
		self.Paragraphs = ParagraphsNum
		self.Runs = RunsNum
		self.Text = String

# docx object

class DocxData:
	def __init__(self, ParagraphData, TableData):
		self.Paragraphs = ParagraphData
		self.Tables = TableData
	

class ParagraphsData:
	def __init__(self, Paragraph_Index, Run_Index, Text):
		self.Paragraph = Paragraph_Index
		self.Run = Run_Index
		self.Text = Text

class TableData:
	def __init__(self, ParagraphsNum, RunsNum, String):
		self.Paragraphs = ParagraphsNum
		self.Runs = RunsNum
		self.Text = String

class RunData:
	def __init__(self, RunsNum, String):
		self.Runs = RunsNum
		self.Text = String

#Workbook handle
def translateWorkbook(ProgressQueue=None, ResultQueue=None, StatusQueue=None, Mytranslator=None, Options = {}):
	
	from openpyxl import load_workbook, worksheet, Workbook
	from openpyxl.styles import Font

	if not 'SourceDocument' in Options:
		StatusQueue.put('No source document input')
		return False
	else:
		SourceDocument = Options['SourceDocument']

	if not 'OutputDocument' in Options:
		now = datetime.now()
		timestamp = str(int(datetime.timestamp(now)))
		Outputdir = os.path.dirname(SourceDocument)
		baseName = os.path.basename(SourceDocument)
		sourcename = os.path.splitext(baseName)[0]
		OutputDocument = Outputdir + '/' + 'Translated_' + sourcename + '_' + timestamp + '.xlsx'
	else:
		OutputDocument = Options['OutputDocument']

	if not 'TranslateSheetName' in Options:
		TranslateSheetName = True
	else:
		TranslateSheetName = Options['TranslateSheetName']

	if not 'Sheet' in Options:
		Sheet = []
	else:
		Sheet = Options['Sheet']

	if not 'DataOnly' in Options:
		DataOnly = True
	else:
		DataOnly = Options['DataOnly']

	if not 'SheetRemovalMode' in Options:
		SheetRemovalMode = False
	else:
		SheetRemovalMode = Options['SheetRemovalMode']

	try:
		if DataOnly:
			xlsx = load_workbook(SourceDocument, data_only=True)
		else:
			xlsx = load_workbook(SourceDocument)	
	except Exception as e:
		StatusQueue.put('Failed to load the document: ' + str(e))
		return e

	StatusQueue.put('Estimating total task to do...')
	ProgressQueue.put(0)
	#tasks_to_accomplish = Queue()
	#tasks_that_are_done = Queue()
	#processes = []
	
	TaskList = []

	SheetList = []
	for sheet in xlsx:
		SheetList.append(sheet.title)
	#StatusQueue.put('Sheet List' + str(SheetList))


	current_task = 0

	TranslateList = GenerateSheetList(SheetList, Sheet)	
	#StatusQueue.put('Translate List' + str(TranslateList))
	for sheet in TranslateList:
		ws = xlsx[sheet]
		for row in ws.iter_rows():
			for cell in row:
				if cell.value != None:
					current_task+=1
	
	TotalTask = current_task
	Counter = 0
	if current_task == 0:
		print('Done')
	else:
			
		StatusQueue.put('Total task: ' + str(TotalTask))
		percent = ShowProgress(Counter, TotalTask)
		ProgressQueue.put(percent)		
		memory_translation = 0	
		fail_request = 0
		empty_cell = 0
		StatusQueue.put('Checking task detail...')

		StatusQueue.put('Pre-processing document...')
		for sheet in xlsx:
			if CheckList(sheet.title, TranslateList):
				StatusQueue.put("Checking sheet: " + str(sheet.title))
				for row in sheet.iter_rows():
					for cell in row:
						if cell.value != None:
							current_string = str(cell.value)
							result = Mytranslator.ValidateSourceText(current_string)
							if result == False:

								fail_request+=1

							elif result != True:

								cell.value = result
								memory_translation+=1
							else:
								ListString = current_string.split('\n')
								SheetName = sheet.title
								CellAddress = cell.column_letter + str(cell.row)
								Task = CellData(SheetName, CellAddress, ListString)
								TaskList.append(Task)
				Counter = fail_request + memory_translation
				percent = ShowProgress(Counter, TotalTask)
				ProgressQueue.put(percent)
			else:
				if SheetRemovalMode:
					std = xlsx.get_sheet_by_name(sheet.title)
					xlsx.remove_sheet(std)

		StatusQueue.put('Empty cell: ' + str(empty_cell))
		StatusQueue.put('Fail request: ' + str(fail_request))
		StatusQueue.put('Translated by Memory: ' + str(memory_translation))
		RemainedTask = TotalTask-Counter	
		StatusQueue.put('Remained task: ' + str(RemainedTask))

		Task_todo = []
		
		while len(TaskList) > 0:
			Translated = []
			TaskLength = 0
			
			while TaskLength < 2000:
				if len(TaskList) > 0:
					Input = TaskList[0].Text
					if isinstance(Input, list):
						TempLen = TaskLength
						for tempString in Input:
							TempLen += len(tempString)
			
					elif isinstance(Input, str):
						TempLen = TaskLength + len(TaskList[0].Text)
						
					if TempLen < 2000:
						TaskLength = TempLen
						Task_todo.append(TaskList[0])
						del TaskList[0]
					else:
						break	
				else:
					break
			Translated = cell_translate(Mytranslator, Task_todo)
			for task in Translated:
				Return = task
				NewSheet = Return.Sheet
				NewAdd = Return.Address
				NewVal = Return.Text
				if isinstance(NewVal, list):
					NewVal = '\r\n'.join(NewVal)

				ws = xlsx[NewSheet]
				cell  = ws[NewAdd]
				cell.value = str(NewVal)
				tempFont = copy.copy(cell.font)  
				tempFont.name = 'Times New Roman'
				cell.font = tempFont
		
			RemainedTask = len(TaskList)
			Message = str(RemainedTask) + ' tasks remain....'
			StatusQueue.put(Message)	

			Counter = TotalTask - RemainedTask
			percent = ShowProgress(Counter, TotalTask)
			ProgressQueue.put(percent)
			del Task_todo
			Task_todo = []

		if TranslateSheetName:
			StatusQueue.put('Translating sheet name...')
			to_translate = []
			for sheet in xlsx:
				if CheckList(sheet.title, TranslateList):
					CurrentSheetName = sheet.title
					to_translate.append(CurrentSheetName)
			translated = Mytranslator.translate(to_translate)
			index = 0
			for sheet in xlsx:
				if CheckList(sheet.title, TranslateList):
					try:
						sheet.title = translated[index][0:29]
					except:
						pass	
					index+=1
		StatusQueue.put('Exporting result....')	
		print('Exporting file to ', OutputDocument)
		
		try:
			xlsx.save(OutputDocument)
			if os.path.isfile(OutputDocument):
				return True
			else:
				return False	
		except Exception as e:
			StatusQueue.put('Failed to save the result: ' + str(e))
			return e
	StatusQueue.put('No thing to do with this file.')	


#**********************************************************************************
#pptx handle **********************************************************************
#**********************************************************************************

def TranslatePresentation(ProgressQueue=None, ResultQueue=None, StatusQueue=None, Mytranslator=None, Options = {}):
	from pptx import Presentation
	
	
	ProgressQueue.put(0)
	
	if not 'SourceDocument' in Options:
		StatusQueue.put('No source document input')
		return False
	else:
		SourceDocument = Options['SourceDocument']
	#print('SourceDocument: ', SourceDocument)
	if not 'OutputDocument' in Options:
		now = datetime.now()
		timestamp = str(int(datetime.timestamp(now)))
		Outputdir = os.path.dirname(SourceDocument)
		baseName = os.path.basename(SourceDocument)
		sourcename, ext = os.path.splitext(baseName)
		OutputDocument = Outputdir + '/' + 'Translated_' + sourcename + '_' + timestamp + ext
	else:
		OutputDocument = Options['OutputDocument']

	if not 'Multiple' in Options:
		Multiple = 8
	else:
		Multiple = Options['Multiple']
	
	pptx = Presentation(SourceDocument)
	print('Estimating total task to do...')
	StatusQueue.put('Estimating total task to do...')


	if Multiple == None:
		print('Turbo mode is not available for the presentation translator')
	Start = time.time()
	total = 0
	
	for slide in pptx.slides:
		for shape in slide.shapes:
			if shape.has_text_frame:
				for paragraph in shape.text_frame.paragraphs:
					string = paragraph.text
					if string != "":
						if string != None:
							if isinstance(string, str) == True:
									total+= 1
			if shape.has_table:	
				for row in shape.table.rows:
					for cell in row.cells:
						for paragraph in cell.text_frame.paragraphs:
							string = paragraph.text
							if string != "":
								if string != None:
									if isinstance(string, str) == True:
										total+= 1
	TotalTask = total
	print('Total task: ', TotalTask)
	StatusQueue.put('Total task: ' + str(TotalTask))
	Counter = 0
	
	for slide in pptx.slides: 
		for shape in slide.shapes:
			if shape.has_text_frame:
				for paragraph in shape.text_frame.paragraphs:
					FirstRun = None
					CurentText = ""
					for j in range(len(paragraph.runs)):
						run = paragraph.runs[j]
						if FirstRun == None:
							FirstRun = j		
						if run.text == '':
							if CurentText != '':
								ListText = CurentText.split('\n')
								Translated = Mytranslator.translate(ListText)
								Translated = "\n".join(Translated)
								Translated = Translated.replace("\r\r\n", "\r\n")
								paragraph.runs[FirstRun].text = Translated
								
							FirstRun = None
							CurentText = ""
						else:
							CurentText += str(run.text)
							run.text = ""

					if CurentText != '':
						ListText = CurentText.split('\n')
						Translated = Mytranslator.translate(ListText)
						Translated = "\n".join(Translated)
						Translated = Translated.replace("\r\r\n", "\r\n")
						paragraph.runs[FirstRun].text = Translated
				
					Counter+=1
					percent = ShowProgress(Counter, TotalTask)
					ProgressQueue.put(percent)

			if shape.has_table:	
				for row in shape.table.rows:
					for cell in row.cells:
						for paragraph in cell.text_frame.paragraphs:
							FirstRun = None
							CurentText = ""
							for j in range(len(paragraph.runs)):
								run = paragraph.runs[j]
								if FirstRun == None:
									FirstRun = j		
								if run.text == '':
									if CurentText != '':
										ListText = CurentText.split('\n')
										Translated = Mytranslator.translate(ListText)
										Translated = "\n".join(Translated)
										Translated = Translated.replace("\r\r\n", "\r\n")
										paragraph.runs[FirstRun].text = Translated
										
									FirstRun = None
									CurentText = ""
								else:
									CurentText += str(run.text)
									run.text = ""

							if CurentText != '':
								ListText = CurentText.split('\n')
								Translated = Mytranslator.translate(ListText)
								Translated = "\n".join(Translated)
								Translated = Translated.replace("\r\r\n", "\r\n")
								paragraph.runs[FirstRun].text = Translated

							Counter+=1
							percent = ShowProgress(Counter, TotalTask)
							ProgressQueue.put(percent)

	percent = ShowProgress(TotalTask, TotalTask)
	print('percent: ', percent)
	StatusQueue.put('Exporting document...')
	try:
		pptx.save(OutputDocument)
		if (os.path.isfile(OutputDocument)):
			End = time.time()
			Message = "Total time spend: " + str(int(End-Start)) + ' seconds.'
			StatusQueue.put(Message)
			return True
		else:
			return False	
	except Exception as e:
		StatusQueue.put('Error message: ' + str(e))
		return e

def translateFrametable(cell, Mytranslator, CurrentTask, TotalTask):
	from docx.shared import RGBColor

	for paragraph in cell.text_frame.paragraphs:
		FirstRun = None
		CurentText = ""
		for j in range(len(paragraph.runs)):
			run = paragraph.runs[j]
			if FirstRun == None:
				FirstRun = j		

			if run.text == '':
				if CurentText != '':
					#print('CurentText ', CurentText)
					ListText = CurentText.split('\n')
					#print('ListText ', ListText)
					Translated = Mytranslator.translate(ListText)
					Translated = "\n".join(Translated)
					#Translated = Translated.replace("\r\r\n", "\r\n")
					#print('Translated ', Translated)
					paragraph.runs[FirstRun].text = Translated
				FirstRun = None
				CurentText = ""
			else:
				CurentText += str(run.text)
				run.text = ""
		if CurentText != '':
			#print('CurentText ', CurentText)
			ListText = CurentText.split('\n')
			#print('ListText ', ListText)
			Translated = Mytranslator.translate(ListText)
			Translated = "\r\n".join(Translated)
			Translated = Translated.replace("\r\r\n", "\r\n")
			#print('Translated ', Translated)
			paragraph.runs[FirstRun].text = Translated

		CurrentTask+=1

	if cell.has_table:	
		for row in cell.table.rows:
			for newcell in row.cells:
				newcell = translateFrametable(cell, Mytranslator, CurrentTask, TotalTask)
				total+= 1
		print('Another table inside a table cell.')

	return [newcell, CurrentTask]

#**********************************************************************************
#Docx handle **********************************************************************
#**********************************************************************************

def CheckParagraphStyle(paragraph, Debug = False):
	if len(paragraph.runs) <= 1:
		return False
	for i in range(len(paragraph.runs)):
		
		run = paragraph.runs[i]
		rbold = str(run.bold)
		ritalic = str(run.italic)
		rcolor = str(run.font.color.rgb)
		runderline = str(run.underline)
		if Debug == True:
			#print("Checking: ", paragraph.text)
			print('bold', run.bold)
			print('italic', run.italic)
			print('color', run.font.color.rgb)
			print('underline', run.underline)

		if rbold != "None" and rbold != "False":
			return True
		elif ritalic != "None" and ritalic != "False":
			return True
		elif rcolor != "000000" and rcolor != "None":
			return True
		elif runderline != "None" and runderline != "False":
			return True

	return False

def translateDocx(ProgressQueue=None, ResultQueue=None, StatusQueue=None, Mytranslator=None, Options = {}):
	import docx
	
	from docx.shared import RGBColor
	print('Estimating total work to do...')
	StatusQueue.put('Estimating total task to do...')
	ProgressQueue.put(0)
	
	if not 'SourceDocument' in Options:
		StatusQueue.put('No source document input')
		return False
	else:
		SourceDocument = Options['SourceDocument']

	if not 'OutputDocument' in Options:
		now = datetime.now()
		timestamp = str(int(datetime.timestamp(now)))
		Outputdir = os.path.dirname(SourceDocument)
		baseName = os.path.basename(SourceDocument)
		sourcename, ext = os.path.splitext(baseName)
		OutputDocument = Outputdir + '/' + 'Translated_' + sourcename + '_' + timestamp + ext
	else:
		OutputDocument = Options['OutputDocument']

	Mydocx = docx.Document(SourceDocument)
	
	Start = time.time()
	
	Counter = 0
	TotalTask = 0
	for i in range(len(Mydocx.paragraphs)):
		TotalTask += 1
	for table in Mydocx.tables:	
		TotalTask += Estimatetables(table)
	StatusQueue.put('Total task: ' + str(TotalTask))

	ParagraphDataList = []

	for i in range(len(Mydocx.paragraphs)):
		paragraph = Mydocx.paragraphs[i]
		if paragraph.text != '':
			#print('TempText', paragraph.text)
			FirstRun = None
			CurentText = ""
			for j in range(len(paragraph.runs)):
				run = paragraph.runs[j]
				if FirstRun == None:
					FirstRun = j		

				if run.text == '':
					if CurentText != '':
						ParagraphData = ParagraphsData(i, FirstRun, CurentText)
						ParagraphDataList.append(ParagraphData)
					FirstRun = None
					CurentText = ""
				else:
					CurentText += str(run.text)
					run.text = ""
			
			if CurentText != '':
				ParagraphData = ParagraphsData(i, FirstRun, CurentText)
				ParagraphDataList.append(ParagraphData)
			#('Adding:', ParagraphData.Text)
	

	RemainedTask = len(ParagraphDataList)
	Task_todo = []
	print('RemainedTask', RemainedTask)
	
	
	
	while len(ParagraphDataList) > 0:
		Translated = []
		TaskLength = 0
			
		while TaskLength < 2000:
			if len(ParagraphDataList) > 0:
				Input = ParagraphDataList[0].Text
				if isinstance(Input, list):
					TempLen = TaskLength
					for tempString in Input:
						TempLen += len(tempString)
		
				elif isinstance(Input, str):
					TempLen = TaskLength + len(ParagraphDataList[0].Text)
					
				if TempLen < 2000:
					TaskLength = TempLen
					#print("TempLen", TempLen)
					Task_todo.append(ParagraphDataList[0])
					del ParagraphDataList[0]
				else:
					break	
			else:
				break

		Translated = cell_translate(Mytranslator, Task_todo)

		for task in Translated:
			Return = task
			Current_Par = Return.Paragraph
			Current_Run = Return.Run
			Current_Text = Return.Text
			Mydocx.paragraphs[Current_Par].runs[Current_Run].text = Current_Text

		
		RemainedTask = len(ParagraphDataList)
		Counter += RemainedTask
		percent = ShowProgress(Counter, TotalTask)
		ProgressQueue.put(percent)
		del Task_todo
		Task_todo = []
	
	for table in Mydocx.tables:

		result = translatetable(table, Mytranslator, Counter, TotalTask)

		table = result[0]
		Counter = result[1]
		percent = ShowProgress(Counter, TotalTask)
		ProgressQueue.put(percent)

	percent = ShowProgress(TotalTask, TotalTask)
	ProgressQueue.put(percent)
	StatusQueue.put('Exporting...')
	print('Exporting')
	try:
		Mydocx.save(OutputDocument)
		if (os.path.isfile(OutputDocument)):
			End = time.time()
			Message = "Total time spend: " + str(int(End-Start)) + ' seconds.'
			StatusQueue.put(Message)
			return True
		else:
			StatusQueue.put('Fail to export file')
			return False
	except Exception as e:
		StatusQueue.put('Error message: ' + str(e))
		return e

def Estimatetables(intable):
	total = 0
	for row in intable.rows:
		for cell in row.cells:
			for paragraph in cell.paragraphs:

				for run in paragraph.runs:
					runtext = run.text
					if runtext != "":
						if not runtext.isdigit():
							total+= 1
			for table in cell.tables:
				total+= Estimatetables(table)			
	return total

def translatetable(intable, Mytranslator, CurrentTask, TotalTask, TaskPool = 4):
	from docx.shared import RGBColor

	#tasks_to_accomplish = Queue()
	#tasks_that_are_done = Queue()
	
	for row in intable.rows:
		for cell in row.cells:
			for paragraph in cell.paragraphs:
				FirstRun = None
				CurentText = ""
				for j in range(len(paragraph.runs)):
					run = paragraph.runs[j]
					if FirstRun == None:
						FirstRun = j		

					if run.text == '':
						if CurentText != '':
							#print('CurentText ', CurentText)
							ListText = CurentText.split('\n')
							#print('ListText ', ListText)
							Translated = Mytranslator.translate(ListText)
							Translated = "\n".join(Translated)
							#Translated = Translated.replace("\r\r\n", "\r\n")
							#print('Translated ', Translated)
							paragraph.runs[FirstRun].text = Translated
						FirstRun = None
						CurentText = ""
					else:
						CurentText += str(run.text)
						run.text = ""
				if CurentText != '':
					#print('CurentText ', CurentText)
					ListText = CurentText.split('\n')
					#print('ListText ', ListText)
					Translated = Mytranslator.translate(ListText)
					Translated = "\n".join(Translated)
					#Translated = Translated.replace("\r\r\n", "\r\n")
					#print('Translated ', Translated)
					paragraph.runs[FirstRun].text = Translated

				CurrentTask+=1
				
			for table in cell.tables:
				print('Another table inside a table celll.')
				translatetable(table, Mytranslator, CurrentTask, TotalTask)

	return [intable, CurrentTask]

#**********************************************************************************
# UI handle ***********************************************************************
#**********************************************************************************

def translateDPF(ProgressQueue=None, ResultQueue=None, StatusQueue=None, Mytranslator=None, Options = {}):
	from pathlib import Path
	from PyPDF2 import PdfFileReader

	from docx import Document
	from docx.shared import Inches

	document = Document()

	print('Estimating total work to do...')
	StatusQueue.put('Estimating total task to do...')
	ProgressQueue.put(0)
	
	if not 'SourceDocument' in Options:
		StatusQueue.put('No source document input')
		return False
	else:
		SourceDocument = Options['SourceDocument']

	if not 'OutputDocument' in Options:
		now = datetime.now()
		timestamp = str(int(datetime.timestamp(now)))
		Outputdir = os.path.dirname(SourceDocument)
		baseName = os.path.basename(SourceDocument)
		sourcename = os.path.splitext(baseName)[1]
		OutputDocument = Outputdir + '/' + 'Translated_' + sourcename + '_' + timestamp + ".docx"
	else:
		OutputDocument = Options['OutputDocument']

	#OutputDocument_Path = Path(OutputDocument)

	
	'''
	if Multiple < multiprocessing.cpu_count() or Multiple == None:
		TaskPool = multiprocessing.cpu_count()
	elif Multiple > multiprocessing.cpu_count()*10:
		TaskPool = multiprocessing.cpu_count() * 5
	else:
		TaskPool = Multiple
	'''

	Start = time.time()

	pdf_reader = PdfFileReader(str(SourceDocument))
	

	#title = pdf_reader.documentInfo.title
	#num_pages = pdf_reader.getNumPages()
	#output_file.write(f"{title}\\nNumber of pages: {num_pages}\\n\\n")

	DraftText = ""	
	# 4
	for page in pdf_reader.pages:
		text = page.extractText()
		DraftText += text

		DraftText.replace('\n', "")
		#SingleText =  ""

		print('Text:', text)
		translated = Mytranslator.translate(text)
		#output_file.write(translated)
		document.add_paragraph(translated)

	try:
		document.save(OutputDocument + '.docx')
		if (os.path.isfile(OutputDocument+ '.docx')):
			End = time.time()
			Message = "Total time spend: " + str(int(End-Start)) + ' seconds.'
			StatusQueue.put(Message)
			return True
		else:
			StatusQueue.put('Fail to export file')
			return False
	except Exception as e:
		StatusQueue.put('Error message: ' + str(e))
		return e
	
	'''
	try:
		document.save(OutputDocument + '.docx')
		if (os.path.isfile(OutputDocument+ '.docx')):
			End = time.time()
			Message = "Total time spend: " + str(int(End-Start)) + ' seconds.'
			StatusQueue.put(Message)
			return True
		else:
			StatusQueue.put('Fail to export file')
			return False
	except Exception as e:
		StatusQueue.put('Error message: ' + str(e))
		return 'Error message: ' + str(e)
	'''

#**********************************************************************************
# UI handle ***********************************************************************
#**********************************************************************************

def translateMsg(ProgressQueue=None, ResultQueue=None, StatusQueue=None, Mytranslator=None, Options = {}):
	from outlook_msg import Message
	from docx import Document
	from docx.shared import Inches

	print('Estimating total work to do...')
	StatusQueue.put('Estimating total task to do...')
	ProgressQueue.put(0)
	
	if not 'SourceDocument' in Options:
		StatusQueue.put('No source document input')
		return False
	else:
		SourceDocument = Options['SourceDocument']

	if not 'OutputDocument' in Options:
		now = datetime.now()
		timestamp = str(int(datetime.timestamp(now)))
		Outputdir = os.path.dirname(SourceDocument)
		baseName = os.path.basename(SourceDocument)
		sourcename, ext = os.path.splitext(baseName)
		OutputDocument = Outputdir + '/' + 'Translated_' + sourcename + '_' + timestamp + ext
	else:
		OutputDocument = Options['OutputDocument']

	Start = time.time()
	
	Counter = 0
	TotalTask = 0

	document = Document()

	with open(SourceDocument) as msg_file:
		msg = Message(msg_file)

	contents = msg.body
	subject = msg.subject
	translated = Mytranslator.translate(subject)	
	document.add_heading(translated, 0)

	para = contents.split('\n')
	TotalTask += len(para)
	Counter = 0
	for Par in para:
		if Par not in ["", ' ', '\r', '\n']:
			translated = Mytranslator.translate(Par)
			document.add_paragraph(translated)
			Counter+=1
			ShowProgress(Counter, TotalTask)
	try:
		document.save(OutputDocument + '.docx')
		if (os.path.isfile(OutputDocument+ '.docx')):
			End = time.time()
			Message = "Total time spend: " + str(int(End-Start)) + ' seconds.'
			StatusQueue.put(Message)
			return True
		else:
			StatusQueue.put('Fail to export file')
			return False
	except Exception as e:
		StatusQueue.put('Error message: ' + str(e))
		return e
