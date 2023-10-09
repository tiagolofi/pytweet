
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk import FreqDist
from leia import SentimentIntensityAnalyzer
from pandas import read_csv, read_excel, DataFrame

class GetSentimentText(object):
	
	def __init__(self):

		self.__regexp = RegexpTokenizer('\s+', gaps=True) 

	def wordcloud(self, path: str, column: str, n_words: int):

		__stpwds = list(set(stopwords.words('portuguese')))

		if path[:-4] == '.csv':
			data = read_csv(path)
		elif path[:-5] == '.xlsx' or path[:-4] == '.xls':
			data = read_excel(path)

		list_text = ' '.join(data[column])

		list_text_tokenized = __regexp.tokenize(list_text)
		list_text_tokenized = [i for i in list_text_tokenized if i not in __stpwds]

		data_frame_freq = DataFrame(
			FreqDist(list_text_tokenized).most_common(n_words), 
			columns=['words', 'frequency']
		)

		data_frame_freq = data_frame_freq[[len(i) > 4 for i in data_frame_freq['words']]]
		data_frame_freq['words'] = [i.lower() for i in data_frame_freq['words']]
		data_frame_freq = data_frame_freq.groupby(['words']).agg({'frequency': 'sum'}).reset_index()

		return data_frame_freq

	def sentiment_analysis2(self, text: str):

		text_list = sent_tokenize(text)
		
		s = SentimentIntensityAnalyzer()
		
		classification = [s.polarity_scores(i)['compound'] for i in text_list]
		
		value = sum(classification)
		
		return value