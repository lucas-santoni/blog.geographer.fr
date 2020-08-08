# https://github.com/rdegges/pelican-minify
# Not used anymore, see gulpfile.js at root

import os
import htmlmin
import rcssmin
import jsmin
import pelican


def minify_html(filename):
    with open(filename, 'r') as f:
        # Read file to minify
        uncompressed = f.read()

    with open(filename, 'w') as f:
        # Minify and override
        compressed = htmlmin.minify(uncompressed, remove_comments=True)
        f.write(compressed)


def minify_css(filename):
    with open(filename, 'r') as f:
        # Read file to minify
        uncompressed = f.read()

    with open(filename, 'w') as f:
        # Minify and override
        compressed = rcssmin.cssmin(uncompressed)
        f.write(compressed)


def minify_js(filename):
    with open(filename, 'r') as f:
        # Read file to minify
        uncompressed = f.read()

    with open(filename, 'w') as f:
        # Minify and override
        compressed = jsmin.jsmin(uncompressed)
        f.write(compressed)


# Check if a file is an HTML file, based on its extension
def is_html_file(name):
    return name.endswith('.html') or name.endswith('.htm')


# Check if a file is a CSS file, based on its extension
def is_css_file(name):
    return name.endswith('.css') or name.endswith('.css3')


# Check if a file is a JS file, based on its extension
def is_js_file(name):
    return name.endswith('.js')


def minify_all(ctx):
    # For each directory
    for dirpath, _, filenames in os.walk(ctx.settings['OUTPUT_PATH']):
        # For each file in the directory
        for name in filenames:
            full_path = os.path.join(dirpath, name)

            if is_html_file(name):
                minify_html(full_path)
            elif is_css_file(name):
                minify_css(full_path)
            elif is_js_file(name):
                minify_js(full_path)


def register():
    pelican.signals.finalized.connect(minify_all)
