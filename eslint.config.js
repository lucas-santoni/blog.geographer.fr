import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import astro from 'eslint-plugin-astro'
import globals from 'globals'

const styleRules = {
  semi: ['error', 'never', { beforeStatementContinuationChars: 'always' }],
  quotes: ['error', 'single', { avoidEscape: true, allowTemplateLiterals: true }],
}

export default [
  {
    ignores: ['dist/**', '.astro/**', '.vercel/**', 'node_modules/**'],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...astro.configs.recommended,
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      ...styleRules,
      '@typescript-eslint/semi': 'off',
      '@typescript-eslint/quotes': 'off',
    },
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    rules: {
      ...styleRules,
    },
  },
  {
    files: ['**/*.astro'],
    rules: {
      ...styleRules,
    },
  },
]
