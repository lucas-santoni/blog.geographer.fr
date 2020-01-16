const SW_PATH = '/service-worker.js';

const CACHE_COMMON = 'common';
const CACHE_PAGES = 'pages';
const CACHE_VERSION = '7::';

const DEBUG = false;

const NO_INTERNET_PAGE = '/internet-error';
const URLS_TO_CACHE = [
  '/',
  NO_INTERNET_PAGE,
  '/404',
  '/theme/avatar.jpg',
  '/theme/mobile.css',
  '/theme/pygments.css',
  '/theme/styles.css',
  '/theme/fonts/iosevka-bold.woff2',
  '/theme/fonts/iosevka-bolditalic.woff2',
  '/theme/fonts/iosevka-italic.woff2',
  '/theme/fonts/iosevka-regular.woff2',
  '/theme/fonts/merriweather-bold.ttf',
  '/theme/fonts/merriweather-bolditalic.ttf',
  '/theme/fonts/merriweather-italic.ttf',
  '/theme/fonts/merriweather-light.ttf',
  '/theme/fonts/merriweather-regular.ttf'
];

const log = msg => {
  if (!DEBUG) {
    return;
  }

  console.log(`[service-worker] ${msg}`);
};

const logerr = (msg, err) => {
  if (!DEBUG) {
    return;
  }

  console.error(`[service-worker] ${msg}`);
  console.error(err);
};

const fetchedFromNetwork = (response, event) => {
  const cacheCopy = response.clone();
  log(`fetching response from network @ ${event.request.url}`);

  caches
    .open(CACHE_VERSION + CACHE_PAGES)
    .then(cache => cache.put(event.request, cacheCopy))
    .then(() => log(`response stored in cache @ ${event.request.url}`));

  return response;
};

const unableToResolve = () => {
  return Response.redirect(NO_INTERNET_PAGE, 302);
};

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register(SW_PATH)
      .then(() => log('registered'))
      .catch(err => logerr('registration failed', err))
  })
}

self.addEventListener('install', event => {
  event.waitUntil(
    caches
      .open(CACHE_VERSION + CACHE_COMMON)
      .then(cache => cache.addAll(URLS_TO_CACHE))
      .then(() => log('installation completed, cached common'))
      .catch(e => logerr('installation failed', e))
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') {
    return;
  }

  if (event.request.url.match('^.*\.(google-analytics|googletagmanager)\.com.*$')) {
    return;
  }

  event.respondWith(
    caches
      .match(event.request)
      .then(cached => {
        const networked = fetch(event.request)
          .then(response => fetchedFromNetwork(response, event), unableToResolve)
          .catch(unableToResolve);


        log(`fetch event ${cached ? '(cached)' : '(network)'} @ ${event.request.url}`)
        return cached || networked;
      })
  );
});

self.addEventListener('activate', event => {
  log('activate');

  const cacheWhitelist = [
    CACHE_VERSION + CACHE_COMMON,
    CACHE_VERSION + CACHE_PAGES
  ];

  event.waitUntil(
    caches.keys().then(cacheNames => Promise.all(
      cacheNames.map(cacheName => {
        if (cacheWhitelist.indexOf(cacheName) === -1) {
          log(`delete ${cacheName}`);
          return caches.delete(cacheName);
        }
      })
    ))
  )
});
