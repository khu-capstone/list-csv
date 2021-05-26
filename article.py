from newspaper import Article as Art
from w3lib.html import replace_entities

# get article from url with newspaper3k
# html: article with html format
# text: only text
class Article():
    def __init__(self, url):
        self.url = url
        self.article = Art(self.url, keep_article_html=True)
        self.html = None
        self.text = None
        self.process()
    
    def process(self):
        self.article.build()
        self.replace()
    
    def replace(self):
        self.html = replace_entities(self.article.article_html)
        self.html = self.html.replace(u'\xa0', u' ')
        
        self.text = replace_entities(self.article.text)
        self.text = self.text.replace(u'\xa0', u' ')