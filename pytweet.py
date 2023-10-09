
from tweepy import API, OAuthHandler
from tweepy.parsers import JSONParser
from credentials import api_key, api_key_secret, access_token, access_token_secret
from datetime import datetime

class Twitter:

	def __init__(self):

		## secrets
		
		self.__api_key = api_key
		self.__api_key_secret = api_key_secret
		self.__access_token = access_token
		self.__access_token_secret = access_token_secret

		## config 

		self.__variables_user = ['id', 'name', 'screen_name', 'location', 'description', 'followers_count', 'friends_count', 'created_at', 'statuses_count', 'verified', 'profile_image_url_https']
		self.__variables_timeline = ['id', 'created_at', 'retweet_count', 'favorite_count']

		## tweepy config
		
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
		
	def user(self, username: str):
		
		req = self.__api.get_user(screen_name = username)
		
		data = {k: v for k, v in req.items() if k in self.__variables_user}

		## parse date
			
		data['created_at'] = int(datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp())

		data['age'] = int(datetime.now().timestamp()) - data['created_at']
		
		return data

	def timeline(self, username: str):

		req = self.__api.user_timeline(screen_name = username, count = 50)

		data = [{k: v for k, v in i.items() if k in self.__variables_timeline} for i in req]

		## parse date
		
		for i in range(len(data)):
		
			data[i]['created_at'] = int(datetime.strptime(data[i]['created_at'], '%a %b %d %H:%M:%S %z %Y').timestamp())

		## filter last 24h
		
		data = [{k: v for k, v in i.items() if i['created_at'] < int(datetime.now().timestamp()) - 43200} for i in data]

		data = [i for i in data if len(i) > 0]
		
		return data
	