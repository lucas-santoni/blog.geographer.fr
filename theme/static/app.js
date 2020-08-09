const twemoji = require('twemoji');
const lozad = require('lozad');
const hljs = require('highlight.js');
const toast = require('toastify-js');

// This function will run for every page once loaded (script is deffered)
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

// Helper function to notify user that a new version of a page is available
window.newVersionToast = () => {
  toast({
    text:
      'A new version of this page is available! <a href="#">Click to refresh!</a>',
    duration: -1,
    close: false,
    gravity: 'bottom',
    position: 'center',
    offset: { y: '1em' },
    stopOnFocus: true,
    onClick: () => window.location.reload(),
  }).showToast();
};
