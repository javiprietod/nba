import requests
from bs4 import BeautifulSoup
import re


soup = BeautifulSoup(requests.get('https://www.sportytrader.es/cuotas/baloncesto/usa/nba-306/').content, 'html.parser')
divs = soup.find_all('div', class_='cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative')
team = 'Golden State Warriors'

for div in divs:
    onclick = div.get('onclick')
    if re.search(team.lower().replace(' ','-'), onclick):
        print(onclick)
        div_buscado = div
        break

m = div_buscado.find_all('a')[0].text.replace('\n','').split(' - ')
pred = [div_buscado.find_all('span', class_='px-1 h-booklogosm font-bold bg-primary-yellow text-white leading-8 rounded-r-md w-14 md:w-18 flex justify-center items-center text-base')[i].text for i in range(2)]

info = {float(pred[0]):m[0], float(pred[1]):m[1]}

print('Gana', info[min(info)])
        
