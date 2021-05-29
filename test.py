from article import Article
from broker import SentenceBroker

if __name__ == "__main__":
    urls = ["https://en.wikipedia.org/wiki/!Decapitacion!"]
    for url in urls:
        # get article only url exist
        try:
            article = Article(url)
        except KeyboardInterrupt:
            break
        except:
            print("ERROR: ", url, "doesn't exist")
            continue
        # process sentences from html
        # use try-catch for some broker error
        html = article.html
        sb = SentenceBroker(html)
        for d in sb.sentences:
            print(d)