---
title: ESLint configuration and best practices
slug: eslint-guide
date: 23/01/2020
---

This post describes how I setup [ESLint](https://eslint.org/) in
different scenarios. We'll start with a simple plain JavaScript project
and then we'll deal with TypeScript, and also React. The aim is to do
the things *right* and avoid installing random packages or copy/pasting
snippets of configuration until things work.

It is a complete guide so you might want to read it in its entirety, or
skip to the section you are interested in, depending on whether you
are already confident with ESLint or not. Still, it is made to be read
from top to bottom. If you have never used ESLint before, it is fine.

This guide heavily relies on
[Airbnb](https://github.com/airbnb/javascript) configuration packages as
they are extremely popular and will most likely satisfy you if you
don't already have a preference. However, you can totally use any other
style guide packages if you prefer.

If you've never heard of Airbnb style guide, I highly recommend that
you take a look at the following pieces of documentation:

-   [Airbnb JavaScript style
    guide](https://github.com/airbnb/javascript/blob/master/README.md)
-   [Airbnb React style
    guide](https://github.com/airbnb/javascript/tree/master/react)
-   [Airbnb CSS in JavaScript style
    guide](https://github.com/airbnb/javascript/tree/master/css-in-javascript)
-   [Airbnb Sass style guide](https://github.com/airbnb/css)

There are explanations for every settings. It is also a great starting
point if you wish to design your own configuration.


## Why ESLint?

There is no competing project to my knowledge. ESLint is highly
configurable and well maintained. Most people or company who design
JavaScript style guides implement it for ESLint.

A few alternatives I had the chance to try are:

-   [standardJS](https://standardjs.com/) is a JavaScript linter that
    enforces the *standard* style guide. It is therefore not
    configurable and is not really made for TypeScript. It is a decent
    solution if you are dealing with a plain JavaScript project and do
    not want to spend time configuring your linter. Otherwise, we can
    definitely do better with ESLint. Moreover, standardJS also is
    available as a [standalone ESLint
    configuration](https://github.com/standard/eslint-config-standard)!

-   [gts](https://github.com/google/gts) is a TypesScript linter that
    implements Google's style guide. It is a nice solution, especially
    if you are looking for something that works with 0 configuration.
    The thing is that `gts` actually uses ESLint under the hood and we
    can totally extract the ESLint configuration it is using.

-   [TSLint](https://palantir.github.io/tslint/) is a TypeScript linter
    that used to be very popular. But is has been
    [deprecated](https://github.com/palantir/tslint/issues/4534) and is
    being merged with ESLint. The exact situation is a bit vague but in
    reality, TypeScript linting is totally possible inside ESLint, with
    the [approtiate
    tooling](https://github.com/typescript-eslint/typescript-eslint).

It is also worth mentioning that most text editors have ESLint plugins.
You will have no trouble integrating live linting into
[VSCode](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint),
[Vim](https://github.com/dense-analysis/ale), or
[Emacs](https://flycheck.readthedocs.io/en/latest/). Some IDEs such as
WebStorm even integrate it [out of the
box](https://www.jetbrains.com/help/webstorm/eslint.html?keymap=primary_default_for_windows).

In short, ESLint is the best platform to build your linting
configuration on.


## ESLint installation

Just like any package, ESLint can be installed at two levels:

-   The *global* level, thanks to `npm -g`
-   The *project* level

It would make sense to install ESLint at the global level so that it
could be invoked from anywhere. However, I prefer to install it at the
project level for a few reasons:

-   Different versions of ESLint for different projects
-   Does not *hide* the ESLint dependecy. There is not reason not to
    make it explicit.
-   Coworkers and automation tools (such as a CI) will install ESLint
    just like they install the other development dependencies of the
    project. No extra setup or documentation required.

The two mechanisms that allow us to properly install and use ESLint at
the project level are:

-   The [devDependency](https://docs.npmjs.com/specifying-dependencies-and-devdependencies-in-a-package-json-file)
    entry in the `package.json` file
-   Local packages binary invocation thanks to
    [npx](https://www.freecodecamp.org/news/npm-vs-npx-whats-the-difference/)

Now that we know that, installing ESLint is as simple as running (inside
the project's directory):

```
npm i eslint --save-dev
```

In order to run ESLint inside the project:

```
npx run eslint
```

It may be a good idea to rely on npm's task running mechanism to hide
the command line arguments we are using and get a cleaner interface. In
the `package.json` file we can add:

```json
"scripts": {
  "lint": "eslint ."
}
```

The `.` parameter allows to run ESLint in the current directory. It can
now be invoked via the `lint` task:

```
npm run lint
```

ESLint is recursive by default so it will correctly lint any `.js` file.


## ESLint configuration file

ESLint reads configuration files at [various
locations](https://eslint.org/docs/user-guide/configuring#configuration-cascading-and-hierarchy).
Most of time, a single configuration file at the root of the project is
enough.

ESLint allows for multiple configuration formats:

-   JavaScript
-   JSON
-   YAML

I find the YAML format to be the most concise and enjoyable. This is the
format I am going to use for this guide. Therefore, our configuration
file will be named `.eslintrc.yaml`. Let's create it at the root of our
project:

```
touch .eslintrc.yaml
```

We are going to tell ESLint about the language features (the [ECMA
version](https://eslint.org/docs/user-guide/configuring#specifying-parser-options))
we want to enable, but also [the
environment](https://eslint.org/docs/user-guide/configuring#specifying-environments)
our code will run on. Without these pieces of information, ESLint will
report false positives. Here is what we can put in our configuration
file for a Node.js ES6 project:

```yaml
parserOptions:
  ecmaVersion: 6
env:
  node: true
```

It is now time to configure some rules!


## Getting Started / Plain JavaScript

Let's start with the plain JavaScript scenario. We have a project with
a bunch of `.js` files that we would like to lint.

We could create a configuration from scratch, tweaking the
[rules](https://eslint.org/docs/rules/) that ESLint exposes to us. But
it is not a very good idea for multiple reasons:

-   It is time consumming
-   It is hard to maintain
-   It reflects your *own* understanding of JavaScript

A lot of companies such as
[Google](https://github.com/google/eslint-config-google),
[Airbnb](https://github.com/airbnb/javascript/tree/master/packages/eslint-config-airbnb)
or
[Facebook](https://github.com/facebook/fbjs/tree/master/packages/eslint-config-fbjs-opensource)
spend a lot of time maintaining configuration that are already widely
adopted, have sane defaults and are kept up to date.

My favorite one is Airbnb's and this is the one we are going to use. Let's
install it:

```
npx install-peerdeps --dev eslint-config-airbnb-base
```

Most online tutorials will recommend that you install the `eslint-config-airbnb`
package, which also includes configurations for React, React Hooks, etc. This is
not necessary in our case, as we are dealing with a plain JavaScript project.

Note that we are **not** using `npm` to install the package but `npx
install-peerdeps`. This is because the configuration package has peer
dependencies. This is actually the case for most ESLint configuration packages
as they usually depend on ESLint plugins, or even other configuration packages.

Once the configuration package is installed, let's use it in our
configuration:

```yaml
extends:
  - airbnb-base
```

We are inheriting Airbnb's configuration and ESLint now reports errors.
Here is what a report looks like:

```
> eslint .


/Users/geographer/Documents/eslint/plain-js/src/index.js
   4:13  error    Expected '===' and instead saw '=='  eqeqeq
   5:5   warning  Unexpected console statement         no-console
   5:42  error    Missing semicolon                    semi
   9:3   warning  Unexpected console statement         no-console
  10:3   warning  Unexpected console statement         no-console
  11:3   error    Unnecessary return statement         no-useless-return
  14:2   error    Missing semicolon                    semi

✖ 7 problems (4 errors, 3 warnings)
  3 errors and 0 warnings potentially fixable with the `--fix` option.
```

For each file, we get a list of errors.

-   The first column tells us the line number and the column of the error
-   The second conlumn is the severity of the error
-   The third column describes the error itself
-   The fourth column is the *internal name* of the error

Knowing the *internal name* of an error allows us to search for it in
the [documentation](https://eslint.org/docs/rules/) to know more, or
quickly tweak our configuration. We are in a Node project so we might
consider that a `console` statement is not a problem. Here is how we can
disable the rule `no-console`:

```yaml
rules:
  no-console: off
```

Rules can also have parameters, which are passed as a list. Let's say
that we only want to allow `console.error` and `console.warn`:

```yaml
rules:
  no-console:
  - error
  - allow:
    - warn
    - error
```

Our settings override the configuration packages we are inheriting.

The report also mentions the `--fix` option. It works really well in
order to automatically fix simple problems such as indentation or missing
semicolons. There is also `--fix-dry-run` which gives an overview of the
fixes, without actually writing the filesystem.

For a plain JavaScript project, this is enough configuration for me. I
try not to override Airbnb's rules as it this configuration is super
popular as it is and it might disturb my coworkers.

Let's recap! The dependencies are:

```json
"devDependencies": {
  "eslint": "^6.1.0",
  "eslint-config-airbnb-base": "^14.0.0",
  "eslint-plugin-import": "^2.20.0" (peer dependency)
}
```

And the final configuration is:

```yaml
parserOptions:
  ecmaVersion: 6

env:
  node: true

extends:
  - eslint:recommended
  - airbnb-base

rules:
  no-console:
  - error
  - allow:
    - warn
    - error
```


## TypeScript configuration

Let's move on and configure ESLint to work with a TypeScript project.

The main problem with TypeScript is that ESLint is not able to parse it
(well, its [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree), to
be exact) out of the box. Therefore we need to use a custom parser:
[@typescript-eslint/parser](https://github.com/typescript-eslint/typescript-eslint/tree/master/packages/parser).
Let's install it:

```
npm install @typescript-eslint/parser --save-dev
```

*Note: the parser is responsible for reading input files and generating
abstract representations that can be understood by ESLint.*

We can now tell ESLint to use this parser instead of the default one:

```yaml
parser: "@typescript-eslint/parser"
```

Let's also update our `package.json` and tell ESLint that it must not
lint `.js` (the default) files but `.ts` files instead:

```json
"scripts": {
  "lint": "eslint . --ext .ts"
},
```

ESLint can now correctly parse our TypeScript files. Just like we did
with the JavaScript project, we are now going to install Airbnb base
configuration:

```
npx install-peerdeps --dev eslint-config-airbnb-typescript
npm i eslint-plugin-import --save-dev
```

`eslint-plugin-import` has to be installed manually. I don't really
know why it is not a peer dependency as the configuration does not run
without it.

Let's update our ESLint configuration in order to inherit from Airbnb's:

```yaml
extends:
  - airbnb-typescript/base
```

*You could also extend from `airbnb-typescript`, which enables support
for React, React Hooks, TSX... But this is not necessary in our case.*

The linting now works for TypeScript, just like it used to for
JavaScript. The `airbnb-typescript` plugin actually wraps
`eslint-config-airbnb` so that it works with TypeScript. You do not need
to explicitly inherit from `airbnb-base` for this to work, as all the
wrapping is done under the hood.

Still, we don't have any TypeScript-specific rulling for now. We
reproduced the JavaScript setup we got before in TypeScript, but nothing
more. In order to get TypeScript-specific rulling, we are going to
inherit from another configuration:

```yaml
extends:
  - airbnb-typescript/base
  - plugin:@typescript-eslint/recommended
```

You might think that we never installed `@typescript-eslint`, but it is
actually a peer dependency of `eslint-config-airbnb-typescript`, so we
are fine. Inheriting from this configuration allows us to get
TypeScript-specific recommended rules, such as *Missing return type on
function*.

A lot of tutorials recommend that you also inherit from
`plugin:@typescript-eslint/eslint-recommended`. This configuration
actually is the TypeScript wrapper for `eslint:recommended`. (Unlike
Airbnb, ESLint does not perform its TypeScript wrapping under the hood
so you need to explicitly inherit from both configurations.) I don't
think these configurations are necessary in our case as Airbnb's ones
are already doing all the work.

This setup is totally reasonable, although the rules might require a bit
more tweaking than in plain JavaScript. The rules documentation [is
available
here](https://github.com/typescript-eslint/typescript-eslint/tree/master/packages/eslint-plugin).

Another important thing to understand is that TypeScript on its own is a
very powerful *linting* tool. Let's consider this code:

```ts
const compute = (expr: string): number => eval(expr);
compute(3 + 3);
```

It is obviously incorrect as `3 + 3` is not a string. However, ESLint
will not complain about that. Why? Simply because it is not a linting
issue, but an actual compilation error:

```
2:9 - error TS2345: Argument of type 'number' is not assignable to parameter of type 'string'.

2 compute(3 + 3);
          ~~~~~


Found 1 error.
```

If you are using an IDE, both ESLint and the TypeScript compiler outputs
are often combined, which is even more powerful.

Finally, you will see a lot of articles recommending that you include
this in you ESLint configuration:

```yaml
plugins:
  - "@typescript-eslint"
```

If you are not using ESLint's recommended settings, this is not
necessary. The reason is that Airbnb already enable this plugin for the
scope of its rules. Other configurations that are designed differently
might require it though. Actually, the same goes for the parser settings
that we put in our configuration at the beginning of this section. But I
usually keep it as it immediately indicates that this configuration is
for TypeScript.

Let's do a little recap! The dependencies are:

```json
"devDependencies": {
  "@typescript-eslint/eslint-plugin": "^2.17.0", (peer dependency)
  "@typescript-eslint/parser": "^2.17.0",
  "eslint": "^6.8.0",
  "eslint-config-airbnb-typescript": "^6.3.1",
  "eslint-plugin-import": "^2.20.0"
}
```

And the final configuration is:

```yaml
# This line can actually be removed
parser: "@typescript-eslint/parser"

parserOptions:
  ecmaVersion: 6

env:
  node: true

extends:
  - airbnb-typescript/base
  - plugin:@typescript-eslint/recommended

# Add your own rules here, as needed
```


## React Configuration

Adding React support to ESLint is very easy, especially with Airbnb's
configuration.

One common mistake is to think that the following setting enables React
support:

```yaml
parserOptions:
  ecmaFeatures:
    jsx: true
```

React indeed uses JSX, but in such a way that ESLint can not deal with it. In
order to add React support to ESLint, we should use a plugin called
`eslint-plugin-react`.

**JavaScript project**

When dealing with a JavaScript project, replace `eslint-config-airbnb-base` by
`eslint-config-airbnb`, which has React support.

```
npx install-peerdeps --dev eslint-config-airbnb
```

Then, in ESLint configuration, inherit from it:

```yaml
extends:
  - airbnb
```

It might also be a good idea to update the `env` setting, since we
are not in Node.js project anymore:

```yaml
env:
  browser: true
```

Update `package.json` and tell ESLint to also parse `.jsx` files:

```json
"scripts": {
  "lint": "eslint . --ext .js,.jsx"
}
```

That's it. We can now lint our React project. If you are dealing
with [Next.js](https://nextjs.org/), or any framework that
automatically inject `react` in JSX files, you might be interested
in this setting:

```yaml
rules:
  react/react-in-jsx-scope: off
```

If your code takes advantage of the [React
Hooks](https://reactjs.org/docs/hooks-intro.html), I recommend that
you also inherit from the related configuration (it is **not**
automatically enabled via `airbnb`):

```yaml
extends:
  - airbnb
  - airbnb/hooks
```

Airbnb's React support enables quite a few rules related to
accessibility. They can be quite noisy, especially if accessibility
is not a requirement. There is no mechanism to disable them but here
is a fairly [clean
workaround](https://stackoverflow.com/questions/54504512/eslint-use-airbnb-styles-but-exclude-all-jsx-a11y):

```yaml
extends:
  - airbnb-base
  - airbnb/rules/react
  - airbnb/hooks
```

We manually enable all the sub-configurations, instead of the meta
one, excluding `rules/react-a11y`. The downside to this approach is
that if another sub-configuration is included in the Airbnb package
at some point, we will need to manually import it too. I recommend
to leave the accessibility rules enabled anyway, as they are not
hard to deal with at all.

Let's recap! The dependencies are as follows:

```json
"devDependencies": {
  "eslint": "^6.1.0",
  "eslint-config-airbnb": "^18.0.1",
  "eslint-plugin-import": "^2.20.0", (peer dependency)
  "eslint-plugin-jsx-a11y": "^6.2.3", (peer dependency)
  "eslint-plugin-react": "^7.18.0", (peer dependency)
  "eslint-plugin-react-hooks": "^1.7.0" (peer dependency)
}
```

And here is our configuration:

```yaml
parserOptions:
  ecmaVersion: 6

env:
  browser: true

extends:
  - airbnb
  - airbnb/hooks

rules:
  react/react-in-jsx-scope: off
```

You should take the time to take a look at the list of [ESLint React
rules](https://github.com/yannickcr/eslint-plugin-react#list-of-supported-rules).

**TypeScript project**

When dealing with a TypeScript project, the package to install is
`eslint-config-airbnb-typescript`. It does not have explicit peer
dependencies, which is weird, because a few other packages are
required.

```
npm install eslint-config-airbnb-typescript \
            eslint-plugin-import \
            eslint-plugin-jsx-a11y \
            eslint-plugin-react \
            eslint-plugin-react-hooks \
            @typescript-eslint/eslint-plugin \
            --save-dev
```

Let's update our ESLint configuration:

```yaml
env:
  browser: true

extends:
  - airbnb-typescript
  - airbnb/hooks
  - plugin:@typescript-eslint/recommended
```

That's all! Here are the dependencies:

```json
"devDependencies": {
  "eslint": "^6.8.0",
  "@typescript-eslint/eslint-plugin": "^2.17.0",
  "eslint-config-airbnb-typescript": "^6.3.1",
  "eslint-plugin-import": "^2.20.0",
  "eslint-plugin-jsx-a11y": "^6.2.3",
  "eslint-plugin-react": "^7.18.0",
  "eslint-plugin-react-hooks": "^2.3.0"
},
```

And the complete configuration:

```yaml
parserOptions:
  ecmaVersion: 6

env:
  browser: true

extends:
  - airbnb-typescript
  - airbnb/hooks
  - plugin:@typescript-eslint/recommended

rules:
  react/react-in-jsx-scope: off
```

There are no specific settings for the React + TypeScript combo to
my knowledge. Components are just functions (or classes, if you are
old-school :p) so the TypeScript linting just deals with them as
such. Therefore I can not recommend more documentation to you!
