// Service worker: deja instalar la app y abrirla sin señal.
// La app (index.html, config, íconos) va primero a la red y, si no hay
// señal, sale de la copia. Los SDK de Firebase salen de la copia (versión
// fija). Los datos de Firebase NUNCA pasan por acá: la copia local de datos
// la maneja index.html (por usuario, y se borra al cerrar sesión).
const CACHE = 'plataforma-v1';
const SDK = [
  'https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js',
  'https://www.gstatic.com/firebasejs/9.23.0/firebase-auth-compat.js',
  'https://www.gstatic.com/firebasejs/9.23.0/firebase-database-compat.js',
];
const APP = ['./', './index.html', './manifest.json', './config/club.json', './config/firebase.js', './icons/icon-192.png', './icons/icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE)
    .then(c => Promise.allSettled([...APP, ...SDK].map(u => c.add(u))))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if(req.method !== 'GET') return;
  const url = new URL(req.url);
  if(SDK.includes(req.url)){
    e.respondWith(caches.match(req).then(r => r || fetch(req)));
    return;
  }
  if(url.origin !== location.origin || url.pathname.includes('/data/')) return;
  e.respondWith(
    fetch(req).then(resp => {
      if(resp.ok){ const copia = resp.clone(); caches.open(CACHE).then(c => c.put(req, copia)); }
      return resp;
    }).catch(() => caches.match(req, {ignoreSearch: true}).then(r => r || caches.match('./index.html')))
  );
});
