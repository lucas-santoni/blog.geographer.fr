#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from __future__ import unicode_literals

#
# SETTINGS
# These are general settings related to Pelican
#

# Useful for dates format
LOCALE = 'en_US.UTF-8'
DEFAULT_LANG = 'en'

# TODO Is it still relevant?
TIMEZONE = 'Europe/Paris'

# The theme is custom, see the theme/ folder
THEME = 'theme'

# Configure the Markdown processor
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',  # CSS class used for code snippets
            'guess_lang': False,  # Try not to guess the language
            'linenums': False,  # Do not input line numbers
        },
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {},
    },
    'output_format': 'html5',
}

# Folders statically served
STATIC_PATHS = ['assets', 'static-root']

# Files in static-root/ must be added here, or moved to another directory
# Indeed we want all files in static-root/ to be served at the root
# We don't seem to have any way to enforce this unfortunately
EXTRA_PATH_METADATA = {
    'static-root/levenshtein.js': {'path': 'levenshtein.js'},
    'static-root/favicon.ico': {'path': 'favicon.ico'},
    'static-root/pwa-icon.png': {'path': 'pwa-icon.png'},
    'static-root/apple-touch-icon.png': {'path': 'apple-touch-icon.png'},
    'static-root/manifest.json': {'path': 'manifest.json'},
    'static-root/robots.txt': {'path': 'robots.txt'},
    'static-root/keybase.txt': {'path': 'keybase.txt'}
}

# TODO What is this?
PATH = 'content'

# Feed settings
FEED_ALL_RSS = 'rss.xml'
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# What we want to generate
PAGE_SAVE_AS = '{slug}.html'
ARTICLE_SAVE_AS = '{slug}.html'

# What we DON'T want to generate
AUTHOR_SAVE_AS = ''
CATEGORY_SAVE_AS = ''
TAG_SAVE_AS = ''
YEAR_ARCHIVE_SAVE_AS = ''
DAY_ARCHIVE_SAVE_AS = ''
ARCHIVES_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
CATEGORIES_SAVE_AS = ''
TAGS_SAVE_AS = ''
#
# END OF SETTINGS
#

#
# VARIABLES
# These variables are used in the template
#

# TODO Allow for different authors depending on the article/page
AUTHOR = 'Lucas Santoni'

SITENAME = 'Lucas Santoni'
TWITTER_HANDLE = 'geographeur'
MAIL = 'lucas.santoni@live.fr'
SITE = 'blog.geographer.fr'
SITEURL = f'https://{SITE}'
TWITTER_URL = 'https://twitter.com/' + TWITTER_HANDLE
GITHUB_URL = 'https://github.com/geospace'
MAIL_URL = 'mailto:' + MAIL

SITE_INTRO = '''
I am a computer science enthusiast. My fields of interest are cybersecurity
and software development. Please, see the <a href="/about">about page</a> or
read <a href="/resume">my resume</a> if you want to know more.
'''

SITE_DESCRIPTION = '''
A blog about computer security and programming. With CTF writeups, side
projects, memos...
'''

#
# END OF VARIABLES
#

#
# PLUGINS
# These are plugins configurations
# Some of them are custom, just read the sources in plugins/ if not sure
#

PLUGINS = [
    'plugins.title-smart-break',  # Avoid single words in titles
    'plugins.api',  # Generate a client side index of all the content
    'plugins.sitemap',  # Generate a sitemap
    'plugins.readtime',  # Insert read times
]

# Change frequency for sitemap plugin
CHANGE_FREQUENCIES = {
    'resume': 'yearly',
}

# Result priorities for sitemap plugin
PRIORITIES = {
    'hexpresso-fic': 0.6,
}

# Slugs of the articles/pages we don't want to appear in the sitemap
EXCLUDE_SLUGS = [
    '404',  # The 404 page
    'posts',  # The post index, does not really have content
    'internet-error',  # The WPA internet error page, not relevant
]

# Slugs of the articles/pages we don't want to appear in the site API
API_EXCLUDE_SLUGS = [
    '404',  # See above for explanations
    'internet-error',
    'posts',
    'about',
]

#
# END OF PLUGINS
#

#
# PROJECTS
# Projects are displayed on the front page
#

# TODO Turn this into articles


class project():
    pass


POOL_2019 = project()
POOL_2019.name = 'PoC Security Pool 2019 [French]'
POOL_2019.emoji = '🏊‍♂️'
POOL_2019.description = '''
In early 2019, I teached ~30 EPITECH students the basics of computer
security. This is the teaching material I wrote for this occasion.
<a href="/piscine-poc-2019">Browse it here.</a>
'''

THIS_BLOG = project()
THIS_BLOG.name = 'This blog'
THIS_BLOG.emoji = '📖'
THIS_BLOG.description = '''
This blog is statically generated using
<a href="https://blog.getpelican.com/">Pelican</a>, and hosted on
<a href="https://zeit.co/dashboard">Now</a>. Feel free
to <a href="https://github.com/Geospace/blog.geographer.fr">contribute</a>.
'''

SQLI_PLATFORM = project()
SQLI_PLATFORM.name = 'SQLi Platform'
SQLI_PLATFORM.emoji = '💉'
SQLI_PLATFORM.description = '''
A WEB application written in JavaScript that makes it simple to understand
and visualize SQL injections. Easy to launch via Docker.
<a href="https://github.com/Geospace/sqli-platform">Get it here.</a>
'''

PROJECTS = [
    POOL_2019,
    THIS_BLOG,
    SQLI_PLATFORM
]

#
# END OF PROJECTS
#
