import requests
from bs4 import BeautifulSoup
import os
import email, smtplib, ssl
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

from Article import Article

# E-mail variables
port = 465
password = os.environ.get('GMAIL_PASS')
sender = 'jadenbrdev@gmail.com'
recipient = '34092@lln.hethwc.nl'

# Scrape home page contents
def scrape_home():
    page = requests.get('https://www.hermannwesselinkcollege.nl/')
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.findAll('div', class_='fields-item')

# Scrape actueel page contents
def scrape_actueel():
    page = requests.get('https://www.hermannwesselinkcollege.nl/actueel')
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.findAll('div', class_='views-row') # Return articles as raw html

# Parse article
def parse_article(article):
    # Get article date
    date_div = article.find('div', class_='views-field-created-1')
    date_txt = date_div.find('div', class_='post-day').text + ' ' + date_div.find('div', class_='post-month').text

    # Get title
    title_div = article.find('div', class_='views-field-title')
    title_txt = title_div.find('a').text

    # Get author
    author_div = article.find('div', class_='views-field-name')
    author_txt = author_div.find('span', class_='field-content').text

    # Get body
    body_div = article.find('div', class_='views-field-body')
    body_txt = body_div.find('p').text

    # Get link
    link_div = article.find('div', class_='views-field-view-node')
    link_txt = link_div.find('a').text
    link_href = link_div.find('a')['href']

    # Return Article object
    return Article(date_txt, title_txt, author_txt, body_txt, link_href)

# Check if article exists in cache
def check_article_cache(article):
    with open('article_cache.txt') as f:
        if article.id in f.read():
            print('Is in cache')
            return True
        else:
            print('Is not in cache.')
            return False

# Rewrite cache file
def rewrite_cache(new_articles):
    if os.path.exists('article_cache.txt'):
        os.remove('article_cache.txt')
    else:
        print('Cache not found, creating new.')

    for article in new_articles:
        cache = open('article_cache.txt', 'a')
        cache.write(article.id + '\n')
        cache.close()
        print('Wrote article to cache with id: ' + article.id)

# Send email with new article(s)
def send_email(articles):
    # HTML body
    html = '<html><body>'
    for article in articles:
        html += '<h2>{}</h2><i>{} ({})</i><br><p>{}</p><br><a href="{}">Lees het hele artikel</a><br><hr>'.format(article.title, article.author, article.date, article.body, 'https://www.hethwc.nl' + article.link)
    html += '</body></html>'

    # HTML message
    htmlMessage = MIMEMultipart()
    htmlMessage['From'] = 'HWC Actueel <{}>'.format(sender)
    htmlMessage['To'] = recipient
    if len(articles) > 1:
        htmlMessage['Subject'] = 'Nieuwe berichten op HWC website'
    else:
        htmlMessage['Subject'] = 'Nieuw bericht op HWC website'

    htmlMessage.attach(MIMEText(html, 'html'))

    print('Sending email with message:\n' + htmlMessage)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, htmlMessage.as_string())
        server.quit()

# Main function
def main():
    new_articles = []
    raw_articles = scrape_actueel()
    for article in raw_articles:
        article_obj = parse_article(article)
        if check_article_cache(article_obj) == False:
            new_articles.append(article_obj)

    if len(new_articles) > 0:
        print('New articles were found, rewriting cache...')
        rewrite_cache(new_articles)
        send_email(new_articles)
    else:
        print('No new article was found.')

if __name__ == "__main__":
    main()