import requests
from bs4 import BeautifulSoup
import re


soup = BeautifulSoup(requests.get('https://www.sportytrader.es/cuotas/baloncesto/usa/nba-306/').content, 'html.parser')
divs = soup.find_all('div', class_='cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative')
team = 'Golden State Warriors'
divs_buscados = []
for div in divs:
    onclick = div.get('onclick')
    if re.search(team.lower().replace(' ','-'), onclick):
        print(onclick)
        divs_buscados.append(div)

for div in divs_buscados:
    m = div.find_all('a')[0].text.replace('\n','').split(' - ')
    pred = [div.find_all('span', class_='px-1 h-booklogosm font-bold bg-primary-yellow text-white leading-8 rounded-r-md w-14 md:w-18 flex justify-center items-center text-base')[i].text for i in range(2)]

    info = {float(pred[0]):m[0], float(pred[1]):m[1]}

    print(f'En el partido de {m[0]} contra {m[1]} ganan los {info[min(info)]}')
        
