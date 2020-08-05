# https://github.com/getpelican/pelican-plugins/blob/master/readtime

import re
import math

from pelican import signals
from pelican.generators import ArticlesGenerator
from html.parser import HTMLParser

# Add a readtime property to the articles
# Based on simple WPM count
# Source code blocks are ignored
# We are assuming that the HTML is well formated

WPM = 230  # Words Per Minute
CODE_BLOCK_TAGS = ['pre']  # We ignore blocks of code


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.acc = []
        self.code_stack = 0

    def handle_starttag(self, tag, _):
        if tag in CODE_BLOCK_TAGS:
            # Keep track that a code block as opened
            self.code_stack += 1

    def handle_endtag(self, tag):
        if tag in CODE_BLOCK_TAGS:
            # A code block has closed
            self.code_stack -= 1

    def handle_data(self, data):
        if self.code_stack == 0:
            # This means we are NOT in a code block
            self.acc.append(data)

    def get_data(self):
        return ''.join(self.acc)


def strip_tags(html_data):
    p = MyHTMLParser()
    p.feed(html_data)

    # May be able to detect HTML malformations
    assert(p.code_stack == 0)

    return p.get_data()


def add_readtime_property(document):
    text = strip_tags(document.content)
    words = re.split(r'[^0-9A-Za-z]+', text)
    nb_words = len(words)

    minutes = max(1, int(math.ceil(nb_words / WPM)))

    document.readtime = minutes


def run(generators):
    for g in generators:
        if isinstance(g, ArticlesGenerator):
            for a in g.articles:
                add_readtime_property(a)


def register():
    signals.all_generators_finalized.connect(run)
