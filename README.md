# [blog.geographer.fr](https://blog.geographer.fr/)

Personal blog, by Lucas SANTONI.


## Static Engine

This blog uses [Pelican](https://docs.getpelican.com/en/stable/), a Python
project, to statically generate content. The theme is custom, located in the
`theme/` folder.

There are a few custom variables in the `pelicanconf.py` configuration file.
Their names should be explicit enough.


## Dependency Management

Python dependencies are managed using [Pipenv](https://github.com/pypa/pipenv).
In order to install them:

```
pipenv install
pipenv shell
```

Because this blog is deployed using [Vercel](https://vercel.com/), a
`requirements.txt` file also has to be kept up to date. In order to update it:

```
pipenv lock -r > requirements.txt
```

There are also JavaScript dependencies managed via
[npm](https://www.npmjs.com/). In order to install them:

```
npm install
```


## Local Setup

After having installed all the dependencies:

```
gulp dev
```

Now the website is re-built whenever a file changes. The output is written in
the `public/` directory.

Use whatever server you prefer to serve this directory and preview the changes
locally. For instance:

```
npm run serve
```

Check the output of the command to know where the website is served at!


## Production Setup

Nothing to do, Vercel and GitHub do all the work.


## Contribute

Just make a pull request. The Vercel bot will automatically reply to the pull
request with a link for you to preview your changes. I will merge it.

I do not have any plans for translations right now. All articles have to be
written in english.