const levenshtein = require('js-levenshtein');

module.exports.fill404 = () => {
  const url_split = window.location.href.split("/");
  const last = url_split[url_split.length - 1].replace('.html', '');

  const distances = API.map(({ title, slug }) => ({ title, slug, score: levenshtein(last, slug) }));
  const sorted = distances.sort((a, b) => a.score - b.score);
  const results = sorted.slice(0, 5);

  const ul = document.createElement('ul');

  for (const r of results) {
    const li = document.createElement('li');
    const a = document.createElement('a');

    a.href = `/${ r.slug }`;
    a.innerHTML = r.title;
    li.appendChild(a);

    ul.appendChild(li);
  }

  const wrapper = document.getElementById("search-result");
  wrapper.firstChild.replaceWith(ul);
};