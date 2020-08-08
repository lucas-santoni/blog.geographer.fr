/* global API */

const levenshtein = require('js-levenshtein');

const URLSplit = window.location.href.split('/');
const last = URLSplit[URLSplit.length - 1].replace('.html', '');

const distances = API.map(({ title, slug }) => ({
  title,
  slug,
  score: levenshtein(last, slug),
}));
const sorted = distances.sort((a, b) => a.score - b.score);
const results = sorted.slice(0, 5);

const ul = document.createElement('ul');

results.forEach(result => {
  const li = document.createElement('li');
  const a = document.createElement('a');

  a.href = `/${result.slug}`;
  a.innerHTML = result.title;
  li.appendChild(a);

  ul.appendChild(li);
});

const wrapper = document.getElementById('search-result');
wrapper.firstChild.replaceWith(ul);
