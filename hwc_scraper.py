import requests
from bs4 import BeautifulSoup
import os
import email, smtplib, ssl
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

# Web variables
URL = 'https://www.hethwc.nl/actueel'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

# Article variables
new_article_found = False
new_articles = []
new_articles_data = []

# E-mail variables
port = 465
password = os.environ.get('GMAIL_PASS')
sender = 'jadenbrdev@gmail.com'
recipient = '34092@lln.hethwc.nl'

# Scrape all articles into array
articles = soup.findAll('div', class_='views-row')

# Rewrite cache file
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

# Send email with new article(s)
def send_email():
    # Plain text body
    body = ''
    for article in new_articles_data:
        body += 'Titel: {}\nAuteur: {}\nDatum: {}\nPreview: {}\nLees het hele artikel: {}\n\n'.format(article[1], article[2], article[0], article[3], 'https://www.hethwc.nl' + article[4])

    # Plain text message
    message = 'Subject: {}\nFrom: {}\nTo: {}\n\n{}'.format('Nieuw bericht op HWC website', 'HWC Actueel <jadenbr.dev@gmail.com>', 'Jaden Accord <34092@lln.hethwc.nl>', body)

    # HTML body
    html = '<html><body>'
    for article in new_articles_data:
        html += '<h2>{}</h2><i>{} ({})</i><br><p>{}</p><br><a href="{}">Lees het hele artikel</a><br><hr>'.format(article[1], article[2], article[0], article[3], 'https://www.hethwc.nl' + article[4])
    html += '</body></html>'

    # HTML message
    htmlMessage = MIMEMultipart()
    htmlMessage['From'] = 'HWC Actueel <{}>'.format(sender)
    htmlMessage['To'] = recipient
    if len(new_articles) > 1:
        htmlMessage['Subject'] = 'Nieuwe berichten op HWC website'
    else:
        htmlMessage['Subject'] = 'Nieuw bericht op HWC website'

    # Attach both plain text body and html body to html message
    # htmlMessage.attach(MIMEText(body, 'plain'))
    htmlMessage.attach(MIMEText(html, 'html'))

    #print('Sending email with message:\n' + htmlMessage)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, htmlMessage.as_string())
        server.quit()

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

    article_data = [date_txt, title_txt, author_txt, body_txt, link_href]

    with open('article_cache.txt') as f:
        if article_id in f.read():
            print('Is in cache')
        else:
            print('Is not in cache.')
            new_article_found = True
            new_articles.append(article)
            new_articles_data.append(article_data)

    print('\n')

if new_article_found == True:
    print('A new article was found, rewriting cache...')
    rewrite_cache()
    send_email()

else:
    print('No new article was found.')
    
