module.exports.end = () => {
  hljs.configure({languages: []}); // Do not try to guess the language
  hljs.initHighlightingOnLoad(); // Highlight code

  // Already loaded in the header, let's run it
  window.observer.observe(); // Lazy loading

  // Google Analytics
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push('js', new Date());
  window.dataLayer.push('config', 'UA-155297229-1');
};