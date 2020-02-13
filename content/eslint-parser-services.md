---
title: ESLint: a value for <code>parserOptions.project</code>
slug: eslint-parser-services
date: 13/02/2020
description: How to fix? Error while loading rule '@typescript-eslint/no-implied-eval': You have used a rule which requires parserServices to be generated.
---

A few days ago, the [`eslint-config-airbnb-typescript`](https://github.com/iamturns/eslint-config-airbnb-typescript)
project updated from `6.3.2` to `7.0.0`. It is an important upgrade, as the
project now supports the latest TypeScript version. Amongst other things, it
means that we won't have to deal with [this warning](https://github.com/iamturns/eslint-config-airbnb-typescript/issues/53) anymore.

However, if you followed my [ESLint guide](/eslint-guide), this update will most likely
break your configuration. The reason is that two breaking changes were introduced
in this `7.0.0` realease.

First, `@typescript-eslint/eslint-plugin` must be upgraded to `2.19.0`. For
example:

```
npm install @typescript-eslint/eslint-plugin@^2.19.0 --save-dev
```

Then, you must set the [`parserOptions.project`](https://github.com/typescript-eslint/typescript-eslint/tree/master/packages/parser#parseroptionsproject) attribute
in your ESLint configuration. The reason for that is that some new rules
which require type information were introduced and they need to know where
your `tsconfig.json` file is in order to work properly.

I'm quite suprised that this attribute does not have `tsconfig.json` or, more
explicitely, `./tsconfig.json` as a default but anyway, here is how to fix it
in a YAML configuration:

```yaml
parserOptions:
  ecmaVersion: 6
  project: tsconfig.json
```

In case you don't already have a `tsconfig.json` file, here is how you can
generate a *default* one, providing that `typescript` is already a local
dependency of the project:

```
npx tsc --init
```

Related links:

* [Pull request with breaking changes](https://github.com/iamturns/eslint-config-airbnb-typescript/pull/63)
* [7.0.0 release](https://github.com/iamturns/eslint-config-airbnb-typescript/releases/tag/v7.0.0)