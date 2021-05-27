#Regular expression handling
import re
#http request and parser
import html.parser
import urllib.request
import urllib.parse
from urllib.parse import urlparse
import html
import requests, uuid, json

from google.cloud import translate_v3 as translate
from google.cloud import storage
from google.cloud import logging


#import numpy as np

# Base64 convert
import base64
#System lib
import os
import sys, getopt
import unicodedata
import string
#from unicodedata import category

import pickle
import time
from datetime import datetime

#MyTranslatorAgent = 'googleapi'
Tool = "Translator lib"
#VerNum = '3.4.0d'
rev = 3411
a,b,c,d = list(str(rev))
VerNum = a + '.' + b + '.' + c + chr(int(d)+97)
TranslatorVersion = Tool + " " + VerNum

#AIOTracker.GenerateToolUsageEvent(version)
#whitespace = ' \t\n\r\v\f'
#ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
#ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#ascii_letters = ascii_lowercase + ascii_uppercase
#digits = '0123456789'
#hexdigits = digits + 'abcdef' + 'ABCDEF'
#octdigits = '01234567'
#punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""


class Translator:
	def __init__(self, 
		From_Language = 'auto', 
		To_Language = 'en', 
		PredictMode = True, 
		ProactiveTMTranslate=True, 
		TMUpdate=True, 
		GlossaryID = None, 
		TMManager = None,
		TM_Path = None,
		Tool = 'writer',
		ToolVersion = None,
	):
		
		self.From_Language = From_Language
		self.To_Language = To_Language	
		self.DefaultException = ['pass', 'fail', 'n/a', 'n/t', 'result', '\t', '\r', '\n', '', '\r\n', ' ', 'sort', 'function', 'data' , 'x', 'o']

		#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= License_Path
		#print(License_Path)
		#self.Key = APIKey
		#self.Subscription = Subscription
		#self.SubscriptionKey = SubscriptionKey

		self.PredictMode = PredictMode
		self.TMUpdate = TMUpdate
		self.ProactiveTMTranslate = ProactiveTMTranslate

		self.Tool = Tool
		self.ToolVersion = ToolVersion

		self.ProjectID = None

		self.Project_Bucket_ID = 'credible-bay-281107'
		self.Load_ProjectID()

		self.GlossaryID = GlossaryID
		self.Location = "us-central1"


		self.GlossaryList = []	
		self.GlossaryDataList = []
		
		if sys.platform.startswith('win'):
			self.config_path = os.environ['APPDATA']
		else:
			self.config_path = os.getcwd()

		if TM_Path != None:
			if os.path.isfile(TM_Path):
				self.TM_Path = TM_Path
			else:
				self.TM_Path = self.config_path + '\\AIO Translator\\Local.pkl'
		else:
			self.TM_Path = self.config_path + '\\AIO Translator\\Local.pkl'		

		if self.Tool == 'document':
			self.tracking_log = self.config_path + '\\AIO Translator\\d_logging.pkl'
			self.invalid_request_log = self.config_path + '\\AIO Translator\\d_invalid_request_logging.pkl'
			self.tm_request_log = self.config_path + '\\AIO Translator\\d_tm_request_logging.pkl'
			#self.false_request = self.config_path + '\\AIO Translator\\false_request.pkl'
		else:
			self.tracking_log = self.config_path + '\\AIO Translator\\logging.pkl'
			self.invalid_request_log = self.config_path + '\\AIO Translator\\invalid_request_logging.pkl'
			self.tm_request_log = self.config_path + '\\AIO Translator\\tm_request_logging.pkl'
			self.TM_Path = None
			#self.false_request = self.config_path + '\\AIO Translator\\false_request.pkl'

		self.OS = 'win'

		if not sys.platform.startswith('win'):
			if self.TM_Path != None:
				self.TM_Path = str(self.TM_Path).replace('\\', '//')
			self.tracking_log = str(self.tracking_log).replace('\\', '//')
			#self.false_request = str(self.false_request).replace('\\', '//')
			self.OS = 'mac'

		self.SpecialSheets = ['kr_only', 'en_only', 'name']

		if TMManager != None:
			self.TMManager = TMManager
		else:
			self.TMManager	= []

	
		self.Dictionary = []

		self.KRDictionary = []
		self.ENDictionary = []

		self.Header = []
		self.Name = []
		self.Version = '-'
		self.UpdateDay = '-'
		self.Exception = []
		self.TemporaryTM = []
		self.TranslationMemory = []
		self.TranslationMemorySize = 0
		#self.ko_tm = np.array([])
		#self.en_tm = np.array([])
		self.KO = []
		self.EN = []

		self.Header = None
		
		self.Exception_Char = string.punctuation + string.digits
		self.Accepted_Char = string.punctuation 
		self.Printable = string.printable
		self.banned = False

		try:
			self.get_user_name()
		except:
			self.UserName = "Anonymous"

		try:
			self.get_pc_name()
		except:
			self.PcName = "Anonymous"

		self.latest_version = 0
		
		try:
			self.load_bucket_list_from_glob()
			self.prepare_db_data()
		except Exception as e:
			print("E:", e)
			print('Fail to load db')

		tracking_result = self.send_tracking_record()
		print('Tracking status:', tracking_result)

		self.Last_Section_TM_Request = 0
		self.Last_Section_Invalid_Request = 0
		self.Last_Section_API_Usage = 0



	def Load_ProjectID(self):
		try:
			License = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
			with open(License, 'r') as myfile:
				data=myfile.read()
			obj = json.loads(data)
			self.ProjectID = obj['project_id']
		except:
			self.ProjectID = 'credible-bay-281107'

	def ActiveTranslator(self, Source_Text):
		count = 0
		try:
			if isinstance(Source_Text, list):
				for c in Source_Text:
					count+= len(c)
			elif isinstance(Source_Text, str):
				count+= len(Source_Text)
			else:
				return False
		except:
			pass
		
		if self.banned == True:
			return
		
		try:	
			if self.Project_Bucket_ID != self.ProjectID:
				translation = self.GoogleAPItranslateV3(Source_Text)
			else:
				translation =  self.GoogleGlossaryTranslate(Source_Text)
		except Exception as e:
			print('error translation:', e)
			try:
				client = logging.Client()
			except:
				pass

			log_name = 'translator-error'
			logger = client.logger(log_name)	
			text_log = self.UserName + ', ' + self.PcName + ', ' + self.GlossaryID + ', ' + str(e)

			try:
				logger.log_text(text_log)
			except:
				pass
			translation = False
		#print('translation', translation)
		if translation != False:
			#print('TM usage:', count)
			self.Append_API_Usage_Logging(count)

		return translation	

	def Init_Glossary(self):
		self.Client = translate.TranslationServiceClient()	
		self.Parent = f"projects/{self.ProjectID}/locations/{self.Location}"
		self.Glossary = self.Client.glossary_path(self.ProjectID, self.Location, self.GlossaryID)
		self.Glossary_Config = translate.TranslateTextGlossaryConfig(glossary=self.Glossary)

	def GetTimeStamp(self):
		now = datetime.now()
		year =  now.isocalendar()[0]
		week =  now.isocalendar()[1]
		return str(year) + "_" + str(week)

	
	
	def GetGlossaryList(self):
		print('Getting Glossary info')
		self.GlossaryList = []
		self.GlossaryListFull = self.full_list_glossaries()
		print('GlossaryListFull', self.GlossaryListFull)
		for Gloss in self.GlossaryListFull:
			Gloss = Gloss.split('/')[-1]
			if '_' not in Gloss:
				self.GlossaryList.append(Gloss)		

	def RefreshTranslationMemory(self):
		#self.ImportNumTranslationMemory()
		self.ImportTranslationMemory()
		#print('New TM length: ', str(len(self.TranslationMemory)))

	# Add a KR-EN pair into TM
	def GenerateTM(self, Translated="", Input=""):
		#print("Adding a pair to Temp TM")
		Translated = Translated.lower()
		Input = Input.lower()
		if self.To_Language == 'ko':
			Pair = [Translated, Input]
		else: 
			Pair = [Input, Translated]
		#print('Old size:', self.TMManager)
		#print("append tm:", Pair)
		try:
			index = self.TMManager.index(Pair)
			if index != -1:
				return
		except Exception as e:
			#print('Error:', e)		
			pass
		self.TMManager.append(Pair)
		print('New size:', len(self.TMManager))

	def load_request_log(self, log_file):

		if not os.path.isfile(log_file):
			amount = 0
		else:
			try:
				with open(log_file, 'rb') as pickle_load:	
					amount = pickle.load(pickle_load)
					#print('loaded amount: ', amount)
			except:
				amount = 0
		return amount

	def Append_TM_Request_Logging(self, add_num=0):
		
		if add_num == 0:
			return

		log_file = self.tm_request_log	
		amount = self.load_request_log(log_file)

		amount += add_num
		#print('Append tm usage:', add_num, amount )
		try:
			with open(log_file, 'wb') as pickle_file:
				pickle.dump(amount, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
		except:
			pass

	def Append_Invalid_Request_Logging(self, add_num=0):
		
		if add_num == 0:
			return

		log_file = self.invalid_request_log	
		amount = self.load_request_log(log_file)

		amount += add_num

		try:
			with open(log_file, 'wb') as pickle_file:
				pickle.dump(amount, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
		except:
			pass
	
	def Append_API_Usage_Logging(self, add_num=0):
		log_file = self.tracking_log
		if add_num == 0:
			return
		amount = self.load_request_log(log_file)

		amount += add_num
		#print('Append translator usage:', add_num, amount )
		try:
			with open(log_file, 'wb') as pickle_file:
				pickle.dump(amount, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
		except:
			pass
	
	def Simple_Optmize(self):
		count = 0
		for text in self.EN:
			text = text.lower()
			count+=1
		for text in self.KO:
			text = text.lower()
			count+=1
		self.Optmized = True
		self.AppendTranslationMemory()
		print('Count:', count)
		print('Done')

	def OptimizeTranslationMemory(self):
		print('Optimizing TM...')
		New_EN = []
		New_KO = []
		print('Old TM:', len(self.EN))
		counter = 0
		for text in self.EN:
			#print('Appending:', text)
			simple =  text.lower()
			#text = text.lower
			if simple not in New_EN:
				try:
					index = self.EN.index(text)	
				except:
					continue
			
			counter+=1
			if counter % 10000 == 0:
				print('Appending:', text, counter)
			New_EN.append(self.EN[index].lower())
			New_KO.append(self.KO[index].lower())
			
		del self.EN
		self.EN = New_EN
		del self.KO
		self.KO = New_KO
		print('New TM:', len(self.EN))	

		self.Optmized = True
		print('Optmize TM completed...')

	def remove_tm_pair(self, index=[]):
		if isinstance(index, int):
			list_to_remove = [index]
		elif isinstance(index, list):
			list_to_remove = index
		else:
			return False	

		self.ImportTranslationMemory()
		for i in list_to_remove:
			#print('Current index:', i)
			self.EN[i] = None
			self.KO[i] = None
		
		self.EN = list(filter(None, self.EN))
		self.KO = list(filter(None, self.KO))	

		self.TranslationMemory = {}
		self.TranslationMemory['EN'] = self.EN
		self.TranslationMemory['KO'] = self.KO
		#self.TranslationMemory['Optmized'] = self.Optmized
		with open(self.TM_Path, 'wb') as pickle_file:
			print("Updating pickle file....", self.TM_Path)
			pickle.dump(self.TranslationMemory, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)


	def AppendTranslationMemory(self):
		new_tm_size = len(self.TMManager)
		print('Size of new TM: ', new_tm_size)
		if len(self.TMManager) > 0:
			while True:
				self.ImportTranslationMemory()
				for NewPair in self.TMManager:
					#print('Append pair:', NewPair)
					try:
						index_en = self.EN.index(NewPair[1])
						index_ko = self.KO.index(NewPair[0])
					except:						
						self.EN.append(NewPair[1])
						self.KO.append(NewPair[0])
					#self.TranslationMemory.append(NewPair)
				
				self.TranslationMemory = {}
				self.TranslationMemory['EN'] = self.EN
				self.TranslationMemory['KO'] = self.KO
				#self.TranslationMemory['Optmized'] = self.Optmized
				try:
					with open(self.TM_Path, 'wb') as pickle_file:
						print("Updating pickle file....", self.TM_Path)
						pickle.dump(self.TranslationMemory, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
					print('Remove TM in memory')
					self.TMManager[:]
					print('Size TM in memory', len(self.TMManager))
					return new_tm_size
				except Exception as e:
					print("Error:", e)
					pass
		return new_tm_size

	def send_tracking_record(self,file_name = None):

		self.Last_Section_API_Usage = self.load_request_log(self.tracking_log)
		print('translate-usage:', self.Last_Section_API_Usage)
		self.Last_Section_TM_Request = self.load_request_log(self.tm_request_log)
		print('tm-usage:', self.Last_Section_TM_Request)
		self.Last_Section_Invalid_Request = self.load_request_log(self.invalid_request_log)
		print('invalid-request:', self.Last_Section_Invalid_Request)
		result = True
		
		try:
			client = logging.Client()
		except Exception as e:
			print('Exception:', e)
			return False
		
		if self.Last_Section_API_Usage > 0 or self.Last_Section_TM_Request > 0:
			log_name = 'translator-usage'

			logger = client.logger(log_name)
			'''
			tracking_object = {
				'user': self.UserName,
				'device': self.PcName,
				'project': self.GlossaryID,
				'tool': self.Tool,
				'tool_ver': self.ToolVersion,
				'translator_ver': VerNum,
				'api_usage': self.Last_Section_API_Usage,
				'tm_usage': self.Last_Section_TM_Request,
				'invalid_request': self.Last_Section_Invalid_Request,
				'tm_size': self.TranslationMemorySize,
				'tm_path': self.TM_Path
			}
			'''
			data_object = {
				'device': self.PcName,
				'project': self.GlossaryID,
				'tool': self.Tool,
				'tool_ver': self.ToolVersion,
				'translator_ver': VerNum,
				'api_usage': self.Last_Section_API_Usage,
				'tm_usage': self.Last_Section_TM_Request,
				'invalid_request': self.Last_Section_Invalid_Request,
				'tm_size': self.TranslationMemorySize,
				'tm_path': self.TM_Path
			}
			if 	file_name != None:
				data_object['file_name'] = file_name

			tracking_object = {
				'user': self.UserName,
				'details': data_object
			}
			
			try:
				logger.log_struct(tracking_object)
				if self.Last_Section_API_Usage > 0:
					os.remove(self.tracking_log)
				if self.Last_Section_TM_Request > 0:
					os.remove(self.tm_request_log)
				if self.Last_Section_Invalid_Request > 0:
					os.remove(self.invalid_request_log)	
			except Exception as e:
				print('Exception:', e)
				result = False
		
		return result

	def get_user_name(self):
		if self.OS == 'win':
			try:
				self.UserName = os.getlogin()
			except:
				self.UserName = os.environ['COMPUTERNAME']
		else:
			try:
				self.UserName = os.environ['LOGNAME']
			except:
				pass

	def get_pc_name(self):
		if self.OS == 'win':
			try:
				self.PcName = os.environ['COMPUTERNAME']
			except:
				self.PcName = "Anonymous"
		else:
			try:
				self.PcName = os.environ['LOGNAME']
			except:
				self.PcName = "Anonymous"

	# Very IMPORTANT function
	# This function is used to sort the Database object (descending)
	# Allow us to check the long word before the sort one:
	# E.g. 'pine apple' will be perfer to lookup first, 
	# if there is no 'pine apple' exist, we will looking for 'apple' in the sentence.
	def SortDictionary(self, List):
		if self.From_Language == 'ko':
			#return(sorted(self.Dictionary, key = lambda x: x[0], reverse = True))
			#NewList = sorted(self.Dictionary, key = lambda x: x[0], reverse = True)
			#return(sorted(NewList, key = len, reverse=True))
			return(sorted(List, key = lambda x: (len(x[0]), x[0]), reverse = True))
		else:
			#return(sorted(self.Dictionary, key = lambda x: x[1], reverse = True))
			#NewList = sorted(self.Dictionary, key = lambda x: x[1], reverse = True)
			#return(sorted(NewList, key = len, reverse=True))
			return(sorted(List, key = lambda x: (len(x[1]), x[1]), reverse = True))
			
	# This function is used to ignore any word present in this list
	# E.g. if a cell contains the text Fail (the TC result), the tool won't translate this cell.
	# The default list can be easily check by Simple Translator tool.
	# The exception list in the exception file is not support by Translator tool.
	def ValidateException(self, string):

		string = str(string).lower()

		try:
			exception_list = self.Exception + self.DefaultException
		except:
			exception_list = self.DefaultException

		for X in exception_list: 
				if string.strip() == X.lower().strip():
					return False
		return True	

	
	# Similar to ValidateException, will allow us to ignore the string that does not contain any Korean character (Only work for KR -> EN)
	# E.g. if a cell contains the text Fail (the TC result), the tool won't translate this cell.
	# Can be easily check by Simple Translator tool.
	def ValidateLanguageSource(self, string):
		if self.From_Language == 'ko':
			for i in range(len(string)):
				c = string[i]
				if unicodedata.category(c)[0:2] == 'Lo' : # other characters
					try:
						if 'HANGUL' in unicodedata.name(c) : return True
					except:
						continue
			return False
		else:
			for i in range(len(string)):
				c = string[i]
				if unicodedata.category(c)[0:2] == 'Ll' : # other characters
					try:
						if 'LATIN' in unicodedata.name(c) : return True
					except:
						continue
			return False

	def ValidateUnicodeSource(self, string):
		for i in range(len(string)):
			c = string[i]
			category = unicodedata.category(c)[0:1]
			if category == 'L': # other characters
				return True
		return False

	# Similar to ValidateException, will allow us to ignore the string is in the URL format
	# E.g. if a cell contains the text "httl://google.com", it won't be translated
	# Can be easily check by Simple Translator tool.

	def ValidateURL(self, string):

		Result = urlparse(string)
		
		try:
			if Result.scheme == "" or Result.netloc == "":
				return False
			else:
				return True
		except:
			return False

	def ValidateSourceText(self, Source_Text):
		
		Source_Text = Source_Text.lower()
		
		result = True

		if self.ValidateException(Source_Text) == False:
			result = False

		# Prevent case that the source text contain some special character.
		elif self.ValidateURL(Source_Text) == True:
			#print('URL, wont translate!')
			result = False

		elif self.ValidateLanguageSource(Source_Text) == False:
			result = False

		#if self.ValidateUnicodeSource(Source_Text) == False:
		#	return False
			
		elif self.ProactiveTMTranslate == True:
			
			Translated = self.MemoryTranslate(Source_Text)
			#print('TM Translate:', Source_Text, '-->', Translated)
			if Translated != False:
				
				result = Translated	

		#self.invalid_request_log
		if not isinstance(result, bool):
			count = 0
			try:
				if isinstance(Source_Text, list):
					for c in Source_Text:
						count+= len(c)
				elif isinstance(Source_Text, str):
					count+= len(Source_Text)
			except Exception as e:
				print('Error message: ', e)
				pass
			#print('Append tm usage:', count)
			self.Append_TM_Request_Logging(count)
		elif result == False:
			count = 0
			try:
				if isinstance(Source_Text, list):
					for c in Source_Text:
						count+= len(c)
				elif isinstance(Source_Text, str):
					count+= len(Source_Text)
			except Exception as e:
				print('Error message: ', e)
				pass

			self.Append_Invalid_Request_Logging(count)
		#print('Validate result: ', result)
		return result
		

	def EnglishPreTranslate(self, source_text):
		#print('English pre-translate')
		# Use for Translating KR -> EN
		# Add 2 space to the dict to prevent the EN character and KO character merge into 1
		# because the translator API cannot handle those.
		RawText = source_text
		LowerCase_text = source_text
		
		temp_dict = self.Dictionary + self.KRDictionary

		for pair in temp_dict:
			# Old is EN text in the dict
			Old = pair[0].strip()
			
			# New is the KR text we want to replace with
			New = " " + pair[1].strip() + " "
			#New = pair[1].strip()
			# IF there is the defined text in the sentence
			StartFind = 0
			while LowerCase_text.find(Old, StartFind) != -1:
				#print('ENglish pretrans')
				# Find the location of the text in the sentence
				Location = int(LowerCase_text.find(Old, StartFind))
				# And the text length
				TextLen = len(Old)
				StartFind = Location + TextLen
				FirstChar = None
				NextChar = None
				# If the text is not in the begin of the sentence
				# E.g. "NewWord XXX" or "XXX [Word] XXX"
				if Location > 0:
					try:
						FirstChar = LowerCase_text[Location-1]
					except:
						FirstChar = ""
				else:
					FirstChar = ""
				# Find the character stand right after the text (first char)
				# E.g. "w" or "["
				try:
					NextChar = LowerCase_text[StartFind] 
				except:
					NextChar = ""
				#AllowedChar = '[](){}:.,-_<>!\"\' '
				
				# Find the character stand right before the text (last char)
				# E.g. " " or "]"
				# Check if the (first char) is alphabet or not
				#print('FirstChar', FirstChar)
				#print('NextChar', NextChar)
				#print('FirstChar', FirstChar, 'NextChar', NextChar)
				if self.Accepted_Char.find(FirstChar) != -1 or FirstChar in [ None,  "", " "]:
					
					# If the (first char) is a alphabet, this is not the word we're looking for
					# E.g. 'Work' is exist in 'homework' but it's not the exact text we're looking for
					if self.Accepted_Char.find(NextChar) != -1 or NextChar in [ None,  "", " "]:
						# If the (first char) is a alphabet, this is not the word we're looking for
						# If the (last char) is a alphabet, this is not the word we're looking for
						# E.g. 'Work' is exist in 'workout' but it's not the exact text we're looking for
						#print('Source: ', source_text)
						#print('Valid 1st char: ', FirstChar)
						#print('Valid end char: ', NextChar)
						Raw_Old = RawText[Location:StartFind]
						#print('Raw_Old', Raw_Old)
						RawText = RawText.replace(FirstChar + Raw_Old + NextChar, FirstChar + New + NextChar, 1)
						
						#RawText[Location, StartFind-1] = RawText

						#print('Replace: ', FirstChar + Old + NextChar, ' by ',  FirstChar + New + NextChar)
					else:
						#print('ORD', ord(NextChar))
						#print('Invalid NextChar char: \'', NextChar, '\'')
						continue
				else:
					#rint('ORD', ord(FirstChar))
					#print('Invalid 1st char: \'', FirstChar, '\'')
					continue
				LowerCase_text = RawText	
		# Remove the space from both side of the text
		# The space that we've add above.
		RawText = RawText.strip()
		#print('RawText', RawText)
		return RawText

	def KoreanPreTranslate(self, input):
		# Use for Translating EN -> KR
		# It's a litle complicated....
		# To cover some special case can happen.
		RawText = input
		source_text = RawText.lower()
			
		temp_dict = self.Dictionary + self.ENDictionary
	
		for pair in temp_dict:
			# Old is EN text in the dict
			Old = pair[1].strip()
			
			# New is the KR text we want to replace with
			New = " " + pair[0].strip() + " "
			#print('KoreanPreTranslate Replacing ', Old, New)
			# IF there is the defined text in the sentence
			StartFind = 0
			while source_text.find(Old) != -1:
				#print('source_text', source_text)		
				# Find the location of the text in the sentence
				Location = source_text.find(Old)
				# And the text length
				TextLen = len(Old)
				StartFind = Location + TextLen
				FirstChar = ""
				NextChar = ""
				# If the text is not in the begin of the sentence
				# E.g. "NewWord XXX" or "XXX [Word] XXX"
				if Location != 0:
					try:
						FirstChar = source_text[Location-1]
					except:
						FirstChar = "" 
				else:
					FirstChar = ""
				# Find the character stand right after the text (first char)
				# E.g. "w" or "["
				try:
					NextChar = source_text[Location+TextLen] 
				except:
					NextChar = "" 
				# Find the character stand right before the text (last char)
				# E.g. " " or "]"
				# Check if the (first char) is alphabet or not
				
				if re.match("^[a-zA-Z-_]", FirstChar) != None:
					# If the (first char) is a alphabet, this is not the word we're looking for
					# E.g. 'Work' is exist in 'homework' but it's not the exact text we're looking for
					break
				elif re.match("^[a-zA-Z-_]", NextChar) != None:
					# If the (last char) is a alphabet, this is not the word we're looking for
					# E.g. 'Work' is exist in 'workout' but it's not the exact text we're looking for
					break	
				else:
					# out of these defined case, we replace the text with the defined one.
					#print('Start:', Location, "End:", StartFind, 'len:', len(RawText))
					Raw_Old = RawText[Location:StartFind]
					#print('Raw Old', Raw_Old, 'Old', Old)
					RawText = RawText.replace(Raw_Old, New, 1)
					#print("RawText", RawText)
				source_text = RawText.lower()
		# Remove the space from both side of the text
		# The space that we've add above.
		RawText = RawText.strip()
		return RawText



	# Translator main function.
	# All the text will be passed into this function.
	def translate(self, Input):
		if isinstance(Input, list):
			Source_Text = Input
		elif isinstance(Input, str):
			Source_Text = [Input]
		else:
			return False
		#ResultType = ''
		# Check if the whole text is defined in the exception list or not.
		# If true, return the Text without translating it.
		'''
		if self.ValidateException(Source_Text) == False:
			#print('Exception, wont translate!')
			return Source_Text
		'''
		#if Source_Text.isnumeric() == True:
		#	print('Number, wont translate!')
		#	return Source_Text

		# Check if the whole text is a number or not
		# If true, return the number without translating it.
		raw_source = []
		to_translate = []
		to_translate_index = []
		translation = []
	
		for text in Source_Text:
			translation.append(text)

		
		for i in range(len(translation)):
			text = str(translation[i])
			
			Validation = self.ValidateSourceText(text)
			#print('Details:', text, 'Result:', Validation)
			if Validation == False:
				continue
			if Validation == True:
				try:
					index_num = raw_source.index(text)
					to_translate_index[index_num].append(i)
				except Exception as e:
					if self.To_Language == 'ko':
						pre_translate = self.KoreanPreTranslate(text)
					else:
						pre_translate = self.EnglishPreTranslate(text)
					
					raw_source.append(text)
					to_translate.append(pre_translate)
					to_translate_index.append([i])

				#raw_source.append(text)
				#to_translate.append(pre_translate)
				#to_translate_index.append(i)
			else:
				#Translated by memory
				translation[i] = Validation

		#print('to_translate', to_translate)
		if len(to_translate) > 0:
			try:
				Translated = self.ActiveTranslator(to_translate)
			except Exception as e:
				print('error:', e)
				Translated = []
		
		else:
			Translated = []	
		#print('raw', raw_source)
		#print('to_translate', to_translate)
		#print('Translated', Translated)	
		#print('to_translate_index', to_translate_index)	
		'''
		if not isinstance(Translated, list):
			return [Translated]
		else:
			for i in range(len(Translated)):
				translation[to_translate_index[i]] = Translated[i]
		'''
		for i in range(len(Translated)):
			for index_number in to_translate_index[i]:
				translation[index_number] = Translated[i]
			#translation[to_translate_index[i]] = Translated[i]
			if self.TMUpdate == True:
				#print('Append TM: ', Translated[i], raw_source[i] )
				self.GenerateTM(Translated[i], raw_source[i])
		'''
		if self.TMUpdate == True and len(to_translate) > 0:
			
			for i in range(len(Translated)):
				translated_result = Translated[i]
				if translated_result != False:
					input_text = raw_source[i]
					
					self.GenerateTM(translated_result, input_text)
		'''
		if isinstance(Input, str):
			return translation[0]
		else:
			return translation
	
	
	def translate_v3(self, Input):
		
		if isinstance(Input, list):
			Source_Text = Input
		elif isinstance(Input, str):
			Source_Text = [Input]
		else:
			return False
		#ResultType = ''
		# Check if the whole text is defined in the exception list or not.
		# If true, return the Text without translating it.
		'''
		if self.ValidateException(Source_Text) == False:
			#print('Exception, wont translate!')
			return Source_Text
		'''
		#if Source_Text.isnumeric() == True:
		#	print('Number, wont translate!')
		#	return Source_Text

		# Check if the whole text is a number or not
		# If true, return the number without translating it.
		
		to_translate = []
		to_translate_index = []
		translation = []
		print('Source_Text', Source_Text)
		for text in Source_Text:
			translation.append(text)

		#print('translation', translation)
		for i in range(len(translation)):
			text = translation[i]
			Validation = self.ValidateSourceText(text)
			if Validation == False:
				continue
			if Validation == True:
				to_translate.append(text)
				to_translate_index.append(i)
			else:
				#Translated by memory
				text = Validation

		Translated = self.ActiveTranslator(to_translate)
		'''
		if not isinstance(Translated, list):
			return [Translated]
		else:
			for i in range(len(Translated)):
				translation[to_translate_index[i]] = Translated[i]
		'''
		for i in range(len(Translated)):
			translation[to_translate_index[i]] = Translated[i]


		Translated = self.ActiveTranslator(to_translate)
		#print(Translated)
		if self.TMUpdate == True:
			for i in range(len(Translated)):
				translated_result = Translated[i]
				if translated_result != False:
					input_text = to_translate[i]
					#print('Append memory: ', translated_result, input_text)
					self.GenerateTM(translated_result, input_text)
		if isinstance(Input, str):
			return translation[0]
		else:
			return translation


	# If Translation Memory is exist, replace the text with the defined one.
	# This method can speed up the translate progress x100 time 
	# and improve the translation speed.
	def MemoryTranslate(self, Source_Text):
		#print("mem translate", self.TMManager)
		# Use the previous translate result to speed up the translation progress
		try:
			#print('self.To_Language', self.To_Language )
			#print('Source_Text', Source_Text)
			if self.To_Language == 'ko':
				#print('Translate to KO')
				index = self.EN.index(Source_Text)
				#print('Source_Text', Source_Text)
				#print('index', index)
				print('TM translate:', Source_Text, self.KO[index])
				return self.KO[index]
			else:
				#print('Translate to EN')
				index = self.KO.index(Source_Text)
				#print('Source_Text', Source_Text)
				#print('index', index)
				print('TM translate:', Source_Text, self.EN[index])
				return self.EN[index]	
		except Exception as e:
			pass
		#for pair in self.TranslationMemory:
		#	if pair[x] == Source_Text:
		#		print('mem trans',time.time()- st)
		#		return pair[y]
		if self.To_Language == 'ko':
			x = 1
			y = 0
		else: 
			x = 0
			y = 1
		
		if self.TMManager != None:
			for pair in self.TMManager:
				if pair[x] == Source_Text:
					#print('mem trans',time.time()- st)
					#print('Temp TM translate:', Source_Text, pair[y])
					#print('Translated by TM')
					return pair[y]
		#print('mem trans',time.time()- st)
		
		return False


	def MemoryTranslateExecute(self, source_text):
		# Use the previous translate result to speed up the translation progress
		if self.To_Language == 'ko':
			x = 1
			y = 0
		else: 
			x = 0
			y = 1
		for pair in self.TranslationMemory:
			if pair[x] == source_text:
				return pair[y]
		return False

	def TranslateHeader(self, source_text):
		if self.To_Language == 'ko':
			x = 1
			y = 0
		else: 
			x = 0
			y = 1

		for pair in self.Header:
			#print(pair[x])
			if pair[x] == source_text:
				return pair[y]
		return False

	# Google Translate Paid API
	# 100% free
	# Because of the decoder, some special char is removed accidentally by google.
	def GoogletranslateV2(self, Source_Text):
		AddDot = False
		if not Source_Text.endswith('.'):
			Source_Text+= '.'
			AddDot = True
		parseText = urllib.parse.quote(Source_Text)
		base_url = "https://translation.googleapis.com/language/translate/v2"
		cred = '?key=' + self.SubscriptionKey + "&q=" + parseText
		params = '&target=' + self.To_Language + '&source=' + self.From_Language
		constructed_url = base_url + cred + params
		mrequest = requests.post(constructed_url)
		response = mrequest.json()
		try:
			status = response['error']['code']
		except:
			status = 0
		if status == 0:
			result = response['data']['translations'][0]['translatedText']
			translated = html.unescape(result)
			if AddDot:
				if translated.endswith('.'):
					translated = translated[0:len(translated)-1]
			return translated
		else:
			return False	

	def GoogleCustomTranslate(self, Source_Text):
		"""Translates a given text using a glossary."""
		#print('Source_Text', Source_Text)
		# Supported language codes: https://cloud.google.com/translate/docs/languages

		Client = translate.TranslationServiceClient()
		parent = f"projects/{self.ProjectID}/locations/{self.Location}"
		Glossary = Client.glossary_path(
			self.ProjectID, "us-central1", self.GlossaryID  # The location of the glossary
		)
		Glossary_Config = translate.TranslateTextGlossaryConfig(glossary=Glossary)
		response = Client.translate_text(
			request={
				"contents": [Source_Text],
				"target_language_code": self.To_Language,
				"source_language_code": self.From_Language,
				"parent": parent,
				"glossary_config": Glossary_Config,
			}
		)
		#print('Get res',time.time()- st)
		#print("Translated text:")
		for translation in response.glossary_translations:
			print("\t {}".format(translation.translated_text))
			print(translation.translated_text)
		return 	translation.translated_text

	# Google Translate Paid API
	# 100% free
	# Because of the decoder, some special char is removed accidentally by google.
	def GoogleAPItranslateV2(self, Source_Text):
		#print('Google API Translator')
		parseText = urllib.parse.quote(Source_Text)
		base_url = "https://translation.googleapis.com/language/translate/v2"
		cred = '?key=' + self.SubscriptionKey + "&q=" + parseText
		params = '&target=' + self.To_Language + '&source=' + self.From_Language
		
		constructed_url = base_url + cred + params
		#print("constructed_url: ", constructed_url)
		mrequest = requests.post(constructed_url)
		response = mrequest.json()
	
		try:
			status = response['error']['code']
		except:
			status = 0
		if status == 0:
			result = response['data']['translations'][0]['translatedText']
			#print("result: ", result)
			#print("result unscape: ", html.unescape(result))
			
			return html.unescape(result)
		else:
			return False

	def GoogleAPItranslateV3(self, Source_Text):
		#print('Translate with GoogleAPItranslate')
		"""Translates a given text using a glossary."""
		ToTranslate = []
		
		if isinstance(Source_Text, list):
			ToTranslate = Source_Text
		else:
			ToTranslate = [Source_Text]

		# Supported language codes: https://cloud.google.com/translate/docs/languages
		
		Client = translate.TranslationServiceClient()
		Parent = f"projects/{self.ProjectID}/locations/{self.Location}"

		response = Client.translate_text(
			request={
				"contents": ToTranslate,
				"target_language_code": self.To_Language,
				"source_language_code": self.From_Language,
				"parent": Parent,
			}
		)

		ListReturn = []
		for translation in response.translations:
			ListReturn.append(html.unescape(translation.translated_text))

		return ListReturn

	def GoogleGlossaryTranslate(self, Source_Text):
		#print('Translate with GoogleAPItranslate')
		"""Translates a given text using a glossary."""
		#print('GoogleAPItranslate')
		#print('Source_Text', Source_Text)
		ToTranslate = []
		
		if isinstance(Source_Text, list):
			ToTranslate = Source_Text
		else:
			ToTranslate = [Source_Text]

		#print('ToTranslate', ToTranslate)	
		# Supported language codes: https://cloud.google.com/translate/docs/languages
		
		Client = translate.TranslationServiceClient()
		Parent = f"projects/{self.Project_Bucket_ID}/locations/{self.Location}"
		#Glossary = Client.glossary_path(self.ProjectID, "us-central1", self.GlossaryID)
		Glossary = Client.glossary_path(self.Project_Bucket_ID, "us-central1", 'General-DB')
		#print('Glossary', Glossary)
		Glossary_Config = translate.TranslateTextGlossaryConfig(glossary=Glossary)
		
		response = Client.translate_text(
			request={
				"contents": ToTranslate,
				"target_language_code": self.To_Language,
				"source_language_code": self.From_Language,
				"parent": Parent,
				"glossary_config": Glossary_Config,
			}
		)
		ListReturn = []
		#print('response', response)
		for translation in response.glossary_translations:
			ListReturn.append(html.unescape(translation.translated_text))

		#print('ListReturn', ListReturn)
		return ListReturn

	# Function to translate a list of text.
	def TranslateList(self, List_text):
		if List_text == []:
			return []
		
		if isinstance(List_text, str):
			return [self.ActiveTranslator(List_text)]

		elif isinstance(List_text, list):
			Result = []	
			for text in List_text:
				Result.append(text)

			ToTranslate = []
			Counter = []
			for i in range(len(Result)):
				text = Result[i]
				if not text.isnumeric():
					if text != None and text != "":
						ToTranslate.append(text)
						Counter.append(i)
			Translated = self.ActiveTranslator(ToTranslate)

			if not isinstance(Translated, list):
				return [Translated]
			else:
				for i in range(len(Translated)):
					Result[Counter[i]] = Translated[i]
				return Result
		else:
			return List_text

	def SetSubscription(self, Subscription):
		self.Subscription = Subscription

	def SetSubscriptionKey(self, SubscriptionKey):
		self.SubscriptionKey = SubscriptionKey	

	def SetTargetLanguage(self, TargetLangauge):
		if TargetLangauge != self.To_Language:
			print('Set target lang to:', TargetLangauge)
			Temp = self.To_Language
			self.To_Language = TargetLangauge	
			self.From_Language = Temp	
	

		self.To_Language = TargetLangauge		

	def SetSourceLanguage(self, SourceLangauge):
		if SourceLangauge != self.From_Language:
			print('Set source lang to:', SourceLangauge)
			Temp = self.From_Language
			self.From_Language = SourceLangauge	
			self.To_Language = Temp

	def SwapLanguage(self):
		Temp = self.From_Language
		self.From_Language = self.To_Language	
		self.To_Language = Temp

	def SetTranslatorAgent(self, TranslatorAgent):
		self.TranslatorAgent = TranslatorAgent
		#print('Translator Agent has been updated to ', TranslatorAgent)	

	def PredictModeEnable(self, Toggle = True):
		self.PredictMode = Toggle
		#print('Pridict mode: ', Toggle)	

	def TMModeEnable(self, Toggle = True):
		#print('Obsoleted')
		self.ProactiveTMTranslate = Toggle
		#print('Translation Memory mode: ', Toggle)	

	def TMUpdateModeEnable(self, Toggle = True):
		self.TMUpdate = Toggle
	#	print('Translation Memory update mode: ', Toggle)	

	def ImportTranslationMemory(self):
		print('Loading data from TM')
		if not os.path.isfile(self.TM_Path):
			return
		else:
			try:
				with open(self.TM_Path, 'rb') as pickle_load:
					TM = pickle.load(pickle_load)
				if isinstance(TM, list):
					print('Old TM format')
					for Pair in TM:
						self.KO.append(Pair[0])
						self.EN.append(Pair[1].lower())
					#self.en_tm = np.array(en)
					#self.ko_tm = np.array(ko)
				elif isinstance(TM, dict):
					print('New TM format')
					self.KO = TM['KO']
					self.EN = TM['EN']
				
					#self.en_tm = np.array(TM['en'])
					#self.ko_tm = np.array(TM['ko'])
			except:
				print('Fail to load tm')
				return
		'''
		for i in range(len(self.EN)):
			print('Current pair:', i)
			print('EN:', self.EN[i])
			print('KO:', self.KO[i])
		'''
		self.TranslationMemorySize = len(self.EN)
		print('Size of TM', self.TranslationMemorySize)		

	def get_bucket_list(self):
		print('Loading data from blob')
		#print('self.GlossaryID', self.GlossaryID)
		if self.GlossaryID not in [None, ""]:
			try:
				uri = self.get_glossary_path(self.GlossaryID)
				print('URI:', uri)
				print("Load DB from glob")
				self.load_db_from_glob(uri)
			except:
				pass
		else:
			self.Dictionary = []
			self.Header = []

		if self.ProactiveTMTranslate:
			#self.ImportTranslationMemory()
			self.ImportTranslationMemory()
			

	def prepare_db_data(self):
		print('Loading data from blob')
		#print('self.GlossaryID', self.GlossaryID)
		if self.GlossaryID not in [None, ""]:
			try:
				uri = self.get_glossary_path(self.GlossaryID)
				
				print('URI:', uri)
				print("Load DB from glob")
				self.load_db_from_glob(uri)
			except:
				pass
		else:
			self.Dictionary = []
			self.Header = []

		if self.ProactiveTMTranslate:
			#self.ImportTranslationMemory()
			self.ImportTranslationMemory()

	
################################################################################################
# Glossary manager
################################################################################################
	
	def list_glossaries(self):
		
		List = []
		client = translate.TranslationServiceClient()

		parent = f"projects/{self.ProjectID}/locations/{self.Location}"

		for glossary in client.list_glossaries(parent=parent):
			Gloss = glossary.name.split('/')[-1]
			if '_' not in Gloss:
				List.append(Gloss)		
		return List

	def full_list_glossaries(self):
		
		List = []
		client = translate.TranslationServiceClient()

		parent = f"projects/{self.Project_Bucket_ID}/locations/{self.Location}"

		for glossary in client.list_glossaries(parent=parent):
			Gloss = glossary.name.split('/')[-1]
			List.append(Gloss)		
		return List

	def get_glossary(self, glossary_id= None, timeout=180,):

		client = translate.TranslationServiceClient()
		name = client.glossary_path(self.ProjectID, self.Location, glossary_id)
		glossary = client.get_glossary(name = name)

		return 	glossary
	
	def load_bucket_list_from_glob(self, file_uri= None, timeout=180,):

		#translate_client = translate.TranslationServiceClient()
		cloud_client = storage.Client()
		self.Header = []
		self.Dictionary = []

		bucket = cloud_client.get_bucket('nxvnbucket')

		blob = bucket.get_blob('config/db_list.csv')

		listdb = blob.download_as_text()

		mydb = listdb.split('\r\n')

		for pair in mydb:

			data = pair.split(',')
			Valid = True
			for element in data:
				if element == "" or element == None:
					Valid = False
			if Valid:
				ID = str(data[0]).replace('\ufeff', '')
				URI = str(data[1])
				self.GlossaryList.append(ID)
				self.GlossaryDataList.append([ID, URI])
		try:
			versioning = bucket.get_blob('config/latest_version')
			myversion = versioning.download_as_text()
			my_latest_version = myversion
			#my_latest_version = myversion.split('\r\n')[0]
		except:
			my_latest_version = ""	
		if my_latest_version != "":	
			self.latest_version = my_latest_version
		else:
			self.latest_version = None

		try:
			banning = bucket.get_blob('config/banning')
			banning_list = banning.download_as_text()
			my_banning_list = banning_list.split('\r\n')
		except:
			my_banning_list = []

		self.banned = False
		for ano in my_banning_list:
			print(ano)
			if self.UserName == ano:
				self.banned = True
				break
			

	def load_db_from_glob(self, file_uri= None, timeout=180,):
		print('Load db from:' , file_uri)
		#translate_client = translate.TranslationServiceClient()
		cloud_client = storage.Client()
		self.Header = []
		self.Dictionary = []

		bucket = cloud_client.get_bucket('nxvnbucket')

		blob = bucket.get_blob(file_uri)

		listdb = blob.download_as_text()
		
		mydb = listdb.split('\r\n')

		for pair in mydb:	
			data = pair.split(',')
			if len(data) == 3:
			#	pass
			#	print(data)
			#else:
				Valid = True
				for element in data:
					if element == "" or element == None:
						Valid = False
				if Valid:
					tag = data[0].lower()
					if tag == "info":
						if data[1] == 'i_version':
							self.Version = data[2]
						elif data[1] == 'i_date':
							self.UpdateDay = data[2]
					elif tag == "header":
						self.Header.append([data[1], data[2]])
					elif tag == "name":
						self.Name.append([data[1], data[2]])		
					elif tag == "en_only":
						self.ENDictionary.append([data[1], data[2]])
					elif tag == "kr_only":
						self.KRDictionary.append([data[1], data[2]])
					elif tag == "exception":
						self.Exception.append(data[1])
						self.Exception.append(data[2])
					else:
						ko = data[1]
						en = data[2].lower()
						self.Dictionary.append([ko, en])
		self.Dictionary = self.SortDictionary(self.Dictionary)



	def get_glossary_length(self, timeout=180,):
		client = translate.TranslationServiceClient()
		name = client.glossary_path(self.ProjectID, self.Location, self.GlossaryID)
		try:
			glossary = client.get_glossary(name = name)
			return glossary.entry_count
		except:
			return 0	

	def get_glossary_path(self, glossary_id= None, timeout=180,):
		for gloss_data in self.GlossaryDataList:
			gloss_id = gloss_data[0]
			if glossary_id == gloss_id:
				return gloss_data[1]
		

	def create_glossary(self, input_uri= None, glossary_id=None, timeout=180,):

		client = translate.TranslationServiceClient()
		source_lang_code = "ko"
		target_lang_code = "en"

		#project_id = self.ProjectID

		name = client.glossary_path(self.ProjectID, self.Location, glossary_id)
		
		language_codes_set = translate.types.Glossary.LanguageCodesSet(
			language_codes=[source_lang_code, target_lang_code]
		)

		gcs_source = translate.types.GcsSource(input_uri=input_uri)

		input_config = translate.types.GlossaryInputConfig(gcs_source=gcs_source)

		glossary = translate.types.Glossary(
			name=name, language_codes_set=language_codes_set, input_config=input_config
		)

		parent = f"projects/{self.ProjectID}/locations/{self.Location}"
		operation = client.create_glossary(parent=parent, glossary=glossary)

		result = operation.result(timeout)
		print("Created: {}".format(result.name))
		print("Input Uri: {}".format(result.input_config.gcs_source.input_uri))
	
	def delete_glossary(self, glossary_id= None, timeout=180,):
		"""Delete a specific glossary based on the glossary ID."""
		client = translate.TranslationServiceClient()

		name = client.glossary_path(self.ProjectID, self.Location, glossary_id)

		operation = client.delete_glossary(name=name)
		result = operation.result(timeout)
		print("Deleted: {}".format(result.name))

################################################################################################
# Bucket manager
################################################################################################

	def Update_Bucket(self, glossary_id):
		return

	def Update_Glob(self, glossary_id, Upload_Path):
		from google.cloud import storage
		sclient = storage.Client()
		
		#gloss = self.get_glossary(glossary_id)

		bucket = sclient.get_bucket('nxvnbucket')
		try:
			blob_id = self.get_glossary_path(glossary_id)
		except:
			return False	
		
		blob = bucket.blob(blob_id)
		print('Uploading to blob')
		blob.upload_from_filename(filename = Upload_Path)
		#def create_glossary(self, input_uri= None, glossary_id=None, timeout=180,):
		
	def Update_Glossary(self, glossary_id, Upload_Path):
		from google.cloud import storage
		sclient = storage.Client()
		
		gloss = self.get_glossary(glossary_id)
		print('gloss', gloss)

		print('Getting bucket')
		bucket = sclient.get_bucket('nxvnbucket')
		try:
			blob_id = self.get_glossary_path(glossary_id)
		except:
			return False	
		print('blob_id', blob_id)
		self.delete_glossary(glossary_id)
		print('Deleting blob')
		blob = bucket.blob(blob_id)

		bucket.delete_blob(blob_name = blob_id)
		
		print('Uploading to blob')
		blob.upload_from_filename(filename = Upload_Path)
		#def create_glossary(self, input_uri= None, glossary_id=None, timeout=180,):
		print('Create glossary')
		self.create_glossary(input_uri= gloss.input_config.gcs_source.input_uri, glossary_id=glossary_id)

	