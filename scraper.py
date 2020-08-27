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
sender = os.environ.get('GMAIL_USER')
recipient = os.environ.get('GMAIL_DEST')

# Scrape home page contents
def scrape_home():
    page = requests.get('https://www.hermannwesselinkcollege.nl/')
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find('h1', class_='title')
    children = soup.find('div', class_='field-item even').findChildren(recursive=False)
    return title, children

# Parse home page contents
def parse_home(_title, _paragraphs):
    body = '<html><body>'
    body += str(_title)
    for paragraph in _paragraphs:
        if paragraph.text != "" and paragraph.text != " ":
            body += '<p>{}<p>'.format(paragraph)
    body += '</body></html>'
    return body

# Email home page contents
def email_home(html):
    htmlMessage = MIMEMultipart()
    htmlMessage['From'] = 'HWC Actueel <{}>'.format(sender)
    htmlMessage['To'] = recipient
    htmlMessage['Subject'] = 'Nieuw bericht op de HWC voorpagina'
    htmlMessage.attach(MIMEText(html, 'html'))

    print('Sending email with message:\n' + str(htmlMessage))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, htmlMessage.as_string())
        server.quit()

# Check home page cache
def check_home_cache(body):
    if os.path.exists('home_cache.txt'):
        with open('home_cache.txt') as f:
            if body in f.read():
                print('Home is in cache.')
                return True
            else:
                print('Home is not in cache.')
                return False
    else:
        print("Could not check home cache: file does not exist.")

# Rewrite home cache file
def rewrite_home_cache(body):
    if os.path.exists('home_cache.txt'):
        os.remove('home_cache.txt')
    else:
        print('Home cache not found, creating new.')

    with open('home_cache.txt', 'a') as f:
        f.write(body)
        f.close()
    
    print('Wrote home page to cache.')

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
    if(os.path.exists('article_cache.txt')):
        with open('article_cache.txt') as f:
            if article.id in f.read():
                print('Is in cache.')
                return True
            else:
                print('Is not in cache.')
                return False
    else:
        print('Could not check article cache: file does not exist.')
        return False

# Rewrite cache file
def rewrite_cache(new_articles):
    if os.path.exists('article_cache.txt'):
        os.remove('article_cache.txt')

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
        htmlMessage['Subject'] = 'Nieuwe berichten op HWC actueel'
    else:
        htmlMessage['Subject'] = 'Nieuw bericht op HWC actueel'

    htmlMessage.attach(MIMEText(html, 'html'))

    print('Sending email with message:\n' + str(htmlMessage))

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
        try:
            send_email(new_articles)
        except smtplib.SMTPResponseException:
            print("Failed to send actueel email!")
    else:
        print('No new article was found.')

    home_title, home_content = scrape_home()
    home_body = parse_home(home_title, home_content)
    if check_home_cache(home_body):
        print('No new home page content was found.')
    else:
        print('New home page content was found, rewriting cache...')
        rewrite_home_cache(home_body)
        try:
            email_home(home_body)
        except smtplib.SMTPResponseException:
            print("Failed to send home email!")

if __name__ == "__main__":
    main()
