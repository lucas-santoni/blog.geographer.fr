// Kill-switch for the old Workbox service worker shipped by the Pelican
// version of this blog. Visitors who installed it once still have it active
// in their browser; this script unregisters it and clears its caches the
// next time their browser checks for SW updates. Keep this file deployed
// indefinitely — it's tiny and harmless for visitors who never had the old
// SW.

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
      await self.registration.unregister();
      const clients = await self.clients.matchAll({ type: 'window' });
      for (const client of clients) {
        if ('navigate' in client) {
          client.navigate(client.url);
        }
      }
    })()
  );
});
