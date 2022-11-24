import requests
from bs4 import BeautifulSoup
import re
import os

soup = BeautifulSoup(requests.get('https://espndeportes.espn.com/basquetbol/nba/equipo/estadisticas/_/nombre/dal/dallas-mavericks').content, 'html.parser')

tr = soup.find_all('tr', class_='Table__TR Table__TR--sm Table__even')
contador = 0
for i in tr:
    if contador < 18:
        print(i.find_all('span')[0].text=='Total')
        name = '_'.join(i.find_all('a')[0].text.split(' '))
        id = i.find_all('a')[0].get('data-player-uid').split(':')[-1]
        link = f'https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/{id}.png&w=350&h=254'
        img = requests.get(link)
        os.mkdir('images') if not os.path.exists('images') else None
        open(f'images/{name}.png', 'wb').write(img.content)     
        contador += 1



