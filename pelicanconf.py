#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from __future__ import unicode_literals

# SITE INFORMATION
AUTHOR = "Geographer"
SITENAME = "Geographer"
SITEURL = ""

# THEME
THEME = "theme"

# LINKS
GITHUB_URL = "https://github.com/geospace"
TWITTER_URL = "https://twitter.com/geographeur"

# STATIC_PATHS
STATIC_PATHS = ["assets"]

# SITE INTRO
SITE_INTRO = """
I am a computer science enthusiast. My fields of
interest are cybersecurity and software development. This blog is mostly
about CTF writeups, personnal projects, and memos. Please,
<a href="/about">click here</a> if you want to know more.
"""

# FOOTER
FOOTER_TEXT = "Happily made in 🇫🇷, the most beautiful country in the world..."

# PATH
PATH = "content"

# TIME
TIMEZONE = "Europe/Paris"
DEFAULT_LANG = "en"

# FEED
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# DO NOT GENERATE
PAGE_SAVE_AS = "{slug}.html"
AUTHOR_SAVE_AS = ""
CATEGORY_SAVE_AS = ""
TAG_SAVE_AS = ""
YEAR_ARCHIVE_SAVE_AS = ""
DAY_ARCHIVE_SAVE_AS = ""
ARCHIVES_SAVE_AS = ""
AUTHORS_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
TAGS_SAVE_AS = ""

# BLOGROLL
LINKS = ()

# SOCIAL
SOCIAL = ()

# PAGINATION
# DEFAULT_PAGINATION = 5

# RELATIVE
# RELATIVE_URLS = True


# PROJECTS
class project():
    pass


POOL_2019 = project()
POOL_2019.name = "PoC Security Pool 2018 [French]"
POOL_2019.emoji = "🏊‍♂️"
POOL_2019.description = """
In 2018, I teached ~30 EPITECH students the basics of computer security. This
is the teaching material I wrote for this occasion.
<a href="/piscine-poc-2019">Browse it here.</a>
"""

THIS_BLOG = project()
THIS_BLOG.name = "This blog"
THIS_BLOG.emoji = "📖"
THIS_BLOG.description = """
This blog is statically generated using a custom Python script. Feel free to
<a href="https://github.com/Geospace/geoblog">contribute</a>.
"""

SQLI_PLATFORM = project()
SQLI_PLATFORM.name = "SQLi Platform"
SQLI_PLATFORM.emoji = "💉"
SQLI_PLATFORM.description = """
A WEB application written in JavaScript that makes it simple to understand
and visualize SQL injections. Easy to launch via Docker.
<a href="https://github.com/Geospace/sqli-platform">Get it here.</a>
"""

# PROJECTS
PROJECTS = [
    POOL_2019,
    THIS_BLOG,
    SQLI_PLATFORM
]
