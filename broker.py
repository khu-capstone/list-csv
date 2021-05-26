from nltk import word_tokenize, sent_tokenize, pos_tag
from openie import StanfordOpenIE
import re
 
class Broker():
    def __init__(self, html):
        self.html = html
        self.index = 0 # Broker index
        self.stack = [] # tag stack
        self.data = [] # structured data with tag, attr, text, block
        self.tag = None
        self.tags = None
        self.attr = None
        self.attrs = None
        self.block = 0 # Borker index for block
        self.blocks = []
        self.text = ''
        # tags with no closing
        self.non_closing_tags = ["area", "base", "br", "col", "command", "embeded", "hr", "img", "input", "keygen", "link", "meta", "param", "source", "track", "wbr", "!--"]
        # tags with article
        self.article_tags = ['div', 'p', 'li', 'ul', 'ol', 'h1', 'h2', 'h3']
        self.process()
    
    def process(self):
        while self.index < len(self.html):
            # blank space process
            if self.html[self.index] in "\n\t":
                self.index += 1
                continue
            # lf other tags
            elif self.html[self.index] == '<' and self.html[self.index + 1] not in "0123456789": # <0.01
                self.tag_process()
            # else not tag
            else:
                self.text_process()
        self.split_dots() # split at dots
        self.split_block() # split as blocks
    
    def tag_process(self):
        self.update_tags()
        self.update_tag()
        self.update_attr()
        self.update_stack()
        self.update_block()

    def text_process(self):
        self.update_text()
        self.update_data()
    
    # find tags(<p>, <span id="..">, <div ...>, </p> ...) from html
    def update_tags(self):
        self.tags = ''
        while self.html[self.index] != '>':
            self.tags += self.html[self.index]
            self.index += 1
        # add '>'
        self.tags += self.html[self.index]
        self.index += 1

    # find tag(p, span, div ...) from tags(<p>, <span id="..">, <div ...>, </p> ...
    def update_tag(self):
        if ' ' in self.tags: # nonsingle open tag (<p id="..">, <span class=".."> ...)
            self.tag = list(self.tags.split(' '))[0][1:]
        else: # single open/close tag (<p>, </p> <span> ...)
            self.tag = self.tags[1:-1]
  
    # find attr(id="..", class="..." ...) from tags(<p>, <span id="..">, <div ...>, </p> ...
    def update_attr(self):
        if ' ' in self.tags: # if nonsingle tags
            self.attr = list(self.tags[:-1].split(' ')[1:])
        else:
            self.attr = None

    # update stack: pop if closing tag, push if open tag
    def update_stack(self):
        # if close tag, pop tag
        if self.tag[0] == '/':
            self.stack.pop()
        # else open tag with closing, push tag
        elif self.tag not in self.non_closing_tags:
            self.stack.append([self.tag, self.attr])
    
    # update block: seperate article into blocks
    def update_block(self):
        if self.tag in self.article_tags:
            self.block += 1
    
    # find text(not tags) from html
    def update_text(self):
        self.text = self.html[self.index]
        self.index += 1
        while self.html[self.index] != '<':
            # remove newline
            if self.html[self.index] == '\n':
                self.index += 1
                continue
            self.text += self.html[self.index]
            self.index += 1

    # update sentence: save texts with all tags and attrs
    def update_data(self):
        if self.text in "\n\t" or self.text == ' '*len(self.text):
            return # for empty text
        self.tags, self.attrs = [], []
        for self.tag, self.attr in self.stack:
            self.tags.append(self.tag)
            self.attrs.append(self.attr)
        # compress header
        if self.data and self.has_header(self.tags) and self.has_header(self.data[-1]['tag']):
            self.data[-1]['text'] += self.text
        else:
            self.data.append({"tag":'>'.join(self.tags), "attr":self.attrs, "text":self.text, "block":self.block})

    # split data at dot
    def split_dots(self):
        datas = []
        for data in self.data:
            text = data['text']
            while '.' in text:
                index = text.find('.')
                new_text = text[:index + 1]
                datas.append({"tag":data["tag"], "attr":data["attr"], "text":new_text, "block": data["block"]})
                text = text[index + 1:]
            datas.append({"tag":data["tag"], "attr":data["attr"], "text":text, "block": data["block"]})
        self.data = datas[:]
    
    # split document into block
    def split_block(self):
        block = []
        index_block = self.data[0]['block']
        for data in self.data:
            if index_block == data['block']:
                block.append(data)
            else:
                self.blocks.append(block[:])
                index_block = data['block']
                block = [data]
    
    @staticmethod
    def has_header(tag):
        if 'h1' in tag or 'h2' in tag or 'h3' in tag or 'h4' in tag or 'h5' in tag or 'h6' in tag:
            return True
        return False

class SentenceBroker(Broker):
    def __init__(self, html):
        self.sentence = []
        self.sentences = [] # data with sentence number
        self.line = 0 # line index
        super().__init__(html)

    def process(self):
        super().process()
        for i, blocks in enumerate(self.blocks):
            self.make_sentences(blocks)
            self.update_sentences(blocks)
        self.remove_wiki() # remove wikipedia specific
        self.remove_empty() # remove empty sentence

    # make sentences with block
    def make_sentences(self, blocks):
        sentence = ""
        for block in blocks:
            sentence += block['text']
        self.sentence = sent_tokenize(sentence)
    
    def update_sentences(self, blocks):
        index_i, index_j = 0, 0 # j index for sentences
        for block in blocks:
            text = block['text']
            while text:
                if text[0] in ['\n', ' ']: # erase indent
                    text = text[1:]
                    continue
                if self.sentence[index_i][index_j] in "\n ": # erase indent
                    index_j += 1
                    continue
                # "abcd", "abcd"
                if text == self.sentence[index_i][index_j:]:
                    article_tag = self.deep_article_tag(block['tag'])
                    self.sentences.append({'line':self.line, 'tag':article_tag, 'text':self.sentence[index_i]})
                    self.line += 1
                    text = ''
                    index_i += 1
                    index_j = 0
                # "abcd", "ab" -> impossible
                # just ignore same index
                elif text[:len(self.sentence[index_i][index_j:])] == self.sentence[index_i][index_j:]:
                    self.line += 1
                    text = text[len(self.sentence[index_i][index_j:]):]
                    index_i += 1
                    index_j = 0
                # "ab", "abcd"
                elif text == self.sentence[index_i][index_j:index_j+len(text)]:
                    index_j += len(text)
                    text = ''
                else:
                    print("ERROR in SentenceBroker: update_sentences()")
                    exit()

    # get deepest article tags
    def deep_article_tag(self, tags):
        tags = tags.split('>')
        for i, tag in enumerate(tags[::-1]):
            if tag in self.article_tags:
                break
        return '>'.join(tags[:len(tags)-i])
        print("ERROR in SentenceBroker: deep_article_tag") # no article tag
        exit()
    
    # get sentence with line no
    def get_sentence(self, line):
        for sentence in self.sentences:
            if sentence['line'] == line:
                return sentence
        return None
    
    # get sentences with tags
    def get_sentences_with_tag(self, tags):
        rs = []
        for sentence in self.sentences:
            if tags in sentence['tag']:
                rs.append(sentence)
        return rs
    
    # get sentences without tags
    def get_sentences_without_tag(self, tags):
        rs = []
        for sentence in self.sentences:
            if tags not in sentence['tag']:
                rs.append(sentence)
        return rs

    # get upper sentence
    def get_upper_sentence(self, u, tag):
        index = u['line']
        while True:
            if not index:
                return None
            s = self.get_sentence(index)
            if s and tag not in s['tag']:
                if 'h1' in s['tag'] or 'h2' in s['tag'] or 'h3' in s['tag'] or 'h4' in s['tag'] or 'h5' in s['tag'] or 'h6' in s['tag']:
                    break
            index -= 1
        return s['text']

    # get previous sentence
    def get_previous_sentence(self, u, tag):
        index = u['line']
        while True:
            if not index:
                return None
            s = self.get_sentence(index)
            if s and tag not in s['tag']:
               break
            index -= 1
        return s['text']
    
    # remove wiki specific
    def remove_wiki(self):
        self.remove_pattern('\[\d+\]')
        self.remove_pattern('\[edit\]')
        
    def remove_pattern(self, pattern):
        regex = re.compile(pattern)
        for sentence in self.sentences:
            for reg in regex.findall(sentence['text']):
                sentence['text'] = sentence['text'].replace(reg, '')
    
    def remove_empty(self):
        rs = []
        for sentence in self.sentences:
            if sentence['text']:
                rs.append(sentence)
        self.sentences = rs[:]

    def get_list_text(self, tag, client):
        rs = []
        for sentence in self.get_sentences_with_tag(tag):
            orig = sentence['text']
            prev = self.get_previous_sentence(sentence, tag)
            uppr = self.get_upper_sentence(sentence, tag)
            if prev:
                pos = pos_tag(word_tokenize(prev))
                vindex, verb = self.verb(pos)
                if not verb: # only nouns
                    r = prev + ' includes ' + orig + '.\n'
                elif prev[-1] == ':' and pos[-1][0] == verb[-1]: # ~ includes:, ~ consists: ...
                    rs.append(prev[:-1] + orig)
                elif prev[-1] == ':' and pos[-2][0] == verb[-1]: # ~ includes of:, ~ consists of: ...
                    rs.append(prev[:-1] + orig)
                else:
                    for triple in client.annotate(prev):
                        rs.append(triple['subject'] + ' ' + triple['relation'] + ' ' + orig)
        return '.'.join(rs)
    
    def getListText(self, tag):
        with StanfordOpenIE() as client:
            return self.get_list_text(tag, client)
    
    @staticmethod
    def verb(pos):
        for i, p in enumerate(pos):
            if 'VB' in p[1]:
                if i < len(p) and 'VB' in pos[i + 1][1]:
                    return i, [p[0], pos[i + 1][0]]
                return i, [p[0]]
        return i, None