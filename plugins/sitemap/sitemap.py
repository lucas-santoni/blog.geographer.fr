import os

import urllib.parse
from pelican import signals, contents

# Generate an XML sitemap for the blog
# The XML sitemap is NOT manually sent to Google but it is publicaly
# available

# The output filename
FILENAME = 'sitemap.xml'

# Table for change frequencies
# These are default values that can be overriden in the configuration file
# of the blog
# The underscore values come from Pelican
CHANGE_FREQUENCIES = {
    '_index': 'daily',
    '_articles': 'monthly',
    '_pages': 'monthly',
    '_default': 'weekly',
}

# Table for the priorities
# These are default values that can be overriden in the configuration file
# of the blog
PRIORITIES = {
    '_default': 0.5
}

# In order to generate the sitemap, we use a bunch of Python templates
# that we glue together

# Last modificagtion template
DATE_TEMPLATE = '\n    <lastmod>{}</lastmod>'

# URL Template
URL_TEMPLATE = '''  <url>
    <loc>{loc}</loc>{lastmod}
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>'''

# Root template
SITEMAP_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{}
</urlset>
'''


# Get the content priority associated with a Pelican content object
def get_content_priority(content):
    if content.slug in PRIORITIES:
        return PRIORITIES[content.slug]

    return PRIORITIES['_default']


# Get the content change frequency associated with a Pelican content object
def get_content_change_frequency(content):
    if content.slug in CHANGE_FREQUENCIES:
        return CHANGE_FREQUENCIES[content.slug]

    if isinstance(content, contents.Article):
        return CHANGE_FREQUENCIES['_articles']

    if isinstance(content, contents.Page):
        return CHANGE_FREQUENCIES['_pages']

    return CHANGE_FREQUENCIES['_default']


# Get the last modification date for a Pelican content object
def get_content_last_date(content):
    # Prioritize the last update date
    if hasattr(content, 'modified'):
        return content.modified

    if hasattr(content, 'date'):
        return content.date

    return None


class SitemapGenerator():
    def __init__(self, context, settings, path, theme, output_path):
        self.context = context
        self.output_path = output_path

        # Merge constants with configuration
        CHANGE_FREQUENCIES.update(context['CHANGE_FREQUENCIES'])
        PRIORITIES.update(context['PRIORITIES'])

        # Get slugs to exclude
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

        # Store all the url blocks
        buffer = []

        # Iterate over all pages, articles, mixed
        for c in content:
            # Date can be YYYY-MM-DD or nothing
            date = get_content_last_date(c)
            date_formated = None
            if date is not None:
                date_formated = DATE_TEMPLATE.format(date.strftime('%Y-%m-%d'))

            # Join site url and content slug
            url = urllib.parse.urljoin(self.context['SITEURL'], c.slug)
            # Update frequency
            frequency = get_content_change_frequency(c)
            # Document priority
            priority = get_content_priority(c)

            # Store the URL block
            buffer.append(URL_TEMPLATE.format(
                loc=url,
                lastmod=date_formated or '',
                changefreq=frequency,
                priority=priority
            ))

        # Don't forget the index page
        buffer.append(URL_TEMPLATE.format(
            loc=self.context['SITEURL'],
            lastmod=None,
            changefreq=CHANGE_FREQUENCIES['_index'],
            priority=PRIORITIES['_default']
        ))

        # Join all the URL blocks into the final template
        sitemap = SITEMAP_TEMPLATE.format('\n'.join(buffer))

        # Write sitemap to disk
        with open(path, 'w+') as f:
            f.write(sitemap)


def get_generators(generators):
    return SitemapGenerator


def register():
    signals.get_generators.connect(get_generators)
