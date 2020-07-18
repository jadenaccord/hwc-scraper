import requests
from bs4 import BeautifulSoup
import os

URL = 'https://www.hethwc.nl/actueel'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

new_article_found = False

articles = soup.findAll('div', class_='views-row')

def rewrite_cache():
    if os.path.exists('article_cache.txt'):
        os.remove('article_cache.txt')
    else:
        print('Cache not found, creating new.')

    for article in articles:
        date_txt = article.find('div', class_='views-field-created-1').find('div', class_='post-day').text + ' ' + article.find('div', class_='views-field-created-1').find('div', class_='post-month').text
        title_txt = article.find('div', class_='views-field-title').find('a').text

        article_id = date_txt + ': ' + title_txt
        cache = open('article_cache.txt', 'a')
        cache.write(article_id + '\n')
        cache.close()
        print('Wrote article to cache with id: ' + article_id)

for article in articles:
    date_div = article.find('div', class_='views-field-created-1')
    date_txt = date_div.find('div', class_='post-day').text + ' ' + date_div.find('div', class_='post-month').text

    title_div = article.find('div', class_='views-field-title')
    title_txt = title_div.find('a').text

    author_div = article.find('div', class_='views-field-name')
    author_txt = author_div.find('span', class_='field-content').text

    body_div = article.find('div', class_='views-field-body')
    body_txt = body_div.find('p').text

    link_div = article.find('div', class_='views-field-view-node')
    link_txt = link_div.find('a').text
    link_href = link_div.find('a')['href']

    article_id = date_txt + ': ' + title_txt
    print('Article id: ' + article_id)

    with open('article_cache.txt') as f:
        if article_id in f.read():
            print('Is in cache')
        else:
            print('Is not in cache.')
            new_article_found = True

    print('\n')

if new_article_found == True:
    print('A new article was found, rewriting cache...')
    rewrite_cache()
else:
    print('No new article was found.')
    