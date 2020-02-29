# [blog.geographer.fr](https://blog.geographer.fr/)

Personal blog, by Lucas SANTONI, also (not) known as [Geographer](https://twitter.com/geographeur).


## Static engine

This blog uses [Pelican](https://docs.getpelican.com/en/stable/), a Python
project, to statically generate content. The theme is custom, located in the
`theme/` folder.

There are a few custom variables in the `pelicanconf.py` configuration
file but there should be explicit enough.


## Dependency Management

Python dependencies are managed using [Pipenv](https://github.com/pypa/pipenv).
In order to install them:

```
pipenv install
pipenv shell
```

Because this blog is deployed using [Now](https://zeit.co/), a
`requirements.txt` file also has to be kept up to date. In order to update it:

```
pipenv lock -r > requirements.txt
```


## Contribute

Just make a pull request. The Now bot will automatically reply to the pull
request with a link for you to preview your changes. I will merge it.

I do not have any plans for translations right now. All articles have to be
written in english.
