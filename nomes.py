
from requests import get
from re import sub

class ApiNomes(object):
	"""docstring for ApiNomes"""
	def __init__(self, name):
		super(ApiNomes, self).__init__()
		self.name = name
		
	def frequency(self):
	
		data = get('https://servicodados.ibge.gov.br/api/v2/censos/nomes/' + self.name).json()

		if len(data) == 0:

			return ValueError('Dados indisponíveis para o nome "' + self.name + '"')
	
		data = data[0]['res']

		data = {
			'name': self.name,
			'intdate': [sub('\,', ' - ', sub('\[|\]', '', i['periodo'])) for i in data],
			'frequency': [i['frequencia'] for i in data]
		}

		return data

	def sex(self):

		data_male = get('https://servicodados.ibge.gov.br/api/v2/censos/nomes/' + self.name + '?sexo=M').json()

		if len(data_male) == 0:

			return ValueError('Dados indisponíveis para o nome "' + self.name + '"')

		data_male = data_male[0]['res']

		data_male = {
			'name': self.name,
			'intdate': [sub('\,', ' - ', sub('\[|\]', '', i['periodo'])) for i in data_male],
			'frequency': [i['frequencia'] for i in data_male]
		}

		data_female = get('https://servicodados.ibge.gov.br/api/v2/censos/nomes/' + self.name + '?sexo=F').json()
		
		data_female = data_female[0]['res']

		data_female = {
			'name': self.name,
			'intdate': [sub('\,', ' - ', sub('\[|\]', '', i['periodo'])) for i in data_female],
			'frequency': [i['frequencia'] for i in data_female]
		}

		if max(data_male['frequency']) > max(data_female['frequency']):

			return 'Masculino'

		else:

			return 'Feminino'

	def groupUF(self):

		data = get('https://servicodados.ibge.gov.br/api/v2/censos/nomes/' + self.name + '?groupBy=UF').json()

		if len(data) == 0:

			return ValueError('Dados indisponíveis para o nome "' + self.name + '"')

		data = {
			'local': [i['localidade'] for i in data],
			'pop': [i['res'][0]['populacao'] for i in data],
			'freq': [i['res'][0]['frequencia'] for i in data],
			'prop': [round(i['res'][0]['proporcao']/100000, 8) for i in data],
		}

		return data

	def local(self, code):

		data = get('https://servicodados.ibge.gov.br/api/v2/censos/nomes/' + self.name + '?localidade=' + code).json()

		if len(data) == 0:

			return ValueError('Dados indisponíveis para o nome "' + self.name + '"')

		data = data[0]['res']

		data = {
			'name': self.name,
			'intdate': [sub('\,', ' - ', sub('\[|\]', '', i['periodo'])) for i in data],
			'frequency': [i['frequencia'] for i in data]
		}

		return data

if __name__ == '__main__':

	ibge = ApiNomes(name = 'Socorro')
	
	print('Frequencia\n', ibge.frequency(), '\n')
	
	print('Gênero', ibge.sex(), '\n')

	print('Por Estado\n', ibge.groupUF(), '\n')
	
	print('Localidade Maranhão\n', ibge.local(code = '21'))
