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
import pandas as pd



headers = {
		"Referer": "http://artchallenge.me/",
		"Accept": "application/json,text/*;q=0.99",
		"Sec-Fetch-Mode": "no-cors",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
		}

def clean_data():

	artists = pd.read_csv('artists.csv')['name'].to_list()
	return artists
	

class Artists_scrape:

	def __init__(self, artists, headers):

		#self.painter_num = painter_num
		self.artists = artists
		self.headers = headers


	def getJSON(self, id):


		self.url = "http://artchallenge.me/painters/{}/data.json".format(id) 
		print(self.url)

		
		r = requests.get(self.url, headers = self.headers)
		resp = json.loads(r.text)
		#print(resp.get('name'))
		if resp.get('name') not in self.artists:
			print('True')
			print(resp.get('genre'))
			return [resp.get("id"), resp.get('name'), resp.get('year'), resp.get('genre'), resp.get('nationality'),resp.get("paintings")]

		else: 
			print('Already in!')
			pass

artists_all = clean_data()
artist_store = []
a1 = Artists_scrape(artists_all,headers)
for i in range(1,119):
	art = a1.getJSON(i)
	if art:
		artist_store.append(art)

df = pd.DataFrame(artist_store, columns=['id', 'name', 'year', 'genre', 'nationality', 'paintings'])
df.to_csv("/home/chenlin/desktop/artists_complemented.csv")
