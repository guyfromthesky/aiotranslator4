# Base64 convert
import json
#System lib
import os
import sys
from google.cloud import storage
import subprocess


class CloudConfigLoader:
	def __init__(self):
		# App online config
		self.bucket_id = 'nxvnbucket'
		self.db_list_uri = 'config/db_list.csv'
		self.project_bucket_id = 'credible-bay-281107'
		self.location = "us-central1"
		
		self.cloud_client = storage.Client()
		self.bucket = self.cloud_client.get_bucket(self.bucket_id)

		# Folder
		print('Load id from json')
		self.project_id = self.load_project_id_from_json()
		self.uuid = self.generate_device_unique_id()
		
		self.Config = {}

		# Add 2 details below:
		#self.Config['bucket_db_list']
		#self.Config['glossary_data_list']
		self.load_project_list_from_bucket()
		# Add 2 details below:
		#self.Config['latest_version']
		#self.Config['banned']
		self.load_project_info_from_bucket()
		print('Config:', self.Config)

	def load_project_id_from_json(self):
		print('load_project_id_from_json')
		try:
			License = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
			with open(License, 'r') as myfile:
				data=myfile.read()
			obj = json.loads(data)
			_project_id = obj['project_id']
		except:
			_project_id = 'credible-bay-281107'	
		
		return _project_id

	def load_project_list_from_bucket(self):
		print('load_project_list_from_bucket')
		blob = self.bucket.get_blob(self.db_list_uri)
		if blob != None:
			try:
				listdb = blob.download_as_text()
			except Exception as e:
				print('Fail to load blob:', e)
				return
		else:
			return
		mydb = listdb.split('\r\n')
		self.Config['bucket_db_list'] = []
		self.Config['glossary_data_list'] = []
		for pair in mydb:

			data = pair.split(',')
			Valid = True
			for element in data:
				if element == "" or element == None:
					Valid = False
			if Valid:
				id = str(data[0]).replace('\ufeff', '')
				URI = str(data[1])
				self.Config['bucket_db_list'].append(id)
				self.Config['glossary_data_list'].append([id, URI])
	
	
	def load_project_info_from_bucket(self):
		print('load_project_info_from_bucket')
		try:
			versioning = self.bucket.get_blob('config/latest_version')
			myversion = versioning.download_as_text()
			my_latest_version = myversion
			#my_latest_version = myversion.split('\r\n')[0]
		except:
			my_latest_version = ""	
		if my_latest_version != "":	
			self.Config['latest_version'] = my_latest_version
		else:
			self.Config['latest_version'] = None

		try:
			banning = self.bucket.get_blob('config/banning')
			banning_list = banning.download_as_text()
			_my_banning_list = banning_list.split('\r\n')
			
		except:
			_my_banning_list = []

		self.Config['banned'] = False
		if self.uuid in _my_banning_list:
			self.Config['banned'] = True
	
	def generate_device_unique_id(self):
		print('generate_device_unique_id')
		return str(subprocess.check_output('wmic csproduct get uuid'), 'utf-8').split('\n')[1].strip()
		