from article import Article
from broker import SentenceBroker

if __name__ == "__main__":
    urls = ["https://en.wikipedia.org/wiki/Wolfgang_Amadeus_Mozart"]
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
        tag = 'ul'
        for sentence in sb.get_sentences_with_tag(tag):
            original = sentence['text']
            previous = sb.get_previous_sentence(sentence, tag)
            print('Original sentence:', original)
            print('Previous sentence:', previous)
            print("=================")