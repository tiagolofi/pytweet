
from tweepy import API, OAuthHandler, Cursor
from tweepy.parsers import JSONParser
from tweepy.errors import TweepyException
from json import dump
from requests import get, post
from time import time, sleep
from datetime import datetime

class Twitter(object):

	def __init__(self, api_key: str, api_key_secret: str, access_token: str, access_token_secret: str):
		
		self.__api_key = api_key
		self.__api_key_secret = api_key_secret
		self.__access_token = access_token
		self.__access_token_secret = access_token_secret
		
		self.__auth = OAuthHandler(
			self.__api_key, 
			self.__api_key_secret
		)

		self.__auth.set_access_token(
			self.__access_token, 
			self.__access_token_secret
		) 

		self.__api = API(
			self.__auth, 
			wait_on_rate_limit=True, 
			parser=JSONParser()
		) 

	def __get_woeid__(self):

		list_of_woeids = self.__api.available_trends()

		list_of_woeids_comp = []

		for i in list_of_woeids:

			list_of_woeids_comp.append({k: v for k, v in i.items() if k in ['name', 'woeid']})
		
		return list_of_woeids_comp

	def tweets(self, query: str, n_tweets: int, filter_retweets: bool, save_json: bool):
		
		# https://developer.twitter.com/en/docs/twitter-api/v1/rules-and-filtering/search-operators
		# query OR

		if filter_retweets:

			q = query + ' -filter:retweets'
		
		else: 
			
			q = query

		if n_tweets < 100:

			tweet_page = 1

		else:

			tweet_page = n_tweets/100

		pages = [i for i in Cursor(self.__api.search_tweets, q=q, count=100, lang='pt', tweet_mode='extended').pages(tweet_page)]

		if save_json:
			with open(f"""{query + str(int(datetime.now().timestamp()))}.json""", 'w', encoding='utf-8') as outfile:
				dump(pages, outfile, ensure_ascii=False, indent=4)

		return pages

	def retweets(self, query: str, n_tweets: int, save_json: bool):
		
		# https://developer.twitter.com/en/docs/twitter-api/v1/rules-and-filtering/search-operators
		# query OR

		if n_tweets < 100:

			tweet_page = 1

		else:

			tweet_page = n_tweets/100

		while True:

			try:

				pages = [i for i in Cursor(self.__api.search_tweets, q=query + ' filter:retweets', count = 100, lang='pt', tweet_mode='extended').pages(tweet_page)]

			except TweepyException:

				print('dormindo...')

				sleep(60 * 15)

				continue

			except StopIteration:

				break

		if save_json:
			with open(f"""{query + str(int(datetime.now().timestamp()))}.json""", 'w', encoding='utf-8') as outfile:
				dump(pages, outfile, ensure_ascii=False, indent=4)

		return pages

class FinepInstagram(object):

	def __init__(self, username: str, password: str):
		self.username = username
		self.password = password
		
	def get_token(self):

		base_url_auth = 'http://191.252.178.150:8000/login'

		headers = {
			'content-type': 'application/x-www-form-urlencoded'
		}

		response = post(
			url = base_url_auth,
			headers = headers,
			json = f'grant_type=&username={self.username}&password={self.password}&scope=&client_id=&client_secret='
		)

		token = response.json()

		return token['access_token']

	def get_profiles(self):

		base_url = 'http://191.252.178.150:8001/profiles'

		headers = {
			'content-type': 'application/json', 
			'authorization': 'Bearer ' + self.get_token()
		}
		
		response = get(
			url = base_url,
			headers = headers,
		)

		data = response.json()

		with open('file.json', 'w', encoding='utf-8') as outfile:
			dump(data, outfile, ensure_ascii=False, indent=4)

		return data

	def get_endpoint(self, username, endpoint):
		
		base_url = f'http://191.252.178.150:8001/profiles/{username}/{endpoint}'

		headers = {
			'content-type': 'application/json', 
			'authorization': 'Bearer ' + self.get_token()
		}
		
		response = get(
			url = base_url,
			headers = headers,
		)

		print(response.status_code)

		data = response.json()

		return data

class FinepTwitter(object):

	def __init__(self, email: str, password: str):

		self.__base_url = 'http://191.252.178.150:3001/api/v2'
		self.email = email
		self.password = password
	
	def get_token(self):

		credentials = {
			'email': self.email,
			'password': self.password
		}
	
		headers = {
			'content-type': 'application/json'
		}
			
		route = '/auth/login'
		
		response = post(
			url = self.__base_url + route, 
			json = credentials, 
			headers = headers
		)
		
		token = response.json()['token']
		
		return token

	def convert_date(self, date: str):

		return str(int(datetime.strptime(date, '%Y-%m-%d').timestamp() * 1000))

	def get_profiles(self):

		route = '/twitter/profiles'
		
		headers = {
			'content-type': 'application/json', 
			'authorization': 'Bearer ' + self.get_token()
		}
				
		response = get(
			url = self.__base_url + route,
			headers = headers
		)
				
		data = response.json()

		with open('file2.json', 'w', encoding='utf-8') as outfile:
			dump(data, outfile, ensure_ascii=False, indent=4)

		return data

	def __get_id__(self, name_screen: str):

		route = f"""/twitter/search/user?name="""
		
		headers = {
			'content-type': 'application/json', 
			'authorization': 'Bearer ' + self.get_token()
		}
				
		response = get(
			url = self.__base_url + route + name_screen,
			headers = headers
		)
				
		data = response.json()

		print(data[0]['screen_name'])

		id_str = str(data[0]['id_str'])

		return id_str

	def finep_followers_data(self, since: str, profile_id: str):
		
		route = f"""/twitter/followers/{profile_id}?g=h&since={self.convert_date(since)}"""
		
		headers = {
			'content-type': 'application/json', 
			'authorization': 'Bearer ' + self.get_token()
		}
				
		response = get(
			url = self.__base_url + route,
			headers = headers
		)
				
		return response.json()

	def finep_engagement_data(self, since: str, until: str, profile_id: str):

		# tmstmp = int(time()*1000) - int(1000 * 60 * 60 * 24 * since)
		
		route = f"""/twitter/engagements/{profile_id}?since={self.convert_date(since)}&until={self.convert_date(until)}"""
		
		headers = {
			'content-type': 'application/json', 
			'authorization': 'Bearer ' + self.get_token()
		}
		
		response = get(
			url = self.__base_url + route,
			headers	= headers
		)

		return response.json()

	def finep_mentions_data(self, since: str, until: str, profile_id: str):
		
		route = f"""/twitter/mentions/{profile_id}?since={self.convert_date(since)}&until={self.convert_date(until)}"""

		headers = {
			'content-type': 'application/json', 
			'authorization': 'Bearer ' + self.get_token()
		}

		response = get(
			url = self.__base_url + route,
			headers = headers
		)

		return response.json()

if __name__ == '__main__':

	from credentials import USERNAME, PWD_INSTAGRAM, EMAIL, PWD_TWITTER, API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

	x = Twitter(api_key = API_KEY, api_key_secret = API_KEY_SECRET, access_token = ACCESS_TOKEN, access_token_secret = ACCESS_TOKEN_SECRET)

	z = x.tweets(
		query='Flavio Dino OR @FlavioDino',
		n_tweets=200,
		filter_retweets=True,
		save_json=True
	)

	print(z)

	# x = FinepInstagram(username = USERNAME, password = PWD_INSTAGRAM)

	# print(x.get_token())
 
	# print(x.get_endpoint(username = 'duartejr_', endpoint = 'posts'))
