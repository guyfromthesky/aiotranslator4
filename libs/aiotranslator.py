#Regular expression handling
from logging import error
import re
import base64
#http request and parser
from html import unescape
# Unuseds
# import urllib.request
#import urllib.parse
from urllib.parse import urlparse
#import html
# Unused
# import requests, uuid, 
import json

from google.cloud import translate_v3 as translator
from google.cloud import storage
from google.cloud import logging
from google.cloud.translate_v3.types.translation_service import Glossary

import pandas as pd
#import numpy as np

#System lib
import os
import sys
import unicodedata
import string
import socket

import pickle
# Unused
#import time
from datetime import datetime
import csv

from pandas.core.frame import DataFrame

from libs.version import get_version

Tool = "translator"
rev = 4113
ver_num = get_version(rev)
Translatorversion = Tool + " " + ver_num

# self.temporary_tm: @Manager.List
# If the translator is run in multiple process, the temporary 
# TM can be share with this feature.
# self.tm_path: @String
# Location of TM file.
# When the translator is created, the TM will be loaded.


class Translator:
	def __init__(self, 
		from_language = 'ko', 
		to_language = 'en', 
		source_language_predict = True, 
		proactive_memory_translate = True, 
		tm_update = True, 
		glossary_id = None, 
		temporary_tm = None,
		tm_path = None,
		# Tool that is currently use this libs
		used_tool = 'writer',
		tool_version = None,
		bucket_id = 'nxvnbucket',
		db_list_uri = 'config/db_list.csv',
		project_bucket_id = 'credible-bay-281107',
		**kwargs
	):
		
		self.from_language = self.correct_language_code(from_language)
		self.to_language = self.correct_language_code(to_language)	
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
		self.glossary_size = 0

		# Get the temp folder location for Windows/Mac
		self.init_config_path()

		# Check and get the location of TM file
		# If path is invalid or not stated, use local TM
		self.init_tm_path(tm_path)
	
		# Select correct log file.
		self.init_logging_file()

		#self.SpecialSheets = ['kr_only', 'en_only', 'name']
		self.special_tag = ['header', 'name', 'en_only', 'kr_only', 'cn_only', 'jp_only', 'vi_only', 'exception']
		self.supported_language = ['ko', 'en', 'cn', 'jp', 'vi']
		self.supported_language_code = ['ko', 'en', 'zh-TW', 'ja', 'vi']
		self.glossary_language = ['ko', 'en']
		# Obsoleted
		#self.init_db_data()

		self.temporary_tm = temporary_tm

		self.translation_memory = None
		self.translation_memory_size = 0

		self.exception_Char = string.punctuation + string.digits
		self.accepted_char = string.punctuation 
		self.printable = string.printable
		
		# Flag for user who is banned.
		# Get user name of the Windows account
		self.get_user_name()

		# Get name of the PC that currently in use
		self.get_pc_name()

		# Minimun version allowed to be used.
		# DB version
		self.version = '-'
		# Update day of the DB
		self.update_day = '-'

		try:
			current_time = datetime.now()
			#print('Load bucket from glob')
			# List of the glossary uploaded.
			# The list is also the list that display in the tool.
			self.load_config_from_bucket()
			#print('Total time to load bucket list:', str(datetime.now() - current_time))
			current_time = datetime.now()
			# Replace this function with the glossary init
			# Get the glossary list and length

			# Check if the glossary is exist or not
			# Create the glassary if any (require permission)
			# Display the length of the
			self.prepare_glossary_info()


			print('Total time to load db:', str(datetime.now() - current_time))
		except Exception  as e:
			print("Error when loading bucket:", e)


		# Send tracking record from previous run to logging server.
		#tracking_tesult = self.send_tracking_record()

		# Init tracking request
		self.last_section_tm_request = 0
		self.last_section_invalid_request = 0
		self.last_section_api_usage = 0

######################################################################################################
# INIT FUNCTION
######################################################################################################
	# Obsoleted
	def init_db_data(self):
		# The multi-language DB.
		self.all_header = pd.DataFrame()
		self.dictionary = []
		'''
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
		# The DB that only be used to translate from Vietnamese to other language.
		self.vi_dictionary = []
		'''
		self.header = []
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
		if self.temporary_tm != None:
			self.temporary_tm[:]
		else:
			self.temporary_tm = []	


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
		self.Client = translator.TranslationServiceClient()	
		self.Parent = f"projects/{self.project_id}/locations/{self.location}"
		self.Glossary = self.Client.glossary_path(self.project_id, self.location, self.glossary_id)
		self.Glossary_Config = translator.TranslateTextGlossaryConfig(glossary=self.Glossary)

	# Check and remove later
	def get_time_stamp(self):
		now = datetime.now()
		year =  now.isocalendar()[0]
		week =  now.isocalendar()[1]
		day =  now.isocalendar()[2]
		return str(year) + "_" + str(week) + '_' + str(day)

	def get_timestamp(self):
		return str(datetime.now())

	# Might use on DB uploader
	def get_glossary_list(self):
		#print('Getting Glossary info')
		self.glossary_list = []
		self.glossary_list_full = self.full_list_glossaries()
		for _gloss in self.glossary_list_full:
			self.glossary_list.append(_gloss)		


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
		print('Send tracking record to logging')
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
			try:
				hostname = socket.gethostname()
				ip_address = socket.gethostbyname(hostname)
			except:
				ip_address = ''	

			data_object = {
				'user': self.user_name,
				'device': self.pc_name,
				'ip': ip_address,
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
		elif self.from_language == 'en':
			for i in range(len(string)):
				c = string[i]
				if unicodedata.category(c)[0:2] == 'Ll' : # other characters
					try:
						if 'LATIN' in unicodedata.name(c) : return True
					except:
						continue
			return False
		else:
			return True	

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
		remained_length = len(RawText)
		LowerCase_text = source_text
		
		if self.to_language == 'en':
			temp_dict = self.dictionary + self.en_dictionary
		elif self.to_language == 'vi':	
			temp_dict = self.dictionary + self.vi_dictionary
		else:
			temp_dict= self.dictionary 
		#print('Temp dict for Korean translate', len(temp_dict))

		for pair in temp_dict:
			if remained_length == 0:
				break
			# Old is en text in the dict
			Old = pair[0].strip()
			
			# New is the KR text we want to replace with
			New = " " + pair[1].strip() + " "
			#New = pair[1].strip()
			# IF there is the defined text in the sentence
			StartFind = 0
			while LowerCase_text.find(Old, StartFind) != -1:
				#print('LowerCase_text', LowerCase_text)
				#print('Old', Old)
				#print('StartFind', StartFind)
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
						remained_length -= len(Raw_Old)
						#RawText[location, StartFind-1] = RawText

						#print('Replace: ', FirstChar + Old + NextChar, ' by ',  FirstChar + New + NextChar)
					else:
						#print('ORD', ord(NextChar))
						#print('Invalid NextChar char: \'', NextChar, '\'')
						break
						
				else:
					#rint('ORD', ord(FirstChar))
					#print('Invalid 1st char: \'', FirstChar, '\'')
					break
	
				LowerCase_text = RawText	
		# Remove the space from both side of the text
		# The space that we've add above.
		RawText = RawText.strip()
		
		if remained_length == 0:
			translated = True
		else:
			translated = False

		return RawText, translated

	def korean_pre_translate(self, input):
		#print('korean_pre_translate')
		# Use for Translating en -> KR
		# It's a litle complicated....
		# To cover some special case can happen.
		RawText = input
		remained_length = len(RawText)
		source_text = RawText.lower()
		if self.to_language == 'ko':
			temp_dict = self.dictionary + self.ko_dictionary
		elif self.to_language == 'cn':	
			temp_dict = self.dictionary + self.cn_dictionary
		elif self.to_language == 'jp':	
			temp_dict = self.dictionary + self.jp_dictionary	
		else:
			temp_dict= self.dictionary 
		#print('Temp dict for English translate', len(temp_dict))

		for pair in temp_dict:
			if remained_length == 0:
				break
			
			# Old is en text in the dict
			Old = pair[0].strip()
			
			# New is the KR text we want to replace with
			New = " " + pair[1].strip() + " "
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
					remained_length -= len(Raw_Old)
					#print("RawText", RawText)
				source_text = RawText.lower()
		# Remove the space from both side of the text
		# The space that we've add above.
		RawText = RawText.strip()
		if remained_length == 0:
			translated = True
		else:
			translated = False

		#print('Raw result:', RawText)
		return RawText, translated

######################################################################
# All translate function
######################################################################
	# Translator main function.
	# All the text will be passed into this function.
	def translate(self, Input):
		if self.to_language == self.from_language:
			return Input
		#print('Translate:', Input)
		if isinstance(Input, list):
			source_text = Input
		elif isinstance(Input, str):
			source_text = [Input]
		else:
			return False

		#print('source_text', source_text)

		raw_source = []
		to_translate = []
		to_translate_index = []
		translation = []
	
		for text in source_text:
			translation.append(text)

		
		for i in range(len(translation)):
			text = str(translation[i])
			# Check if the text we send to google translate does not belong to these case below:
			# + Number
			# + Url
			# + In-valid source language
			# + Text has been ranslated before
			validation = self.ValidateSourceText(text)
			#print('Details:', text, 'Result:', validation)
			if validation == False:
				continue
			if validation == True:
				try:
					# Check if the text has been request to translate
					# This check is to remove duplicate translate request
					index_num = raw_source.index(text)
					# If the index number is found, appen the index
					to_translate_index[index_num].append(i)
				except Exception  as e:
					#print('Exception: ', e)
					raw_source.append(text)
					to_translate.append(text)
					to_translate_index.append([i])
				#print('Append done')
				#raw_source.append(text)
				#to_translate.append(pre_translate)
				#to_translate_index.append(i)
			else:
				#translated by memory
				translation[i] = validation

		if len(to_translate) > 0:
			try:
				translated = self.activated_translator(to_translate)
			except Exception  as e:
				print('error:', e)
				translated = []
		
		else:
			translated = []	

		#print('translated', translated)

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
		
		#print('Active translator', 'from:', self.from_language, 'to:', self.to_language)
		
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
		_translate_fail = False
		translation = None
	
		try:	
			#translation = self.google_translate_v3(source_text)
			if self.glossary_id == "":
				translation = self.google_translate_v3(source_text)
			else:	
				if self.from_language in self.glossary_language and self.to_language in self.glossary_language:
					translation = self.google_glossary_translate(source_text)
				else:
					translation = self.google_translate_v3(source_text)
		except Exception  as e:
			print('Activated translation error:', e)
			_error_message = e

		if translation == None:	
	
			try:
				client = logging.Client()
			except:
				pass

			log_name = 'translator-error'
			logger = client.logger(log_name)	
			
			data_object = {
				'user': self.user_name,
				'device': self.pc_name,
				'project': self.glossary_id,
				'tool': self.used_tool,
				'tool_ver': self.tool_version,
				'translator_ver': ver_num,
				'tm_size': self.translation_memory_size,
				'tm_path': self.tm_path,
				'error_message': str(_error_message),
			}

			tracking_object = {
				'user': self.user_name,
				'details': data_object
			}
			
			try:
				logger.log_struct(tracking_object)
			except Exception  as e:
				print('exception:', e)
				result = False
		
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

	def correct_language_code(self, language_code):
		"""Correct support language from tool to google standard"""
		if language_code == 'jp':
			return 'ja'
		if language_code == 'cn':
			return 'zh-TW'
		return language_code

	def google_translate_v3(self, source_text):
		#print('Translate with GoogleAPItranslate')
		"""Translates a given text with google api."""
		ToTranslate = []
		
		if isinstance(source_text, list):
			ToTranslate = source_text
		else:
			ToTranslate = [source_text]

		# Supported language codes: https://cloud.google.com/translate/docs/languages
		
		Client = translator.TranslationServiceClient()
		Parent = f"projects/{self.project_id}/locations/{self.location}"
		target_language_code = self.correct_language_code(self.to_language)
		#print('target_language_code', target_language_code)
		source_language_code = self.correct_language_code(self.from_language)
		#print('source_language_code', source_language_code)
		response = Client.translate_text(
			request={
				"contents": ToTranslate,
				"target_language_code": target_language_code,
				"source_language_code": source_language_code,
				"parent": Parent,
			}
		)

		ListReturn = []
		for translation in response.translations:
			ListReturn.append(unescape(translation.translated_text))

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

		# Supported language codes: https://cloud.google.com/translate/docs/languages
		Client = translator.TranslationServiceClient()
		Parent = f"projects/{self.project_id}/locations/{self.location}"
		Glossary = Client.glossary_path(self.project_bucket_id, "us-central1", self.glossary_id)
		#Glossary = Client.glossary_path(self.project_bucket_id, "us-central1", 'General-DB')
		#print('Glossary', Glossary)
		Glossary_Config = translator.TranslateTextGlossaryConfig(glossary=Glossary)
		
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
		for translation in response.glossary_translations:
			ListReturn.append(unescape(translation.translated_text))

		#print('ListReturn', ListReturn)
		return ListReturn

############################################################################
# Setting function
############################################################################
	def set_subscription(self, Subscription):
		self.Subscription = Subscription

	def set_subscription_key(self, SubscriptionKey):
		self.SubscriptionKey = SubscriptionKey	

	def set_target_language(self, target_language):
		if target_language != self.to_language:
			self.set_language_pair(self.from_language, self.correct_language_code(target_language))
			

	def set_source_language(self, source_language):
		if source_language != self.from_language:
			self.set_language_pair( self.correct_language_code(source_language), self.to_language)

	def set_language_pair(self, source_language, target_language):
		if self.from_language == source_language and self.to_language == target_language:
			return
		print('Set languag pair:', 'Source - ', source_language, 'Target -', target_language)
		if source_language != target_language:
			self.from_language = source_language
			self.to_language = target_language
			
			if self.used_tool == 'writer':
				self.update_header_from_dataframe()
				self.update_db_from_dataframe()
			else:	
				self.update_tm_from_dataframe()

	def set_language_pair_only(self, source_language, target_language):
		if self.from_language == source_language and self.to_language == target_language:
			return
		print('Set languag pair:', 'Source - ', source_language, 'Target -', target_language)
		if source_language != target_language:
			self.from_language = source_language
			self.to_language = target_language
			
			if self.used_tool == 'writer':
				self.update_header_from_dataframe()
				self.update_db_from_dataframe()
			else:	
				self.update_tm_from_dataframe()			

	def swap_language(self):
		Temp = self.from_language
		self.from_language = self.to_language	
		self.to_language = Temp
		#self.update_db_from_dataframe()
		#self.import_translation_memory()

	def set_translator_agent(self, TranslatorAgent):
		self.TranslatorAgent = TranslatorAgent
		#print('Translator Agent has been updated to ', TranslatorAgent)	


	
################################################################################################
# Glossary manager
################################################################################################
	
	def list_glossaries(self):
		
		List = []
		client = translator.TranslationServiceClient()

		parent = f"projects/{self.project_id}/locations/{self.location}"

		for glossary in client.list_glossaries(parent=parent):
			Gloss = glossary.name.split('/')[-1]
			if '_' not in Gloss:
				List.append(Gloss)		
		return List

	def full_list_glossaries(self):
		
		List = {}
		client = translator.TranslationServiceClient()

		parent = f"projects/{self.project_bucket_id}/locations/{self.location}"

		for glossary in client.list_glossaries(parent=parent):
			_gloss_name = glossary.name.split('/')[-1]
			List[_gloss_name] = {}
			List[_gloss_name]['size'] = glossary.entry_count
			List[_gloss_name]['language'] = []
			for language_code in glossary.language_codes_set.language_codes:
				List[_gloss_name]['language'].append(language_code)
		return List

	def get_glossary(self, glossary_id= None, timeout=180,):
		# Get glossary from the running project
		client = translator.TranslationServiceClient()
		name = client.glossary_path(self.project_id, self.location, glossary_id)
		glossary = client.get_glossary(name = name)

		return 	glossary
	
	def load_config_from_bucket(self, file_uri= None, timeout=180,):

		cloud_client = storage.Client()
		bucket = cloud_client.get_bucket(self.bucket_id)
		blob = bucket.get_blob(self.db_list_uri)
		#print('blob', blob)
		
		try:
			listdb = blob.download_as_text()
		except Exception as e:
			print('Fail to load blob:', e)
			return
	
		mydb = listdb.split('\r\n')
		self.bucket_db_list = []
		for pair in mydb:

			data = pair.split(',')
			Valid = True
			for element in data:
				if element == "" or element == None:
					Valid = False
			if Valid:
				id = str(data[0]).replace('\ufeff', '')
				URI = str(data[1])
				self.bucket_db_list.append(id)
				self.glossary_data_list.append([id, URI])
		#print('Bucket glossary list: ', self.bucket_db_list)		

	def download_db_to_file(self, glossary_id, download_path):
		for gloss_data in self.glossary_data_list:
			gloss_id = gloss_data[0]
			if glossary_id == gloss_id:
				_uri =  gloss_data[1]

			
		if _uri == None:
			print('No old DB, skip dowwnload')
			with open(download_path, 'w', newline='', encoding='utf_8_sig') as csv_db:
				db_writer = csv.writer(csv_db, delimiter=',')
				db_writer.writerow(['','ko', 'en', 'zh-TW', 'ja', 'vi', 'description'])
				
		sourcename, ext = os.path.splitext(_uri)
		_uri = sourcename + '_db' + ext	
		print('Download db from:', _uri)
		cloud_client = storage.Client()
		bucket = cloud_client.get_bucket(self.bucket_id)
		blob = bucket.get_blob(_uri)
		

		if blob != None:
			try:
				blob.download_to_filename(download_path)	
			except Exception as e:
				print('Fail to load blob:', e)	
				return
		'''
		with open(download_path,'wb') as f:
			cloud_client.download_to_file(blob, f)
		'''

	def _load_header_from_blob(self, header_uri):
		cloud_client = storage.Client()

		bucket = cloud_client.get_bucket(self.bucket_id)

		blob = bucket.get_blob(header_uri)
		if blob != None:
			try:
				_download_path = self.config_path + '\\AIO Translator\\temp_header.csv'
				blob.download_to_filename(_download_path)	
			except Exception as e:
				print('Fail to load blob:', e)
				self.header = []	
				return

			# Load DB as DataFrame
			self.all_header = pd.read_csv(_download_path, usecols=self.supported_language)
			try:
				os.remove(_download_path)
			except Exception as e:
				print("Error when removing header:", _download_path)	
			self.update_header_from_dataframe()
		else:
			self.header = []	

	def load_info_from_glob(self, file_uri= None, timeout=180,):
	
		cloud_client = storage.Client()

		bucket = cloud_client.get_bucket(self.bucket_id)

		blob = bucket.get_blob(file_uri)
		if blob == None:
			self.version = '-'
			self.update_day = '-'
			return
		try:
			listdb = blob.download_as_text()
		except Exception as e:
			print('Fail to load blob:', e)
			return

		# Split DB into row.
		
		mydb = listdb.split('\r\n')
		
		# Split row into list
		split_db = lambda x: x.split(',')
		list_db = list(map(split_db, mydb))

		
		# Retrive info data and remove from DB
		for item in list_db:
			key = item[0].replace('\ufeff', '')
			if key == 'date':
				self.update_day = item[1]

	
	def load_db_from_glob(self, file_uri= None, timeout=180,):

		cloud_client = storage.Client()

		bucket = cloud_client.get_bucket(self.bucket_id)

		blob = bucket.get_blob(file_uri)
		if blob != None:
			try:
				_download_path = self.config_path + '\\AIO Translator\\temp_db.csv'
				blob.download_to_filename(_download_path)	
			except Exception as e:
				print('Fail to load blob:', e)
				return

			# Load DB as DataFrame
			self.all_db = pd.read_csv(_download_path, usecols=self.glossary_language)
			try:
				os.remove(_download_path)
			except Exception as e:
				print("Error when removing header:", _download_path)
			self.update_db_from_dataframe()
		else:
			self.dictionary = []	

	# Filter DB and store in suitable variable
	def update_header_from_dataframe(self):
		
		if self.from_language != self.to_language:
			if self.from_language in self.all_header and self.to_language in self.all_header:
				#Create normal dict list:
				print('Create Header list from Dataframe')
				
				header = self.all_header[[self.from_language, self.to_language]]
				header = header.dropna(subset=[self.from_language])
				header = header.dropna(subset=[self.to_language])
				header = header.drop_duplicates()
				self.header = header.values.tolist()
			else:
				self.header = []
		else:
			self.header = []
	
	def update_db_from_dataframe(self):
		print('Update DB from dataframe')
		# Drop N/A value
		if self.from_language != self.to_language:
			if self.from_language in self.all_db and self.to_language in self.all_db:
				#Create normal dict list:
				print('Create DB list from Dataframe')
				dictionary = self.all_db[[self.from_language, self.to_language]]
				dictionary = dictionary.drop_duplicates()
				self.dictionary = dictionary[self.from_language].astype(str).values.tolist()
				#self.dictionary = dictionary[self.from_language].astype(str).values.tolist() + dictionary[self.to_language].astype(str).values.tolist()
			else:
				self.dictionary = []
		else:
			self.dictionary = []


	def get_glossary_length(self, timeout=180,):
		client = translator.TranslationServiceClient()
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
	# Currently not use
	def create_glossary(self, input_uri= None, glossary_id=None, supported_language = ['en', 'ko'], timeout=180,):

		client = translator.TranslationServiceClient()

		name = client.glossary_path(self.project_id, self.location, glossary_id)
		
		language_codes_set = translator.types.Glossary.LanguageCodesSet(
			language_codes = supported_language
		)

		gcs_source = translator.types.GcsSource(input_uri=input_uri)

		input_config = translator.types.GlossaryInputConfig(gcs_source=gcs_source)

		glossary = translator.types.Glossary(
			name=name, language_codes_set=language_codes_set, input_config=input_config
		)

		parent = f"projects/{self.project_id}/locations/{self.location}"
		try:
			operation = client.create_glossary(parent=parent, glossary=glossary)
			return operation.result(timeout)
		except Exception as e:
			print('Error while uploading glossary:', e)
			return False
	
	# Delete the glossary that use for glossary_translate
	def delete_glossary(self, glossary_id= None, timeout=180,):
		"""Delete a specific glossary based on the glossary id."""
		client = translator.TranslationServiceClient()

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

	def prepare_glossary_info(self):
		#print('Get glossary list and length:')
		# self.glossary_list = [{glossary_id: glossary_length}...{}]
		try:
			self.get_glossary_list()
			#print('Glossary list ', self.glossary_list)
			#print('Glossary full list', self.glossary_list_full)
			
			# Check if the glossary is exist
			# self.glossary_id

			# Create glossary if any

			# Update db_length
			if self.glossary_id in self.glossary_list:
				#print('Update db length')
				self.glossary_size = self.glossary_list_full[self.glossary_id]['size']
				self.glossary_language = self.glossary_list_full[self.glossary_id]['language']
				#print('Get URI from glossary_id ')
				uri = self.get_glossary_path(self.glossary_id)

				if uri != None:
					_uri_name, _ext = os.path.splitext(uri)
					_db_uri = _uri_name + "_" + 'db' + _ext
					_header_uri = _uri_name + "_" + 'header' + _ext
					_info_uri = _uri_name + "_" + 'info' + _ext
					#print('URI:', _header_uri)

					
					print("Load info from glob:", _info_uri)
					self.load_info_from_glob(_info_uri)

					if self.used_tool == 'writer':
						print("Load header from glob:", _header_uri)
						self._load_header_from_blob(_header_uri)
						print("Load db from glob:", _db_uri)
						self.load_db_from_glob(_db_uri)
						print('Load db from bucket done')	

					else:
						self.init_db_data()
				else:
					self.init_db_data()
				print('Load data from bucket done')	
			else:
				print('Init blank dict')
				self.init_db_data()
			#print('Loading done!')
		except Exception as e:
			print('[Error] prepare_db_data:', e)
			self.init_db_data()
		
		if self.proactive_memory_translate:
			self.import_translation_memory()

	def prepare_db_data(self):
		print('prepare_db_data')
		if self.glossary_id not in [None, ""]:
			try:
				print('Get URI from glossary_id ')
				uri = self.get_glossary_path(self.glossary_id)
				print('URI:', uri)
				print("Load DB from glob:", uri)
				self.load_db_from_glob(uri)
				print('Loading done!')
			except Exception as e:
				print('[Error] prepare_db_data:', e)

		
			self.dictionary = []
			#self.header = []

		if self.proactive_memory_translate:
			#self.import_translation_memory()
			self.import_translation_memory()

	# Store the DB in base64 format for csv format friendly
	def basse64_encode(self, string_to_encode):
		raw_encoded_string =  str(base64.b64encode(string_to_encode.encode('utf-8')))
		encoded_string = re.findall(r'b\'(.+?)\'', raw_encoded_string)[0]
		
		return encoded_string

	def base64_decode(self, string_to_decode):
		if string_to_decode in ['', None] :
			return ''
		try:
			return base64.b64decode(string_to_decode).decode('utf-8')
		except:
			return string_to_decode
	
	# Decode the DB from base64 format and fill empty element (by '') to the list.
	# All tag are not listed in the special_tag will be considered as 'dictionary'
	def base64_decode_list(self, list_string_to_decode):
		#print('list_string_to_decode', list_string_to_decode)
		DataFrame_len = len(self.supported_language) + 1

		if list_string_to_decode[0] not in self.special_tag:
			tag = 'dictionary'
		else:
			tag = list_string_to_decode[0]

		decode = lambda x: self.base64_decode(x)
		decoded_list = list(map(decode, list_string_to_decode[1:]))

		decoded_list.insert(0, tag)

		# Fill empty elements:
		missing_element_count = DataFrame_len - len(decoded_list)
		return_list = decoded_list + [""] * (missing_element_count)

		return return_list

################################################################################################
# Bucket manager
# Backet is the storage that store DB
# Main bucket that this tool use is "nxvnbucket"
################################################################################################

	# Replace the DB file by the new one
	# Need to rename the old DB file for backup purpose
	# 	-> Update later
	def upload_blob(self, blob_id, upload_path):
		
		from google.cloud import storage
		sclient = storage.Client()
		
		print('Get bucket...')
		current_time = datetime.now()
		bucket = sclient.get_bucket(self.bucket_id)	
		print('Total time to get bucket:', str(datetime.now() - current_time))
		print('Get blob...')
		current_time = datetime.now()
		blob = bucket.blob(blob_id)
		print('Total time to get blob:', str(datetime.now() - current_time))

		print('Upload to blob')
		current_time = datetime.now()
		blob.upload_from_filename(filename = upload_path)
		print('Total time to upload file:', str(datetime.now() - current_time))
		
	def download_blob(self, blob_id, download_path):

		from google.cloud import storage
		sclient = storage.Client()
		current_time = datetime.now()
		print('Get bucket...')
		current_time = datetime.now()
		bucket = sclient.get_bucket(self.bucket_id)	
		
		
		print('Get blob...')
		
		blob = bucket.blob(blob_id)
		print('Total time to get blob:', str(datetime.now() - current_time))

		print('Download blob to')
		current_time = datetime.now()
		download_file = blob.download_as_text()
		print('Total time to download blob:', str(datetime.now() - current_time))
		#print('download_file:', download_file)

	# Replace the DB file by the new one
	# Need to rename the old DB file for backup purpose
	# 	-> Update later
	def backup_and_update_blob(self, glossary_id, address):
		from google.cloud import storage
		sclient = storage.Client()
		
		#db_path = address['db']
		#header_path = address['header']
		#info_path = address['info']
		
		#gloss = self.get_glossary(glossary_id)

		bucket = sclient.get_bucket(self.bucket_id)
		try:
			blob_id = self.get_glossary_path(glossary_id)
		except:
			return False	
		
		_blob_name, _ext = os.path.splitext(blob_id)

		for file_name in ['db', 'header', 'info']:
			current_id = _blob_name + "_" + file_name + _ext
			blob = bucket.blob(current_id)
			if file_name == 'db':
				try:
					current_timestamp  = self.get_timestamp()
					list_folder = _blob_name.split('/')
					db_name = list_folder[-1]
					root = list_folder[0:-1]
					root_name = '/'.join(root)
					new_blob = root_name + '/Backup/' + db_name + "_db_" + current_timestamp + _ext
					print('Backup blob to: ', new_blob)
					bucket.copy_blob(blob, bucket, new_blob)
				except Exception as e:
					print('Fail to backup blob:', e)
				_gloosary_id = current_id

			Upload_Path = address[file_name]

			supported_language = address['language']
			print('Uploading to blob:', current_id)
			blob.upload_from_filename(filename = Upload_Path)
			print('Uploading done.')
		print('Create glossary from blob: ', _gloosary_id)
		return self.update_glossary(glossary_id, _gloosary_id, supported_language)
	

	def delete_glossary(self, glossary_id= "", timeout=180,):
		"""Delete a specific glossary based on the glossary ID."""
		client = translator.TranslationServiceClient()
		name = client.glossary_path(self.project_bucket_id , "us-central1", glossary_id)
		operation = client.delete_glossary(name=name)
		result = operation.result(timeout)
		print("Deleted: {}".format(result.name))



	def update_glossary(self, glossary_id, db_uri, supported_language):
		from google.cloud import storage
		print('Provided uri:', db_uri)
		_uri = 'gs://nxvnbucket/' + db_uri
		print('URI: ', _uri)
		print('Glossary ID:', glossary_id)
		try:
			self.delete_glossary(glossary_id)
			print('Deleting blob')
		except Exception as e:
			print('Error while deleting glossary:', glossary_id, e)	
		
		print('Create glossary')
		
		return self.create_glossary(_uri, glossary_id, supported_language)

	
##########################################################
# TM Manager
# TM type: pd.DataFrame
# tm = {'project_id': pd.DataFrame}
# df = {'en': string_en, 'ko': string_ko, 'cn': string_cn, 'jp': string_jp}
##########################################################

	# Get the tm's path.
	# if tm is invalid, use local tm instead
	def init_tm_path(self, tm_path = None):
		if tm_path not in [None, '']:
			if os.path.isfile(tm_path):
				self.tm_path = self.correct_path_os(tm_path)
				return
		if self.used_tool == 'writer':
			self.tm_path = None
			return
		tm_path = self.config_path + '\\AIO Translator\\Local.pkl'
		self.tm_path = self.correct_path_os(tm_path)
		return

	def init_translation_memory(self):
		self.current_tm = pd.DataFrame(columns=self.supported_language)
		self.translation_memory_size = len(self.current_tm)	

	# Load TM detail from pickle file.
	# The TM support all supported languages (en, ko, jp, cn, vi)
	def import_translation_memory(self):
		#print('Import TM from pickle file', str(self.tm_path))

		self.init_temporary_tm()
		self.init_translation_memory()
		if self.tm_path == None:
			return
		if not os.path.isfile(self.tm_path):
			print('Pickle file not found')
			return
		else:
			try:
				with open(self.tm_path, 'rb') as pickle_load:
					all_tm = pickle.load(pickle_load)
					#print('all tm:', all_tm)
				if isinstance(all_tm, dict):
					# TM format v4
					if self.glossary_id in all_tm:
						print('TM v4')
						self.current_tm = all_tm[self.glossary_id]

					# TM format v3
					elif 'EN' in all_tm:
						# Please note that from V3 and below, the TM only have 2 languages.
						print('TM v3')		
						print(all_tm.keys())
						self.current_tm['en'] = all_tm['EN']
						self.current_tm['en'] = self.current_tm['en'].str.lower()
						self.current_tm['ko'] = all_tm['KO']
						self.current_tm['ko'] = self.current_tm['ko'].str.lower()
					else:
						print('No TM for this ProjectID')

				elif isinstance(all_tm, list):
					print('TM v2')
					# Consider drop support
					
					for Pair in all_tm:
						new_row = {'en': Pair[1], 'ko':Pair[0],}
						self.current_tm = self.current_tm.append(new_row, ignore_index=True)
				else:
					print('Current TM format:')
					print(type(all_tm))		
			except Exception  as e:
				print("Error:", e)
				print('Fail to load pickle file')
				return

		self.update_tm_from_dataframe()


	def update_tm_from_dataframe(self):
		print('Update TM from dataframe')
		if self.from_language != self.to_language:
			self.translation_memory = self.current_tm.dropna(subset=[self.from_language])
			self.translation_memory = self.translation_memory.dropna(subset=[self.to_language])
			#self.translation_memory = self.translation_memory[~self.translation_memory[self.to_language].isin([pd.NA])][[self.from_language, self.to_language]]
			self.translation_memory = self.translation_memory[[self.from_language, self.to_language]]
			#self.translation_memory.drop_duplicates(inplace=True)
		else:
			self.init_translation_memory()

		self.translation_memory_size = len(self.translation_memory)	

	# Update TM from temporary_tm to pickle file
	def append_translation_memory(self):
		print('Append translation memory')
		new_tm_size = len(self.temporary_tm)
		print('Size of temporary TM: ', new_tm_size)
		if self.glossary_id == "":
			_glossary = 'Default'
		else:
			_glossary = self.glossary_id

		if len(self.temporary_tm) > 0:
			while True:
				try:
					with open(self.tm_path, 'rb') as pickle_load:
						all_tm = pickle.load(pickle_load)
					if isinstance(all_tm, dict):
						# TM format v4
						if _glossary in all_tm:
							print('TM v4 format')
							self.translation_memory = all_tm[_glossary]
						# TM format v3
						elif 'en' in all_tm:
							print('TM v3 format')

							self.init_translation_memory()

							self.translation_memory = pd.DataFrame({'en': all_tm['en'],'ko': all_tm['ko']})
			
					elif isinstance(all_tm, list):
						print('TM v2 format')
						self.init_translation_memory()

						for Pair in all_tm:
							new_row = {'en': Pair[1], 'ko':Pair[0]}
						self.translation_memory = self.translation_memory.append(new_row, ignore_index=True)
				except Exception as e:
					print('Fail to load tm:', e)
					all_tm = {}
				if self.translation_memory.empty:
					self.init_translation_memory()

				for Pair in self.temporary_tm:
					try:
						self.translation_memory = self.append_tm_dataframe(self.translation_memory, Pair)
					except Exception as e:
						print('Append TM DF error:', e)	

					#self.translation_memory = self.translation_memory.append(Pair, ignore_index=True)

				all_tm[_glossary] = self.translation_memory
				
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
		
		if self.glossary_id == "":
			_glossary = 'Default'
		else:
			_glossary = self.glossary_id
		
		while True:
			try:
				with open(self.tm_path, 'rb') as pickle_load:
					all_tm = pickle.load(pickle_load)
				if isinstance(all_tm, dict):
					# TM format v4
					if _glossary in all_tm:
						print('TM v4 format')
					elif 'en' in all_tm:
						all_tm = {}
		
				elif isinstance(all_tm, list):
					all_tm = {}
			except:
				print('Fail to load tm')
				all_tm = {}
			
			save_data = self.translation_memory

			for Pair in self.temporary_tm:
				save_data = self.translation_memory.append(Pair, ignore_index=True)
			
			save_data = save_data.reindex()
			all_tm[_glossary] = save_data
			
			try:
				with open(self.tm_path, 'wb') as pickle_file:
					print("Updating pickle file....", self.tm_path)
					pickle.dump(all_tm, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
				
				self.init_temporary_tm()
				
				return
			except Exception  as e:
				print("Error:", e)
		
		return 
		
	def create_new_tm_file(self, new_tm_file):
	
		if self.glossary_id == "":
			_glossary = 'Default'
		else:
			_glossary = self.glossary_id

		all_tm = {}
		all_tm[_glossary] = None
		try:
			with open(new_tm_file, 'wb') as pickle_file:
				print("Updating pickle file....", new_tm_file)
				pickle.dump(all_tm, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)			
			return
		except Exception  as e:
			print("Error:", e)
		return 

	def refresh_translation_memory(self):
		self.import_translation_memory()

	# Temporary TM is a list of dict
	# {self.to_language: translated, self.from_language: Input}
	# Add a KR-en pair into TM
	def generate_temporary_tm(self, str_translated = "", str_input = ""):
		#print('Generate Temp TM:', str_translated, str_input)
		translated = str_translated.lower()
		Input = str_input.lower()
		new_row = {self.to_language: translated, self.from_language: Input}
		self.temporary_tm.append(new_row)

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
					elif 'en' in all_tm:
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
		if isinstance(self.memory_translate, DataFrame):
			try:
				if len(self.translation_memory) > 0:
					#translated = self.translation_memory[self.to_language].where(self.translation_memory[self.from_language] == source_text)[0]
					translated = self.translation_memory.loc[self.translation_memory[self.from_language] == source_text]
					#print('Mem translated:', translated)
					if len(translated) > 0:
						#print('TM translate', translated)
						return translated.iloc[0][self.to_language]

			except Exception  as e:
				print('Error message (TM):', e)
				pass
			
		# new_row = {self.to_language: translated, self.from_language: Input}
		# self.temporary_tm = self.temporary_tm.append(new_row)
		
		try:
			if len(self.temporary_tm) > 0:
				for pair in self.temporary_tm:
					if pair[self.from_language] == source_text:
						return pair[self.to_language]
		except Exception  as e:
			print('Error message(temporary TM):', e)
			return False

		return False

	def append_tm_dataframe(self, dataframe, pair, ):
		#print(dataframe)
		# pair: @dict
		index_value = pair[self.from_language]
		append_value = pair[self.to_language]

		index = dataframe.index

		if self.from_language in dataframe.columns:
			condition = dataframe[self.from_language] == index_value


		indices = index[condition]
		indices_list = indices.tolist()
		#print('indices_list', indices_list)

		if len(indices_list) == 0:
			dataframe = dataframe.append({self.from_language: index_value, self.to_language: append_value}, ignore_index=True)
			return dataframe
		else:
			append_indices = indices_list[0]
			if pd.isna(dataframe[self.to_language][append_indices]):
				dataframe[self.to_language][append_indices] = append_value
				return dataframe
			else:
				return dataframe

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

# Function for Document Translator
def generate_translator(
		my_translator_queue = None, 
		temporary_tm = None, 
		from_language = 'ko', 
		to_language = 'en', 
		glossary_id = None,
		used_tool = None,
		tm_path= None, 
		bucket_id = 'nxvnbucket',
		db_list_uri = 'config/db_list.csv',
		project_bucket_id = 'credible-bay-281107'):	
	print('Translator options:', locals())
	MyTranslator = Translator(	from_language = from_language, 
								to_language = to_language, 
								glossary_id =  glossary_id, 
								temporary_tm = temporary_tm,
								tm_path = tm_path, 
								used_tool = used_tool, 
								tool_version = ver_num,
								bucket_id = bucket_id,
								db_list_uri = db_list_uri,
								project_bucket_id = project_bucket_id)
	my_translator_queue.put(MyTranslator)