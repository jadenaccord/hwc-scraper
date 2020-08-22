class Article:
    def __init__(self, date_txt, title_txt, author_txt, body_txt, link_href):
        self.date = date_txt
        self.title = title_txt
        self.author = author_txt
        self.body = body_txt
        self.link = link_href
        
        self.id = self.date + ': ' + self.title
