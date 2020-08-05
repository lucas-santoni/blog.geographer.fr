import os

from pelican import signals

# Generate an "API" for the blog
# It is actually a JavaScript array that can be easily consumed
# and allows to search for an article, via title or slug

# Template for the content
JS_BASE = '''const API = [
  {}
];
'''

# Output filename
FILENAME = 'api.js'


class APIGenerator():
    def __init__(self, context, settings, path, theme, output_path):
        self.context = context
        self.output_path = output_path

        # Slugs to exclude
        self.exclude = self.context['API_EXCLUDE_SLUGS']

    def generate_output(self, writer):
        # Final file path
        path = os.path.join(self.output_path, FILENAME)

        # Extract pages and articles
        content = \
            self.context['articles'] + \
            self.context['pages']

        # Remove the content that must be excluded
        content = [c for c in content if c.slug not in self.exclude]

        # Get all the slugs, and titles
        slugs = [c.slug for c in content]
        titles = [c.title for c in content]

        # Escape quotes in the title
        titles = [title.replace('\'', '\\\'') for title in titles]

        # Format objects
        objs = [
            f'{{ title: \'{title}\', slug: \'{slug}\' }}'
            for title, slug in zip(titles, slugs)
        ]

        # JavaScript array content
        js_array_elements = ',\n  '.join(objs)

        # Put content into array
        js = JS_BASE.format(js_array_elements)

        # Write JS file
        with open(path, 'w+') as fd:
            fd.write(js)


def get_generators(generators):
    return APIGenerator


def register():
    signals.get_generators.connect(get_generators)
