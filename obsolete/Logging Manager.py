from google.cloud import logging
from aioconfigmanager import ConfigLoader
import os
import time
from datetime import datetime, timedelta
import csv
import pickle


TranslatorAgent = 'googleapi'
from_language = 'en'
to_language = 'ko'
GlossaryID = 'V4GB'

AppConfig = ConfigLoader()
Configuration = AppConfig.Config
json = Configuration['License_File']['path']
print(Configuration['License_File']['path'])
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json

def get_time_stamp(number_of_day):
	datetime_object = datetime.today() - timedelta(days=number_of_day)
	date = str(datetime_object).split(' ')[0]
	#date_object = datetime.strptime(datetime_object, "%YYYY-%mm%-dd")
	# if you encounter a "year is out of range" error the timestamp
	# may be in milliseconds, try `ts /= 1000` in that case
	return date

def get_db_update_log(logger_name = 'db-update', record_day=7):
	try:
		client = logging.Client()
	except:
		pass
	log_name = logger_name
	logger = client.logger(log_name)
	now = datetime.now()
	timestamp = str(int(datetime.timestamp(now)))			
	output_file_csv = log_name + "_" + timestamp + '.csv'
	with open(output_file_csv, 'w', newline='', encoding='utf_8_sig') as csv_file:
		writer = csv.writer(csv_file, delimiter=',')
		writer.writerow(['TimeStamp', 'Device', 'Project', 'DB link'])
		timestring = get_time_stamp(30)
		for entry in logger.list_entries(page_size = 1000, filter_ = 'timestamp > \" ' + timestring + '\"'):
			timestamp = entry.timestamp.isoformat()
			details = entry.payload.split(',')
			row = [timestamp] + details
			writer.writerow(row)
	print("Done", output_file_csv)

def get_translation_usage_log(logger_name = 'translator-usage', record_day=7):
	try:
		client = logging.Client()
	except:
		pass
	log_name = logger_name
	logger = client.logger(log_name)
	now = datetime.now()
	timestamp = str(int(datetime.timestamp(now)))			
	output_file_csv = log_name + "_" + timestamp + '.csv'
	with open(output_file_csv, 'w', newline='', encoding='utf_8_sig') as csv_file:
		writer = csv.writer(csv_file, delimiter=',')
		writer.writerow(['Timestamp', 'User', 'Device', 'Project', 'Usage'])
		timestring = get_time_stamp(4)
		for entry in logger.list_entries(page_size = 1000, filter_ = 'timestamp > \" ' + timestring + '\"'):
			timestamp = entry.timestamp.isoformat()
			details = entry.payload.split(',')
			row = [timestamp] + details
			print("Detail:", row)
			writer.writerow(row)
	print("Done", output_file_csv)

def get_tm_usage_log(logger_name = 'tm-usage', record_day=7):
	try:
		client = logging.Client()
	except:
		pass
	log_name = logger_name
	logger = client.logger(log_name)
	now = datetime.now()
	timestamp = str(int(datetime.timestamp(now)))			
	output_file_csv = log_name + "_" + timestamp + '.csv'
	with open(output_file_csv, 'w', newline='', encoding='utf_8_sig') as csv_file:
		writer = csv.writer(csv_file, delimiter=',')
		writer.writerow(['Timestamp', 'User', 'Device', 'Project', 'Usage'])
		timestring = get_time_stamp(30)
		for entry in logger.list_entries(page_size = 1000, filter_ = 'timestamp > \" ' + timestring + '\"'):
			timestamp = entry.timestamp.isoformat()
			details = entry.payload.split(',')
			row = [timestamp] + details
			print("Detail:", row)
			writer.writerow(row)
	print("Done", output_file_csv)

def get_tm_info_log(logger_name = 'tm-info', record_day=7):
	try:
		client = logging.Client()
	except:
		pass
	log_name = logger_name
	logger = client.logger(log_name)
	now = datetime.now()
	timestamp = str(int(datetime.timestamp(now)))			
	output_file_csv = log_name + "_" + timestamp + '.csv'
	with open(output_file_csv, 'w', newline='', encoding='utf_8_sig') as csv_file:
		writer = csv.writer(csv_file, delimiter=',')
		writer.writerow(['Timestamp', 'User', 'Device', 'Project', 'TM size', 'Usage'])
		timestring = get_time_stamp(30)
		for entry in logger.list_entries(page_size = 1000, filter_ = 'timestamp > \" ' + timestring + '\"'):
			timestamp = entry.timestamp.isoformat()
			details = entry.payload.split(',')
			row = [timestamp] + details
			writer.writerow(row)
	print("Done", output_file_csv)

def get_error_log(logger_name = 'translator-error', record_day=7):
	try:
		client = logging.Client()
	except:
		pass
	log_name = logger_name
	logger = client.logger(log_name)
	now = datetime.now()
	timestamp = str(int(datetime.timestamp(now)))			
	output_file_csv = log_name + "_" + timestamp + '.csv'
	with open(output_file_csv, 'w', newline='', encoding='utf_8_sig') as csv_file:
		writer = csv.writer(csv_file, delimiter=',')
		writer.writerow(['Timestamp', 'User', 'Device', 'Project', 'Error message'])
		timestring = get_time_stamp(30)
		for entry in logger.list_entries(page_size = 1000, filter_ = 'timestamp > \" ' + timestring + '\"'):
			timestamp = entry.timestamp.isoformat()
			details = entry.payload.split(',')
			row = [timestamp] + details
			writer.writerow(row)
	print("Done", output_file_csv)	

def delete_logger(logger_name):
	"""Deletes a logger and all its entries.
	Note that a deletion can take several minutes to take effect.
	"""
	logging_client = logging.Client()
	logger = logging_client.logger(logger_name)

	logger.delete()

	print("Deleted all logging entries for {}".format(logger.name))

delete_logger('document-tool-usage')
delete_logger('writer-tool-usage')
delete_logger('tm-usage')
delete_logger('tm-info')
#get_translation_usage_log()
#get_tm_usage_log()
#get_db_update_log()
#get_tm_info_log()