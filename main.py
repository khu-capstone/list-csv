import sys

from article import Article
from broker import SentenceBroker

# check argument length valid
# python3 main.py <input filename> <tag name> <output filename>
def argument_check():
    if len(sys.argv) != 4:
        print("Please enter command like this: python3 main.py <input filename> <tag name> <output filename>")
        exit()

# get current-previous sentence combinations from html
def process(url, html, tag):
    broker = SentenceBroker(html)
    results = []
    for sentence in broker.get_sentences_with_tag(tag):
        original = sentence['text']
        previous = broker.get_previous_sentence(sentence, tag)
        print('Original sentence:', original)
        print('Previous sentence:', previous)
        print("=================")
        # <url>,<original sentence>,<previous sentence>
        if not previous:
            previous = ''
        results.append(url + ',"' + original + '","' + previous + '"')
    return results

def main(input_filename, tag_name, output_filename):
    with open(input_filename, 'r', encoding = 'utf-8') as input_file:
        urls = input_file.read().splitlines()
            
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
        results = process(url, article.html, tag_name)
        with open(output_filename, 'a', encoding = 'utf-8') as output_file:
            for result in results:
                output_file.write(result + '\n')

if __name__ == '__main__':
    # check argument length valid
    argument_check()
    # arguments
    input_filename, tag_name, output_filename = sys.argv[1], sys.argv[2], sys.argv[3]
    # main
    main(input_filename, tag_name, output_filename)
