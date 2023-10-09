
import streamlit as st
from credentials import TOKEN_FINEP, API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from pytweet import Twitter, Finep
from pln import GetSentimentText
from streamlit_echarts import st_echarts
from datetime import datetime
from datetime import date
from re import sub
from json import loads
from pandas import DataFrame

icon = 'https://w7.pngwing.com/pngs/872/50/png-transparent-computer-icons-social-media-logo-twitter-social-media-blue-logo-social-media-thumbnail.png'

st.set_page_config(
	layout='wide', 
	page_title='Monitoramento Político',
	page_icon=icon,
	initial_sidebar_state='collapsed'
)
st.set_option('deprecation.showPyplotGlobalUse', False)

twitter = Twitter(
	api_key=API_KEY, 
	api_key_secret=API_KEY_SECRET, 
	access_token=ACCESS_TOKEN, 
	access_token_secret=ACCESS_TOKEN_SECRET
)

finep = Finep(
	token_finep=TOKEN_FINEP
)

st.write(
"""
## Monitoramento de Engajamento no Twitter
"""
)

c1, c2, c3, c4 = st.columns(4)

with c1:
	nome = st.text_input(label='Username:', value='LulaOficial')
with c2:
	dias = st.number_input(label='Número de Dias atrás:', value=30)
with c3:	
	variavel = st.selectbox(
		label='Tipo da Variável:', 
		options=list(['followers', 'engagements']),
		index=0
	)
with c4:
	if variavel == 'engagements':
		info_type = st.radio(
			label='RTs or Favs', 
			options=list(['Retweets', 'Favorites'])
		)
	else:
		info_type = 'Other'

@st.cache(persist=True)
def follow_data():
	follow_data = finep.finep_followers_data(
		since=dias,
		profile_id=twitter.__get_id__(name_screen=nome),
	)
	return follow_data

@st.cache(persist=True)
def engage_data():
	engage_data = finep.finep_engage_data(
		since=dias,
		profile_id=twitter.__get_id__(name_screen=nome),
		n_tweets=500
	)
	return engage_data

if variavel == 'followers':
	data = follow_data()
	data = loads(data)
else:
	data = engage_data()
	data = loads(data)

if info_type == 'Retweets':
	value = 'retweet_count'
elif info_type == 'Favorites':
	value = 'favorite_count'
else:
	value = 'followers_count'

x = [date.strftime(
		datetime.strptime(i['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z'), 
		'%Y-%m-%d\n%H:%m') for i in data]

y = [i[value] for i in data]

options = {
	"xAxis": {
	"type": "category",
	"name": "Data",
	"data": x 
	},
	"tooltip": {
        "trigger": "axis"
    },
	"yAxis": {
		"type": "value",
		"name": "Quantidade",
		"min": int(min(y)*0.999),
        "max": int(max(y)*1.001)
	},
	"series": [
		{"data": y, "type": "line"}
	]
}

st_echarts(options=options)

st.write(
"""
## Análise de Sentimentos no Twitter
"""
)

text = st.text_area(
	label='Tema (assunto):', 
	value="""Eleições Lula"""
)

tweet = twitter.trending_topics(
	query=text, 
	n_tweets=30
)

text = ' '.join(tweet['full_text'])
text = sub('\#|\%', '', text)

@st.cache(allow_output_mutation=True)
def data_nlp():
	nlp = GetSentimentText(text=text)
	return nlp

st.write(
	DataFrame(
		data_nlp().sentiment_analysis()
	)
)

st.pyplot(
	data_nlp().plot_cloud()
)

st.write(
"""
## Monitoramento dos Trending Topics em São Luís/MA
"""
)

@st.cache()
def trends_data():
	trends_data = twitter.trending_topics_regional(
		woeid=twitter.__get_woeid__(
			location='São Luís'
			)
		)
	return trends_data

st.write(
	DataFrame(
		trends_data()
	)
)