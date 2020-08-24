import requests
from bs4 import BeautifulSoup
import os

page = requests.get('https://www.hermannwesselinkcollege.nl/')
soup = BeautifulSoup(page.content, 'html.parser')
container = soup.find('div', class_='field-item even')
children = container.findChildren(recursive=False)

for child in children:
    if child.text != "":
        print(child.text)
        file = open('test.txt', 'a')
        file.write(child.text + '\n')
        file.close()