from article import Article
from broker import SentenceBroker
import sys

def process(url, html, tag):
    broker = SentenceBroker(html)
    results = []
    for sentence in broker.get_sentences_with_tag(tag):
        original = sentence['text']
        previous = broker.get_previous_sentence(sentence, tag)
        rs = broker.getTriple(previous, original)
        if rs:
            results.append(rs)
    return results

def main(input_filename, tag_name, output_filename):
    with open(input_filename, 'r', encoding = 'utf-8') as input_file:
        urls = input_file.read().splitlines()

    count = 0
    for url in urls:
        print("url: ", url)
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
        try:
            results = process(url, article.html, tag_name)
            with open(output_filename, 'a', encoding = 'utf-8') as output_file:
                for result in results:
                    output_file.write(str(count) + ',"' + str(result) + '"\n')
                    count += 1
        except:
            print("broker ERROR at ", url)

if __name__ == '__main__':
    # arguments
    input_filename, tag_name, output_filename = sys.argv[1], sys.argv[2], sys.argv[3]
    # main
    main(input_filename, tag_name, output_filename)
