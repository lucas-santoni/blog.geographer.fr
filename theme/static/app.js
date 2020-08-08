const twemoji = require('twemoji');
const lozad = require('lozad');
const hljs = require('highlight.js');

// This function will run for every page
const common = () => {
  // Highlight.js
  // Highlight source code snippets
  hljs.configure({ languages: [] }); // Do not try to guess the language
  hljs.initHighlightingOnLoad(); // Highlight code

  // Lozad
  // Lazy load images (when they enter the viewport)
  window.observer = lozad();
  window.observer.observe(); // Lazy loading

  // Twemoji
  // Consistent display for emojis
  twemoji.parse(document.body);
};

common();
