const CACHE_NAME = 'swamini-panchang-v4';
const ASSETS_TO_CACHE = [
  '/dashboard/',
  '/static/css/style.css',
  '/static/images/Swamini App.jpg',
  '/static/images/Swamini Banner.jpg',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install Event - cache core shell resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[Service Worker] Caching App Shell and Dependencies');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate Event - clean up old caches instantly
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keyList => {
      return Promise.all(keyList.map(key => {
        if (key !== CACHE_NAME) {
          console.log('[Service Worker] Removing old cache', key);
          return caches.delete(key);
        }
      }));
    }).then(() => self.clients.claim())
  );
});

// Fetch Event - Network-First for dynamic pages, Stale-While-Revalidate for static assets
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  if (!url.protocol.startsWith('http')) return;

  // Identify static assets
  const isStaticAsset = url.pathname.startsWith('/static/') || 
                       url.hostname.includes('cdn') || 
                       url.hostname.includes('cdnjs') ||
                       url.pathname === '/manifest.json';

  if (isStaticAsset) {
    // Stale-While-Revalidate for static files
    event.respondWith(
      caches.match(event.request)
        .then(cachedResponse => {
          const fetchPromise = fetch(event.request).then(networkResponse => {
            if (networkResponse && networkResponse.status === 200) {
              caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, networkResponse.clone());
              });
            }
            return networkResponse;
          }).catch(err => console.log('[Service Worker] Static background fetch failed: ', err));

          return cachedResponse || fetchPromise;
        })
    );
  } else {
    // Network-First for dynamic HTML/routes
    event.respondWith(
      fetch(event.request)
        .then(networkResponse => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          // If offline, retrieve from cache
          return caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // If offline and navigate request, fallback to dashboard
            if (event.request.mode === 'navigate') {
              return caches.match('/dashboard/');
            }
          });
        })
    );
  }
});
