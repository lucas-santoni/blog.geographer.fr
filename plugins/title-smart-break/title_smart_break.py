from pelican import signals
from pelican.generators import ArticlesGenerator, PagesGenerator

# Make sure than when a title breaks, there will never be
# a single word "alone" on its line
# Does not work if the last "word" of the title is an emoji
# in the form of an image (like Twemoji)

# Title has to be more than four words
# in order to be considered
SMART_BREAK_MIN_LEN = 4


def smart_break(document):
    # Get the number of words
    splited = document.title.split(' ')
    length = len(splited)

    if length > SMART_BREAK_MIN_LEN:
        # Join the last two elements with a non-breaking space
        end = '&nbsp;'.join(splited[length - 2:])
        # Get the start of the title back
        start = ' '.join(splited[:length-2])

        # Glue the title back together
        final = f'{start} {end}'

        # Write to a custom property
        # Writing the title directly leads to &nbsp; not being
        # interpreted at various places
        document.smart_title = final


def run(generators):
    for g in generators:
        if isinstance(g, ArticlesGenerator):
            for a in g.articles:
                smart_break(a)
        if isinstance(g, PagesGenerator):
            for p in g.pages:
                smart_break(p)


def register():
    signals.all_generators_finalized.connect(run)
