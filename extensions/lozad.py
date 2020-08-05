from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import re


class FigureCaptionProcessor(BlockProcessor):
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


class FigureCaptionExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add(
            'figureAltcaption', FigureCaptionProcessor(md.parser), '<ulist')


def makeExtension(**kwargs):
    return FigureCaptionExtension(**kwargs)
