const SW_PATH = '/service-worker.js';

const CACHE_NAME = 'cache';
const CACHE_VERSION = '1::';

const URLS_TO_CACHE = [
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
  console.log(`[service-worker] ${msg}`);
};

const logerr = (msg, err) => {
  console.error(`[service-worker] ${msg}`);
  console.error(err);
};

const fetchedFromNetwork = (response, event) => {
  const cacheCopy = response.clone();
  log(`fetching response from network @ ${event.request.url}`);

  caches
    .open(CACHE_VERSION + 'pages')
    .then(cache => cache.put(event.request, cacheCopy))
    .then(() => console.log(`response stored in cache @ ${event.request.url}`));

  return response;
};

const unableToResolve = (err, url) => {
  logerr(`request failed in both cache, and network @ ${url}`, err);

  // TODO: Fix this
  return new Response('<h1>Service Unavailable</h1>', {
    status: 503,
    statusText: 'Service Unavailable',
    headers: new Headers({
      'Content-Type': 'text/html'
    })
  });
};

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register(SW_PATH);
} else {
  logerr('not supported', new Error('/'));
}

self.addEventListener('install', event => {
  event.waitUntil(
    caches
      .open(CACHE_VERSION + 'common')
      .then(cache => cache.addAll(URLS_TO_CACHE))
      .then(() => log('installation completed, cached common'))
      .catch(e => logerr('installation failed', e))
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches
      .match(event.request)
      .then(cached => {
        const networked = fetch(event.request)
          .then(response => fetchedFromNetwork(response, event))
          .catch(error => unableToResolve(error, event.request.url));


        log(`fetch event ${cached ? '(cached)' : '(network)'} @ ${event.request.url}`)
        return cached || networked;
      })
  );
});