# !/usr/bin/env python
# -*- coding: utf-8 -*-   


import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import os
import json
import time
import concurrent.futures
import shutil

import smtplib
import zipfile
from email.mime.multipart import MIMEMultipart 
from email.mime.base import MIMEBase 
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate 
from email import encoders
from email.message import EmailMessage



headers = {
		"Referer": "http://artchallenge.me/",
		"Accept": "application/json,text/*;q=0.99",
		"Sec-Fetch-Mode": "no-cors",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
		}

def clean_data():
	"""
	Get already existing artists
	"""

	artists = pd.read_csv('artists.csv')['name'].to_list()
	return artists
	

class Artchanllege_scrape:

	def __init__(self, artists, painter_id, headers):

		self.artists = artists
		self.id = painter_id
		self.headers = headers


	def getJSON(self):
		"""
		Get the artist name, id and number of paintings
		"""

		self.url = "http://artchallenge.me/painters/{}/data.json".format(str(self.id))
		print(self.url)

		try:
			r = requests.get(self.url, headers = self.headers)
			resp = json.loads(r.text)
			return (resp.get("name"), resp.get("id"),resp.get("paintings"))
		except:
			return None

	def parsePainters(self, artists_painting):
		"""
		Parse the painter to see whether it is already in.
		"""

		artist = artists_painting[0]
		artist_id = artists_painting[1]
		paintings = artists_painting[2]
		
		if artists_painting[0] in self.artists:
			print("Artists {} has already the pictures downloaded!".format(artist))
			return None
		else:
			#left_artist = [artist, artist_id, paintings]
			print("New Artist {} get in!".format(artist))
			return artist, artist_id, paintings

	def getPictures(self, artist_name, artist_id, painting_num):
		"""
		Get painter's pictures

		"""
		artist = '_'.join(artist_name.split(' '))

		try:
			path = os.getcwd() + '/images/images' # create folders
			directory = path + '/' + artist
			if not os.path.exists(directory):
				os.makedirs(directory)
		except:
			print("Errors in creating folders")
			return None

		self.painting_url = "http://artchallenge.me/painters/" + str(artist_id) + "/" + str(painting_num)+ ".jpg"
		print(self.painting_url)
		r = requests.get(self.painting_url)
		if r.status_code == 200:
			print("requests succeed!")
			try:
				new_path = directory + '/' + artist + '_'+str(painting_num)+'.jpg'
				with open(new_path, 'wb') as f:
					f.write(r.content)
					print("File write!")
			except:
				print("File doesn't write")
		else:
			print("The connection fails, status_code is ", r.status_code)
		return None

	def main(self):
		artist_id_paintings = self.getJSON()
		if self.parsePainters(artist_id_paintings) == None:
			pass
		else:
			artist_name, artist_id, painting_num  = self.parsePainters(artist_id_paintings)
			with concurrent.futures.ThreadPoolExecutor() as executor:
			 	executor.map(lambda x: self.getPictures(artist_name=artist_name, artist_id=artist_id, painting_num=x), range(1,painting_num+1))
			print("Finished {} pictures download".format(artist_name))
			return artist_name


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def email_send(zf):
	EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
	EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

	zf = open(zf, 'rb')
	msg = MIMEMultipart()
	msg['From'] = EMAIL_ADDRESS 
	msg['TO'] = EMAIL_ADDRESS
	msg['Date'] = formatdate(localtime = True)
	msg['Subject'] = 'zipfile_sent'
	part = MIMEBase('application', "zip")
	part.set_payload(zf.read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', 'attachment; filename="Scraped_Pictures.zip"')
	msg.attach(part)

	with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
		smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
		smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
	print('successfully sent the mail')

if __name__ == '__main__':
	# version 2 running
	begin = time.time()
	collected_artists = []
	artists = clean_data()
	for i in range(1, 119):
		a1 = Artchanllege_scrape(artists=artists, painter_id=i, headers=headers)
		name = a1.main()
		collected_artists.append(name)
		time.sleep(1)
	end = time.time()
	print('time', end - begin)

	path = os.getcwd() + '/image' 
	zipf = zipfile.ZipFile('Scraped_Pictures.zip', 'w', zipfile.ZIP_DEFLATED)
	zipdir(path, zipf)
	zipf.close()
	zf = os.getcwd() + '/Scraped_Pictures.zip'
	print(zf)
	email_send(zf)











