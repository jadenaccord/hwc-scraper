import requests
from bs4 import BeautifulSoup
import os

def formatHomePage(_title, _paragraphs):
    body = '<html><body>'
    body += str(_title)
    for paragraph in _paragraphs:
        if paragraph.text != "" and paragraph.text != " ":
            body += '<p>{}<p>'.format(paragraph)
    body += '</body></html>'

    print(body)

def main():
    page = requests.get('https://www.hermannwesselinkcollege.nl/')
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find('h1', class_='title')
    container = soup.find('div', class_='field-item even')
    children = container.findChildren(recursive=False)
    formatHomePage(title, children)

if __name__ == '__main__':
    main()