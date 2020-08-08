# Add the lozad class to img tags
# so that they can be lazy-loaded

from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import re


class LozadProcessor(BlockProcessor):
    RE = re.compile(r'!\[(?P<caption>.*?)\]\((?P<url>.*?)\)')

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        raw_block = blocks.pop(0)
        parsed = self.RE.search(raw_block)

        img = etree.SubElement(parent, 'img')
        img.set('data-src', parsed.group('url'))
        img.set('alt', parsed.group('caption'))
        img.set('class', 'lozad')


class LozadExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add(
            'LozadExtension',
            LozadProcessor(md.parser),
            '<ulist',
        )


def makeExtension(**kwargs):
    return LozadExtension(**kwargs)
