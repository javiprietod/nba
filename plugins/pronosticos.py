import requests
from bs4 import BeautifulSoup
import re
import sys, os

def extract():
    text = requests.get('https://www.sportytrader.es/cuotas/baloncesto/usa/nba-306/').text
    os.mkdir('data/pronosticos_etl') if not os.path.exists('data/pronosticos_etl') else None
    open('data/pronosticos_etl/extracted.txt','w').write(text)


def transform():
    team = eval(open('data/config.txt','r').read())['team']
    text = open('data/pronosticos_etl/extracted.txt','r').read()
    soup = BeautifulSoup(text, 'html.parser')
    divs = soup.find_all('div', class_='cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative')
    divs_buscados = []
    for div in divs:
        onclick = div.get('onclick')
        if re.search(team.lower().replace(' ','-'), onclick):
            divs_buscados.append(div)
    info = {}
    opponents = []
    for div in divs_buscados:
        m = div.find_all('a')[0].text.replace('\n','').split(' - ')
        pred = [div.find_all('span', class_='px-1 h-booklogosm font-bold bg-primary-yellow text-white leading-8 rounded-r-md w-14 md:w-18 flex justify-center items-center text-base')[i].text for i in range(2)]

        info = {float(pred[0]):m[0], float(pred[1]):m[1]}
        if info != {}:
            cuota_ganadora = min(info.keys())
            team = 'En el partido entre ' + m[0] + ' y ' + m[1] + ' se pronostica que ' + info[cuota_ganadora] + ' gana con una cuota de ' + str(cuota_ganadora) + ' frente a ' + str(max(info.keys())) + ' de su rival'
            opponents.append(team)
    open('data/pronosticos_etl/transformed.txt','w').write(str(opponents))

def load():
    opponents = eval(open('data/pronosticos_etl/transformed.txt','r').read())
    file = open('data/pronosticos.txt','w')
    if opponents == []:
        file.write('No se encontraron predicciones del equipo')
    else:
        for i in opponents:
            file.write(i + '\n')
    file.close()
