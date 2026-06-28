const CACHE = 'ehealth-mw-v1';
const ASSETS = [
  '/',
  '/index.html',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // API calls — network-first with offline fallback
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(networkFirst(e.request));
    return;
  }

  // Static assets — cache-first
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request).then(resp => {
      const clone = resp.clone();
      caches.open(CACHE).then(c => c.put(e.request, clone));
      return resp;
    })).catch(() => new Response('Offline', { status: 503 }))
  );
});

async function networkFirst(request) {
  try {
    const resp = await fetch(request);
    const clone = resp.clone();
    caches.open(CACHE).then(c => {
      const key = new Request(request.url, { method: 'GET' });
      if (request.method === 'GET') c.put(key, clone);
    });
    return resp;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(JSON.stringify({ offline: true, error: 'No network' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
