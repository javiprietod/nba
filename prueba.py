import requests

img = requests.get('https://upload.wikimedia.org//wikipedia//en//0//02//Washington_Wizards_logo.svg') 
open('prueba.svg', 'wb').write(img.content)  
# -*- coding: utf-8 -*-
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

drawing = svg2rlg('prueba.svg')
renderPM.drawToFile(drawing, 'prueba.png', fmt='PNG')  