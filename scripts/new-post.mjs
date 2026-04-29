#!/usr/bin/env node
import { writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const POSTS = join(HERE, '..', 'src', 'content', 'posts');

const title = process.argv.slice(2).join(' ').trim();
if (!title) {
  console.error('Usage: npm run new "Post title"');
  process.exit(1);
}

const slug = title
  .toLowerCase()
  .normalize('NFKD')
  .replace(/[̀-ͯ]/g, '')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const today = new Date().toISOString().slice(0, 10);
const fm = `---
title: ${JSON.stringify(title)}
slug: ${slug}
date: ${today}
description: ""
---

Write your post here. Markdown is supported.
`;

if (!existsSync(POSTS)) mkdirSync(POSTS, { recursive: true });
const path = join(POSTS, `${slug}.md`);
if (existsSync(path)) {
  console.error(`Already exists: ${path}`);
  process.exit(1);
}
writeFileSync(path, fm);
console.log(`Created ${path}`);
