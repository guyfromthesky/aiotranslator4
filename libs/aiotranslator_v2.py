#Regular expression handling
import re
import base64
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

import pandas as pd
import numpy as np

#System lib
import os
import sys, getopt
import unicodedata
import string

import pickle
import time
from datetime import datetime

Tool = "translator"
rev = 4000
a,b,c,d = list(str(rev))
ver_num = a + '.' + b + '.' + c + chr(int(d)+97)
Translatorversion = Tool + " " + ver_num

class Translator:
	def __init__(self, 
		from_language = 'auto', 
		to_language = 'en', 
		source_language_predict = True, 
		proactive_memory_translate = True, 
		tm_update=True, 
		glossary_id = None, 
		temporary_tm = None,
		tm_path = None,
		#Tool that is currently use this libs
		used_tool = 'writer',
		tool_version = None,
		bucket_id = 'nxvnbucket',
		db_list_uri = 'config/db_list.csv',
		project_bucket_id = 'credible-bay-281107',
		**kwargs
	):
		
		self.from_language = from_language
		self.to_language = to_language	
		self.default_exception = ['pass', 'fail', 'n/a', 'n/t', 'result', '\t', '\r', '\n', '', '\r\n', ' ', 'sort', 'function', 'data' , 'x', 'o']

		self.source_language_predict = source_language_predict
		self.tm_update = tm_update
		self.proactive_memory_translate = proactive_memory_translate

		self.used_tool = used_tool
		self.tool_version = tool_version

		self.project_id = None

		# App online config
		self.project_bucket_id = project_bucket_id
		self.bucket_id = bucket_id
		self.db_list_uri = db_list_uri

		self.load_project_id_from_json()

		self.glossary_id = glossary_id
		self.location = "us-central1"


		self.glossary_list = []	
		self.glossary_data_list = []
		

		# Get the temp folder location for Windows/Mac
		self.init_config_path()
		
		# Check and get the location of TM file
		# If path is invalid or not stated, use local TM
		self.init_tm_path(tm_path)
	
		# Select correct log file.
		self.init_logging_file()

		#self.SpecialSheets = ['kr_only', 'en_only', 'name']
		self.special_tag = ['header', 'name', 'en_only', 'kr_only', 'cn_only', 'jp_only', 'exception']
		self.supported_language = ['ko', 'en', 'cn', 'jp']
		
		self.init_temporary_tm()

		self.init_db_data()

		self.temporary_tm = pd.DataFrame()
		self.translation_memory = pd.DataFrame()
		self.translation_memory_size = 0

		self.exception_Char = string.punctuation + string.digits
		self.accepted_char = string.punctuation 
		self.printable = string.printable
		
		# Flag for user who is banned.
		self.banned = False

		# Get user name of the Windows account
		self.get_user_name()

		# Get name of the PC that currently in use
		self.get_pc_name()

		# Minimun version allowed to be used.
		self.latest_version = 0
		# DB version
		self.version = '-'
		# Update day of the DB
		self.update_day = '-'

		try:
			current_time = datetime.now()
			self.load_bucket_list_from_glob()
			print('Total time to load bucket list:', str(datetime.now() - current_time))
			current_time = datetime.now()
			self.prepare_db_data()
			print('Total time to load db:', str(datetime.now() - current_time))
		except Exception  as e:
			print("Error:", e)


		# Send tracking record from previous run to logging server.
		tracking_result = self.send_tracking_record()

		# Init tracking request
		self.last_section_tm_request = 0
		self.last_section_invalid_request = 0
		self.last_section_api_usage = 0

######################################################################################################
# INIT FUNCTION
######################################################################################################
	def init_db_data(self):
		# The multi-language DB.
		self.all_db = pd.DataFrame()
		# Used to translate from A -> B and vice versa
		self.dictionary = []
		# The DB that only be used to translate from korean to other language
		self.ko_dictionary = []
		# The DB that only be used to translate from english to other language.
		self.en_dictionary = []
		# The DB that only be used to translate from Chinese to other language.
		self.cn_dictionary = []
		# The DB that only be used to translate from Japanese to other language.
		self.jp_dictionary = []

		self.header = []
		self.name = []
		self.exception = []
	
	def init_config_path(self):
		if sys.platform.startswith('win'):
			self.config_path = os.environ['APPDATA']
			self.OS = 'win'
		else:
			self.config_path = os.getcwd()
			self.OS = 'mac'

	
	def init_logging_file(self):
		if self.used_tool == 'document':
			self.tracking_log = self.config_path + '\\AIO Translator\\d_logging.pkl'
			self.invalid_request_log = self.config_path + '\\AIO Translator\\d_invalid_request_logging.pkl'
			self.tm_request_log = self.config_path + '\\AIO Translator\\d_tm_request_logging.pkl'
			#self.false_request = self.config_path + '\\AIO Translator\\false_request.pkl'
		else:
			self.tracking_log = self.config_path + '\\AIO Translator\\logging.pkl'
			self.invalid_request_log = self.config_path + '\\AIO Translator\\invalid_request_logging.pkl'
			self.tm_request_log = self.config_path + '\\AIO Translator\\tm_request_logging.pkl'
		
		self.tracking_log = self.correct_path_os(self.tracking_log)
		self.invalid_request_log = self.correct_path_os(self.invalid_request_log)
		self.tm_request_log = self.correct_path_os(self.tm_request_log)

	def correct_path_os(self, path):
		if not sys.platform.startswith('win'):
			return str(path).replace('\\', '//')
		return path
	
	def init_temporary_tm(self):
		self.temporary_tm	= pd.DataFrame(columns=['en','ko', 'cn', 'jp'])
		#self.temporary_tm = self.temporary_tm.append({'en': np.nan,'ko': np.nan, 'cn': np.nan, 'jp': np.nan}, ignore_index=True)

	def get_user_name(self):
		try:
			if self.OS == 'win':
				try:
					self.user_name = os.getlogin()
				except:
					self.user_name = os.environ['COMPUTERNAME']
			else:
				try:
					self.user_name = os.environ['LOGNAME']
				except:
					self.user_name = "Anonymous"
		except:
			self.user_name = "Anonymous"

	def get_pc_name(self):
		try:
			if self.OS == 'win':
				try:
					self.pc_name = os.environ['COMPUTERNAME']
				except:
					self.pc_name = "Anonymous"
			else:
				try:
					self.pc_name = os.environ['LOGNAME']
				except:
					self.pc_name = "Anonymous"
		except:
			self.pc_name = "Anonymous"				

######################################################################
# Cloud function - DB handling
######################################################################
 	# Get the current Project of the current account
	# The account id is stored in the JSON file.
	def load_project_id_from_json(self):
		try:
			License = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
			with open(License, 'r') as myfile:
				data=myfile.read()
			obj = json.loads(data)
			self.project_id = obj['project_id']
		except:
			self.project_id = 'credible-bay-281107'

	# Not use, consider remove later
	# If the lib is run as a server, consider to use this function
	def init_glossary(self):
		self.Client = translate.TranslationServiceClient()	
		self.Parent = f"projects/{self.project_id}/locations/{self.location}"
		self.Glossary = self.Client.glossary_path(self.project_id, self.location, self.glossary_id)
		self.Glossary_Config = translate.TranslateTextGlossaryConfig(glossary=self.Glossary)

	# Check and remove later
	def get_time_stamp(self):
		now = datetime.now()
		year =  now.isocalendar()[0]
		week =  now.isocalendar()[1]
		return str(year) + "_" + str(week)

	# Might use on DB uploader
	def get_glossary_list(self):
		print('Getting Glossary info')
		self.glossary_list = []
		self.glossary_listFull = self.full_list_glossaries()
		print('glossary_listFull', self.glossary_listFull)
		for Gloss in self.glossary_listFull:
			Gloss = Gloss.split('/')[-1]
			if '_' not in Gloss:
				self.glossary_list.append(Gloss)		


	def load_request_log(self, log_file):

		if not os.path.isfile(log_file):
			amount = 0
		else:
			try:
				with open(log_file, 'rb') as pickle_load:
					amount = pickle.load(pickle_load)
			except:
				amount = 0
		return amount

	# Add counter to temp log file
	def append_tm_request_logging(self, add_num=0):

		if add_num == 0:
			return
		log_file = self.tm_request_log	
		amount = self.load_request_log(log_file)

		amount += add_num
		try:
			with open(log_file, 'wb') as pickle_file:
				pickle.dump(amount, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
		except:
			pass

	# Add counter to temp log file
	def append_invalid_request_logging(self, add_num=0):
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
	
	# Add counter to temp log file
	def append_api_usage_logging(self, add_num=0):
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
	
	# Send all tracking record to logging
	def send_tracking_record(self,file_name = None):

		self.last_section_api_usage = self.load_request_log(self.tracking_log)
		print('translate-usage:', self.last_section_api_usage)
		self.last_section_tm_request = self.load_request_log(self.tm_request_log)
		print('tm-usage:', self.last_section_tm_request)
		self.last_section_invalid_request = self.load_request_log(self.invalid_request_log)
		print('invalid-request:', self.last_section_invalid_request)
		result = True
		
		try:
			client = logging.Client()
		except Exception  as e:
			print('exception:', e)
			return False
		
		if self.last_section_api_usage > 0 or self.last_section_tm_request > 0:
			log_name = 'translator-usage'

			logger = client.logger(log_name)

			data_object = {
				'user': self.user_name,
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
				try:
					correct_source_name = file_name.encode('cp437').decode('euc_kr')
				except:
					correct_source_name = file_name

				data_object['file_name'] = correct_source_name

			tracking_object = {
				'user': self.user_name,
				'details': data_object
			}
			
			try:
				logger.log_struct(tracking_object)
				if self.last_section_api_usage > 0:
					os.remove(self.tracking_log)
				if self.last_section_tm_request > 0:
					os.remove(self.tm_request_log)
				if self.last_section_invalid_request > 0:
					os.remove(self.invalid_request_log)	
			except Exception  as e:
				print('exception:', e)
				result = False
		
		return result
	
	# Very IMPORTANT function
	# This function is used to sort the Database object (descending)
	# Allow us to check the long word before the sort one:
	# E.g. 'pine apple' will be perfer to lookup first, 
	# if there is no 'pine apple' exist, we will looking for 'apple' in the sentence.
	def sort_dictionary(self, List):
		return(sorted(List, key = lambda x: (len(x[0]), x[0]), reverse = True))

######################################################################
# Pre-translate function
######################################################################

	# This function is used to ignore any word present in this list
	# E.g. if a cell contains the text Fail (the TC result), the tool won't translate this cell.
	# The default list can be easily check by Simple Translator tool.
	# The exception list in the exception file is not support by Translator tool.
	def Validateexception(self, string):

		string = str(string).lower()

		try:
			exception_list = self.exception + self.default_exception
		except:
			exception_list = self.default_exception

		for X in exception_list: 
				if string.strip() == X.lower().strip():
					return False
		return True	

	
	# Similar to Validateexception, will allow us to ignore the string that does not contain any korean character (Only work for KR -> en)
	# E.g. if a cell contains the text Fail (the TC result), the tool won't translate this cell.
	# Can be easily check by Simple Translator tool.
	def ValidateLanguageSource(self, string):
		if self.from_language == 'ko':
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

	# Similar to Validateexception, will allow us to ignore the string is in the URL format
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

	def ValidateSourceText(self, source_text):
		
		source_text = source_text.lower()
		
		result = True

		if self.Validateexception(source_text) == False:
			result = False

		# Prevent case that the source text contain some special character.
		elif self.ValidateURL(source_text) == True:
			#print('URL, wont translate!')
			result = False

		elif self.ValidateLanguageSource(source_text) == False:
			result = False

		#if self.ValidateUnicodeSource(source_text) == False:
		#	return False
			
		elif self.proactive_memory_translate == True:
			
			translated = self.memory_translate(source_text)
			#print('TM Translate:', source_text, '-->', translated)
			if translated != False:
				
				result = translated	

		#self.invalid_request_log
		if not isinstance(result, bool):
			count = 0
			try:
				if isinstance(source_text, list):
					for c in source_text:
						count+= len(c)
				elif isinstance(source_text, str):
					count+= len(source_text)
			except Exception  as e:
				print('Error message: ', e)
				pass
			#print('Append tm usage:', count)
			self.append_tm_request_logging(count)
		elif result == False:
			count = 0
			try:
				if isinstance(source_text, list):
					for c in source_text:
						count+= len(c)
				elif isinstance(source_text, str):
					count+= len(source_text)
			except Exception  as e:
				print('Error message: ', e)
				pass

			self.append_invalid_request_logging(count)
		#print('Validate result: ', result)
		return result
		

	def english_pre_translate(self, source_text):
		#print('english pre-translate')
		# Use for Translating KR -> en
		# Add 2 space to the dict to prevent the en character and ko character merge into 1
		# because the translator API cannot handle those.
		RawText = source_text
		LowerCase_text = source_text
		
		temp_dict = self.dictionary + self.ko_dictionary
		#print('Temp dict for Korean translate', len(temp_dict))

		for pair in temp_dict:

			# Old is en text in the dict
			Old = pair[0].strip()
			
			# New is the KR text we want to replace with
			New = " " + pair[1].strip() + " "
			#New = pair[1].strip()
			# IF there is the defined text in the sentence
			StartFind = 0
			while LowerCase_text.find(Old, StartFind) != -1:
				#print('english pretrans')
				# Find the location of the text in the sentence
				location = int(LowerCase_text.find(Old, StartFind))
				# And the text length
				TextLen = len(Old)
				StartFind = location + TextLen
				FirstChar = None
				NextChar = None
				# If the text is not in the begin of the sentence
				# E.g. "NewWord XXX" or "XXX [Word] XXX"
				if location > 0:
					try:
						FirstChar = LowerCase_text[location-1]
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
				if self.accepted_char.find(FirstChar) != -1 or FirstChar in [ None,  "", " "]:
					
					# If the (first char) is a alphabet, this is not the word we're looking for
					# E.g. 'Work' is exist in 'homework' but it's not the exact text we're looking for
					if self.accepted_char.find(NextChar) != -1 or NextChar in [ None,  "", " "]:
						# If the (first char) is a alphabet, this is not the word we're looking for
						# If the (last char) is a alphabet, this is not the word we're looking for
						# E.g. 'Work' is exist in 'workout' but it's not the exact text we're looking for
						#print('Source: ', source_text)
						#print('Valid 1st char: ', FirstChar)
						#print('Valid end char: ', NextChar)
						Raw_Old = RawText[location:StartFind]
						#print('Raw_Old', Raw_Old)
						RawText = RawText.replace(FirstChar + Raw_Old + NextChar, FirstChar + New + NextChar, 1)
						
						#RawText[location, StartFind-1] = RawText

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

	def korean_pre_translate(self, input):
		# Use for Translating en -> KR
		# It's a litle complicated....
		# To cover some special case can happen.
		RawText = input
		source_text = RawText.lower()
			
		temp_dict = self.dictionary + self.en_dictionary
		#print('Temp dict for English translate', len(temp_dict))

		for pair in temp_dict:
			# Old is en text in the dict
			Old = pair[1].strip()
			
			# New is the KR text we want to replace with
			New = " " + pair[0].strip() + " "
			#print('koreanPreTranslate Replacing ', Old, New)
			# IF there is the defined text in the sentence
			StartFind = 0
			while source_text.find(Old) != -1:
				#print('source_text', source_text)		
				# Find the location of the text in the sentence
				location = source_text.find(Old)
				# And the text length
				TextLen = len(Old)
				StartFind = location + TextLen
				FirstChar = ""
				NextChar = ""
				# If the text is not in the begin of the sentence
				# E.g. "NewWord XXX" or "XXX [Word] XXX"
				if location != 0:
					try:
						FirstChar = source_text[location-1]
					except:
						FirstChar = "" 
				else:
					FirstChar = ""
				# Find the character stand right after the text (first char)
				# E.g. "w" or "["
				try:
					NextChar = source_text[location+TextLen] 
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
					#print('Start:', location, "end:", StartFind, 'len:', len(RawText))
					Raw_Old = RawText[location:StartFind]
					#print('Raw Old', Raw_Old, 'Old', Old)
					RawText = RawText.replace(Raw_Old, New, 1)
					#print("RawText", RawText)
				source_text = RawText.lower()
		# Remove the space from both side of the text
		# The space that we've add above.
		RawText = RawText.strip()
		return RawText

######################################################################
# All translate function
######################################################################
	# Translator main function.
	# All the text will be passed into this function.
	def translate(self, Input):
		if isinstance(Input, list):
			source_text = Input
		elif isinstance(Input, str):
			source_text = [Input]
		else:
			return False

		raw_source = []
		to_translate = []
		to_translate_index = []
		translation = []
	
		for text in source_text:
			translation.append(text)

		
		for i in range(len(translation)):
			text = str(translation[i])
			
			validation = self.ValidateSourceText(text)
			#print('Details:', text, 'Result:', validation)
			if validation == False:
				continue
			if validation == True:
				try:
					index_num = raw_source.index(text)
					to_translate_index[index_num].append(i)
				except Exception  as e:
					if self.to_language == 'ko':
						pre_translate = self.korean_pre_translate(text)
					elif self.to_language == 'en':
						pre_translate = self.english_pre_translate(text)
					
					raw_source.append(text)
					to_translate.append(pre_translate)
					to_translate_index.append([i])

				#raw_source.append(text)
				#to_translate.append(pre_translate)
				#to_translate_index.append(i)
			else:
				#translated by memory
				translation[i] = validation

		#print('to_translate', to_translate)
		if len(to_translate) > 0:
			try:
				translated = self.activated_translator(to_translate)
			except Exception  as e:
				print('error:', e)
				translated = []
		
		else:
			translated = []	

		for i in range(len(translated)):
			for index_number in to_translate_index[i]:
				translation[index_number] = translated[i]
			#translation[to_translate_index[i]] = translated[i]
			if self.tm_update == True:
				#print('Append TM: ', translated[i], raw_source[i] )
				self.generate_temporary_tm(str_translated = translated[i], str_input = raw_source[i])
	
		if isinstance(Input, str):
			return translation[0]
		else:
			return translation
	
	def activated_translator(self, source_text):
		count = 0
		try:
			if isinstance(source_text, list):
				for c in source_text:
					count+= len(c)
			elif isinstance(source_text, str):
				count+= len(source_text)
			else:
				return False
		except:
			pass
		
		if self.banned == True:
			return
		
		try:	
			if self.project_bucket_id != self.project_id:
				translation = self.google_translate_v3(source_text)
			else:
				translation =  self.google_glossary_translate(source_text)
		except Exception  as e:
			print('error translation:', e)
			try:
				client = logging.Client()
			except:
				pass

			log_name = 'translator-error'
			logger = client.logger(log_name)	
			text_log = self.user_name + ', ' + self.pc_name + ', ' + self.glossary_id + ', ' + str(e)

			try:
				logger.log_text(text_log)
			except:
				pass
			translation = False
		#print('translation', translation)
		if translation != False:
			#print('TM usage:', count)
			self.append_api_usage_logging(count)

		return translation	

	def translate_header(self, source_text):
		for pair in self.header:
			#print(pair[x])
			if pair[0] == source_text:
				return pair[1]
		return False

	def google_translate_v3(self, source_text):
		#print('Translate with GoogleAPItranslate')
		"""Translates a given text using a glossary."""
		ToTranslate = []
		
		if isinstance(source_text, list):
			ToTranslate = source_text
		else:
			ToTranslate = [source_text]

		# Supported language codes: https://cloud.google.com/translate/docs/languages
		
		Client = translate.TranslationServiceClient()
		Parent = f"projects/{self.project_id}/locations/{self.location}"

		response = Client.translate_text(
			request={
				"contents": ToTranslate,
				"target_language_code": self.to_language,
				"source_language_code": self.from_language,
				"parent": Parent,
			}
		)

		ListReturn = []
		for translation in response.translations:
			ListReturn.append(html.unescape(translation.translated_text))

		return ListReturn

	def google_glossary_translate(self, source_text):
		#print('Translate with GoogleAPItranslate')
		"""Translates a given text using a glossary."""
		#print('GoogleAPItranslate')
		#print('source_text', source_text)
		ToTranslate = []
		
		if isinstance(source_text, list):
			ToTranslate = source_text
		else:
			ToTranslate = [source_text]

		#print('ToTranslate', ToTranslate)	
		# Supported language codes: https://cloud.google.com/translate/docs/languages
		
		Client = translate.TranslationServiceClient()
		Parent = f"projects/{self.project_bucket_id}/locations/{self.location}"
		#Glossary = Client.glossary_path(self.project_id, "us-central1", self.glossary_id)
		Glossary = Client.glossary_path(self.project_bucket_id, "us-central1", 'General-DB')
		#print('Glossary', Glossary)
		Glossary_Config = translate.TranslateTextGlossaryConfig(glossary=Glossary)
		
		response = Client.translate_text(
			request={
				"contents": ToTranslate,
				"target_language_code": self.to_language,
				"source_language_code": self.from_language,
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

############################################################################
# Setting function
############################################################################
	def set_subscription(self, Subscription):
		self.Subscription = Subscription

	def set_subscription_key(self, SubscriptionKey):
		self.SubscriptionKey = SubscriptionKey	

	def set_target_language(self, TargetLangauge):
		if TargetLangauge != self.to_language:
			print('Set target lang to:', TargetLangauge)
			Temp = self.to_language
			self.to_language = TargetLangauge	
			self.from_language = Temp
		self.to_language = TargetLangauge	
		self.update_db_from_dataframe()


	def set_source_language(self, source_language):
		if source_language != self.from_language:
			print('Set source lang to:', source_language)
			Temp = self.from_language
			self.from_language = source_language	
			self.to_language = Temp
			self.update_db_from_dataframe()

	def swap_language(self):
		Temp = self.from_language
		self.from_language = self.to_language	
		self.to_language = Temp
		self.update_db_from_dataframe()

	def set_translator_agent(self, TranslatorAgent):
		self.TranslatorAgent = TranslatorAgent
		#print('Translator Agent has been updated to ', TranslatorAgent)	


	
################################################################################################
# Glossary manager
################################################################################################
	
	def list_glossaries(self):
		
		List = []
		client = translate.TranslationServiceClient()

		parent = f"projects/{self.project_id}/locations/{self.location}"

		for glossary in client.list_glossaries(parent=parent):
			Gloss = glossary.name.split('/')[-1]
			if '_' not in Gloss:
				List.append(Gloss)		
		return List

	def full_list_glossaries(self):
		
		List = []
		client = translate.TranslationServiceClient()

		parent = f"projects/{self.project_bucket_id}/locations/{self.location}"

		for glossary in client.list_glossaries(parent=parent):
			Gloss = glossary.name.split('/')[-1]
			List.append(Gloss)		
		return List

	def get_glossary(self, glossary_id= None, timeout=180,):

		client = translate.TranslationServiceClient()
		name = client.glossary_path(self.project_id, self.location, glossary_id)
		glossary = client.get_glossary(name = name)

		return 	glossary
	
	def load_bucket_list_from_glob(self, file_uri= None, timeout=180,):

		cloud_client = storage.Client()

		bucket = cloud_client.get_bucket(self.bucket_id)

		blob = bucket.get_blob(self.db_list_uri)

		listdb = blob.download_as_text()

		mydb = listdb.split('\r\n')

		for pair in mydb:

			data = pair.split(',')
			Valid = True
			for element in data:
				if element == "" or element == None:
					Valid = False
			if Valid:
				id = str(data[0]).replace('\ufeff', '')
				URI = str(data[1])
				self.glossary_list.append(id)
				self.glossary_data_list.append([id, URI])
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
			if self.user_name == ano:
				self.banned = True
				break
			

	def load_db_from_glob(self, file_uri= None, timeout=180,):

		cloud_client = storage.Client()

		bucket = cloud_client.get_bucket(self.bucket_id)

		blob = bucket.get_blob(file_uri)

		# Retrive DB as string from URI
		listdb = blob.download_as_text()
		
		# Split DB into row.
		mydb = listdb.split('\r\n')
		
		# Split row into list
		split_db = lambda x: x.split(',')
		list_db = list(map(split_db, mydb))
		# Remove the header since it's not nesessary
		list_db.remove(list_db[0])

		# Retrive info data and remove from DB
		index_count = 0
		for item_index in range(len(list_db)- 1):
			current_indexer = item_index-index_count
			item = list_db[current_indexer]		
			if item[0] == 'info':
				if item[1] == 'version':
					self.version = item[2]
					del list_db[current_indexer]
					index_count += 1
				elif item[1] == 'date':
					self.update_day = item[2]
					del list_db[current_indexer]
					index_count += 1
				if index_count == 2:
					break	
		
		# Decode encoded DB.
		# Please note that from translator V4, DB is store in base64 encoded format.
		new_list_db = list(map(lambda x: self.base64_decode_list(x), list_db))
		# Load DB as DataFrame
		self.all_db = pd.DataFrame(columns=['tag', 'ko', 'en', 'cn', 'jp'], data=new_list_db)
		self.update_db_from_dataframe()

	# Filter DB and store in suitable variable
	def update_db_from_dataframe(self):
		#Create header list:
		header = self.all_db[self.all_db["tag"] == 'header'][[self.from_language, self.to_language]]
		self.header = header.values.tolist()
		self.header = self.sort_dictionary(self.header)
		#Create name list:
		name = self.all_db[self.all_db["tag"] == 'name'][[self.from_language, self.to_language]]
		self.name = name.values.tolist()
		self.name = self.sort_dictionary(self.name)
		if self.from_language == 'en':
			#Create en_only list:
			en_dictionary = self.all_db[self.all_db["tag"] == 'en_only'][[self.from_language, self.to_language]]
			self.en_dictionary = en_dictionary.values.tolist()
			self.en_dictionary = self.sort_dictionary(self.en_dictionary)
		elif self.from_language == 'ko':
			#Create kr_only list:
			ko_dictionary = self.all_db[self.all_db["tag"] == 'kr_only'][[self.from_language, self.to_language]]
			self.ko_dictionary = ko_dictionary.values.tolist()
			self.ko_dictionary = self.sort_dictionary(self.ko_dictionary)
		elif self.from_language == 'cn':
			#Create cn_only list:
			cn_dictionary = self.all_db[self.all_db["tag"] == 'cn_only'][[self.from_language, self.to_language]]
			self.cn_dictionary = cn_dictionary.values.tolist()
			self.cn_dictionary = self.sort_dictionary(self.cn_dictionary)
		elif self.from_language == 'jp':
			#Create jp_only list:
			jp_dictionary = self.all_db[self.all_db["tag"] == 'jp_only'][[self.from_language, self.to_language]]
			self.jp_dictionary = jp_dictionary.values.tolist()
			self.jp_dictionary = self.sort_dictionary(self.jp_dictionary)
		#Create exception list:
		exception_for_source_language = self.all_db[self.all_db["tag"] == 'exception'][[self.to_language]].values.tolist()
		exception_for_target_language = self.all_db[self.all_db["tag"] == 'exception'][[self.from_language]].values.tolist()
		self.exception = exception_for_source_language + exception_for_target_language
		
		#Create normal dict list:
		dictionary = self.all_db[self.all_db["tag"] == 'dictionary'][[self.from_language, self.to_language]]
		self.dictionary = dictionary.values.tolist()
		self.dictionary = self.sort_dictionary(self.dictionary)
		#print(self.dictionary)



	def get_glossary_length(self, timeout=180,):
		client = translate.TranslationServiceClient()
		name = client.glossary_path(self.project_id, self.location, self.glossary_id)
		try:
			glossary = client.get_glossary(name = name)
			return glossary.entry_count
		except:
			return 0	

	def get_glossary_path(self, glossary_id= None, timeout=180,):
		for gloss_data in self.glossary_data_list:
			gloss_id = gloss_data[0]
			if glossary_id == gloss_id:
				return gloss_data[1]
		
	# Create the glossary that use for glossary_translate
	def create_glossary(self, input_uri= None, glossary_id=None, timeout=180,):

		client = translate.TranslationServiceClient()
		source_lang_code = "ko"
		target_lang_code = "en"

		name = client.glossary_path(self.project_id, self.location, glossary_id)
		
		language_codes_set = translate.types.Glossary.LanguageCodesSet(
			language_codes=[source_lang_code, target_lang_code]
		)

		gcs_source = translate.types.GcsSource(input_uri=input_uri)

		input_config = translate.types.GlossaryInputConfig(gcs_source=gcs_source)

		glossary = translate.types.Glossary(
			name=name, language_codes_set=language_codes_set, input_config=input_config
		)

		parent = f"projects/{self.project_id}/locations/{self.location}"
		operation = client.create_glossary(parent=parent, glossary=glossary)

		result = operation.result(timeout)
		print("Created: {}".format(result.name))
		print("Input Uri: {}".format(result.input_config.gcs_source.input_uri))
	
	# Delete the glossary that use for glossary_translate
	def delete_glossary(self, glossary_id= None, timeout=180,):
		"""Delete a specific glossary based on the glossary id."""
		client = translate.TranslationServiceClient()

		name = client.glossary_path(self.project_id, self.location, glossary_id)

		operation = client.delete_glossary(name=name)
		result = operation.result(timeout)
		print("Deleted: {}".format(result.name))

	def get_bucket_list(self):
		print('Loading data from blob')
		#print('self.glossary_id', self.glossary_id)
		if self.glossary_id not in [None, ""]:
			try:
				uri = self.get_glossary_path(self.glossary_id)
				print('URI:', uri)
				#print("Load DB from glob")
				self.load_db_from_glob(uri)
			except Exception as e:
				print('Error:', e)
		else:
			self.dictionary = []
			self.header = []

		if self.proactive_memory_translate:
			#self.import_translation_memory()
			self.import_translation_memory()
			

	def prepare_db_data(self):
		if self.glossary_id not in [None, ""]:
			try:
				uri = self.get_glossary_path(self.glossary_id)
				print('URI:', uri)
				print("Load DB from glob:", uri)
				self.load_db_from_glob(uri)
			except Exception as e:
				print('[Error] prepare_db_data:', e)

		else:
			self.dictionary = []
			self.header = []

		if self.proactive_memory_translate:
			#self.import_translation_memory()
			self.import_translation_memory()

	# Store the DB in base64 format for csv format friendly
	def basse64_encode(self, string_to_encode):
		raw_encoded_string =  str(base64.b64encode(Path_Value.encode('utf-8')))
		encoded_string = re.findall(r'b\'(.+?)\'', raw_encoded_string)[0]
		
		return encoded_string

	def base64_decode(self, string_to_decode):
		if string_to_decode in ['', None] :
			return ''
		return base64.b64decode(string_to_decode).decode('utf-8')
		
	
	def base64_decode_list(self, list_string_to_decode):
		#print('list_string_to_decode', list_string_to_decode)
		if len(list_string_to_decode) != 5:
			return [['Invalid', None, None, None, None]]
		decode = lambda x: self.base64_decode(x)
		decoded_list = list(map(decode, list_string_to_decode[1:]))
		if list_string_to_decode[0] not in self.special_tag:
			tag = 'dictionary'
		else:
			tag = list_string_to_decode[0]

		decoded_list.insert(0, tag)
	
		return decoded_list

################################################################################################
# Bucket manager
# Backet is the storage that store DB
# Main bucket that this tool use is "nxvnbucket"
################################################################################################

	def update_bucket(self, glossary_id):
		return

	# Replace the DB file by the new one
	# Need to rename the old DB file for backup purpose
	# 	-> Update later
	def update_glob(self, glossary_id, Upload_Path):
		from google.cloud import storage
		sclient = storage.Client()
		
		#gloss = self.get_glossary(glossary_id)

		bucket = sclient.get_bucket(self.bucket_id)
		try:
			blob_id = self.get_glossary_path(glossary_id)
		except:
			return False	
		
		blob = bucket.blob(blob_id)
		print('Uploading to blob')
		blob.upload_from_filename(filename = Upload_Path)
		#def create_glossary(self, input_uri= None, glossary_id=None, timeout=180,):

	# Upload DB to bucket
	# DB file will be converted into base64 format
	# 
	def upload_glob_from_object(self, glossary_id, db_object):
		from google.cloud import storage
		sclient = storage.Client()
		
		#gloss = self.get_glossary(glossary_id)

		bucket = sclient.get_bucket(self.bucket_id)
		try:
			blob_id = self.get_glossary_path(glossary_id)
		except:
			return False	
		
		blob = bucket.blob(blob_id)
		print('Uploading to blob')
		
		#db_object = {}
		#db_object['info'] = {}
		#db_object['db'] = {}
		List = []
		# Info:
		version = db_object['info']['version']
		date = db_object['info']['date']
		
		List.append()
		blob.upload_from_filename(filename = Upload_Path)
		
		return
		
	def update_glossary(self, glossary_id, upload_path):
		
		from google.cloud import storage
		sclient = storage.Client()
		
		gloss = self.get_glossary(glossary_id)
		print('gloss', gloss)

		print('Getting bucket')
		bucket = sclient.get_bucket(self.bucket_id)
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

	
##########################################################
# TM Manager
# TM type: pd.DataFrame
# tm = {'project_id': pd.DataFrame}
# df = {'en': string_en, 'ko': string_ko, 'cn': string_cn, 'jp': string_jp}
##########################################################

	# Get the tm's path.
	# if tm is invalid, use local tm instead
	def init_tm_path(self, tm_path):
		if tm_path != None:
			if os.path.isfile(tm_path):
				self.tm_path = self.correct_path_os(tm_path)
				return
		tm_path = self.config_path + '\\AIO Translator\\Local.pkl'
		self.tm_path = self.correct_path_os(tm_path)
		return

	def import_translation_memory(self):
		print('Import TM from pickle file', str(self.tm_path))
		if not os.path.isfile(self.tm_path):
			print('Pickle file not found')
			return
		else:
			try:
				with open(self.tm_path, 'rb') as pickle_load:
					all_tm = pickle.load(pickle_load)
				if isinstance(all_tm, dict):
					# TM format v4
					if self.glossary_id in all_tm:
						print('TM v4')
						self.translation_memory = all_tm[self.glossary_id]

					# TM format v3
					elif 'EN' in all_tm:
						# Please note that from V3 and below, the TM only have 2 languages.
						print('TM v3')		
						self.translation_memory = pd.DataFrame()
						self.translation_memory['en'] = all_tm['EN']
						self.translation_memory['en'] = self.translation_memory['en'].str.lower()
						self.translation_memory['ko'] = all_tm['KO']
						self.translation_memory['ko'] = self.translation_memory['ko'].str.lower()
					else:
						print('No TM for this ProjectID')
						self.translation_memory = pd.DataFrame()
	
			
				elif isinstance(all_tm, list):
					print('TM v2')
					# Consider drop support
					self.translation_memory = pd.DataFrame()
					for Pair in all_tm:
						new_row = {'en': Pair[1], 'ko':Pair[0],}
						self.translation_memory = self.translation_memory.append(new_row, ignore_index=True)
				else:
					print('Current TM format:')
					print(type(all_tm))		
			except Exception  as e:
				print("Error:", e)
				print('Fail to load pickle file')
				return
		print('Size of loaded TM', len(self.translation_memory))			
		self.translation_memory.drop_duplicates(inplace=True)
		self.translation_memory_size = len(self.translation_memory)
		print('Size of optimized TM', self.translation_memory_size)		

	# Update TM from temporary_tm to pickle file
	def append_translation_memory(self):
		new_tm_size = len(self.temporary_tm)
		print('Size of temporary TM: ', new_tm_size)

		if len(self.temporary_tm) > 0:
			while True:
				try:
					with open(self.tm_path, 'rb') as pickle_load:
						all_tm = pickle.load(pickle_load)
					if isinstance(all_tm, dict):
						# TM format v4
						if self.glossary_id in all_tm:
							print('TM v4 format')
							self.translation_memory = all_tm[self.glossary_id]
						# TM format v3
						elif 'en' in TM:
							print('TM v3 format')
							self.translation_memory = pd.DataFrame({'en': all_tm['en'],'ko': all_tm['ko']})
			
					elif isinstance(all_tm, list):
						print('TM v2 format')
						self.translation_memory = pd.DataFrame()
						for Pair in all_tm:
							new_row = {'en': Pair[1], 'ko':Pair[0]}
						self.translation_memory = self.translation_memory.append(new_row, ignore_index=True)
				except:
					print('Fail to load tm')
					all_tm = {}
					
				if isinstance(self.translation_memory, pd.DataFrame):
					self.translation_memory = self.translation_memory.append(self.temporary_tm)
				else:
					self.translation_memory = self.temporary_tm

				all_tm[self.glossary_id] = self.translation_memory
				
				try:
					with open(self.tm_path, 'wb') as pickle_file:
						print("Updating pickle file....", self.tm_path)
						pickle.dump(all_tm, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
					
					self.init_temporary_tm()
					print('Size TM in memory', len(self.temporary_tm))
					return new_tm_size
				except Exception  as e:
					print("Error:", e)
		return new_tm_size
	
	def export_current_translation_memory(self):
	
		while True:
			try:
				with open(self.tm_path, 'rb') as pickle_load:
					all_tm = pickle.load(pickle_load)
				if isinstance(all_tm, dict):
					# TM format v4
					if self.glossary_id in all_tm:
						print('TM v4 format')
					elif 'en' in TM:
						all_tm = {}
		
				elif isinstance(all_tm, list):
					all_tm = {}
			except:
				print('Fail to load tm')
				all_tm = {}

			if isinstance(self.translation_memory, pd.DataFrame):
				save_data = self.translation_memory.append(self.temporary_tm)
			else:
				save_data = self.temporary_tm
			save_data = save_data.reindex()
			all_tm[self.glossary_id] = save_data
			
			try:
				with open(self.tm_path, 'wb') as pickle_file:
					print("Updating pickle file....", self.tm_path)
					pickle.dump(all_tm, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
				
				self.init_temporary_tm()
				
				return
			except Exception  as e:
				print("Error:", e)
		
		return 
		
	def refresh_translation_memory(self):
		self.import_translation_memory()

	# Add a KR-en pair into TM
	def generate_temporary_tm(self, str_translated = "", str_input = ""):
		translated = str_translated.lower()
		Input = str_input.lower()
		if self.from_language in self.temporary_tm:
			if Input not in self.temporary_tm[self.from_language]:	
				new_row = {self.to_language: translated, self.from_language: Input}
				self.temporary_tm = self.temporary_tm.append(new_row, ignore_index=True)
		else:
			new_row = {self.to_language: translated, self.from_language: Input}
			self.temporary_tm = self.temporary_tm.append(new_row, ignore_index=True)

	# Remove duplicated pair, lower string in the TM
	def optimize_translation_memory(self):
		print('Optimizing TM...')
		print('Old TM:', len(self.translation_memory))
		self.import_translation_memory()

		self.translation_memory = self.translation_memory.append(self.temporary_tm)
		self.translation_memory.drop_duplicates(inplace=True)

		print('New TM:', len(self.translation_memory))

		print('Optmize TM completed...')
		self.export_current_translation_memory()

	# Used in TM Manager tool
	# to remove TM pair in the TM
	# Need to update
	def remove_tm_pair(self, index=[]):
		if isinstance(index, int):
			list_to_remove = [index]
		elif isinstance(index, list):
			list_to_remove = index
		else:
			return False	

		while True:
			try:
				with open(self.tm_path, 'rb') as pickle_load:
					all_tm = pickle.load(pickle_load)
				if isinstance(all_tm, dict):
					# TM format v4
					if self.glossary_id in all_tm:
						print('TM v4 format')
					elif 'en' in TM:
						all_tm = {}
		
				elif isinstance(all_tm, list):
					all_tm = {}
			except:
				print('Fail to load tm')
				all_tm = {}

			if isinstance(self.translation_memory, pd.DataFrame):
				save_data = self.translation_memory.append(self.temporary_tm)
			else:
				save_data = self.temporary_tm

			all_tm[self.glossary_id] = save_data
			
			try:
				with open(self.tm_path, 'wb') as pickle_file:
					print("Updating pickle file....", self.tm_path)
					pickle.dump(all_tm, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
				
				self.init_temporary_tm()
				
				return
			except Exception  as e:
				print("Error:", e)
		
		return 


		# If Translation Memory is exist, replace the text with the defined one.
	# This method can speed up the translate progress x100 time 
	# and improve the translation speed.
	def memory_translate(self, source_text):
		# Use the previous translate result to speed up the translation progress
		source_text = source_text.lower()

		try:
			if len(self.translation_memory) > 0:
				#translated = self.translation_memory[self.to_language].where(self.translation_memory[self.from_language] == source_text)[0]
				translated = self.translation_memory.loc[self.translation_memory[self.from_language] == source_text]
				if len(translated) > 0:
					#print('TM translate', translated)
					return translated.iloc[0][self.from_language]

		except Exception  as e:
			#print('Error message (TM):', e)
			pass
		
		try:
			if len(self.temporary_tm) > 0:
				#translated = self.temporary_tm[self.to_language].where(self.temporary_tm[self.from_language] == source_text)[0]
				translated = self.temporary_tm.loc[self.temporary_tm[self.from_language] == source_text]
				if len(translated) > 0:
					#print('Temporary TM translate', translated)
					return translated.iloc[0][self.from_language]

		except Exception  as e:
			#print('Error message(temporary TM):', e)
			return False

		return False

#########################################################################
# Toggle function
#########################################################################
	
	def source_language_predict_enable(self, Toggle = True):
		self.source_language_predict = Toggle
		#print('Pridict mode: ', Toggle)	

	def tm_translate_enable(self, Toggle = True):
		#print('Obsoleted')
		self.proactive_memory_translate = Toggle
		#print('Translation Memory mode: ', Toggle)	

	def tm_update_anable(self, Toggle = True):
		self.tm_update = Toggle
	#	print('Translation Memory update mode: ', Toggle)		