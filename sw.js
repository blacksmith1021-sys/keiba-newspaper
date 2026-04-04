// Service Worker for 競馬ファクター新聞
// キャッシュ対象: 静的ファイルのみ（IndexedDBのデータには触れない）
const CACHE_NAME = 'keiba-v2.8.0';
const CACHE_FILES = [
  '/keiba-newspaper/',
  '/keiba-newspaper/index.html'
];

// インストール時: 静的ファイルをキャッシュ
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CACHE_FILES))
      .then(() => self.skipWaiting())
  );
});

// アクティベート時: 古いキャッシュを削除
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// フェッチ時: キャッシュ優先、なければネットワーク（Network Fallback）
self.addEventListener('fetch', (e) => {
  // API呼び出し（Gist同期等）はキャッシュしない
  if (e.request.url.includes('api.github.com')) return;
  // Google Fonts等の外部リソースはキャッシュしない
  if (!e.request.url.startsWith(self.location.origin)) return;

  e.respondWith(
    caches.match(e.request).then(cached => {
      // キャッシュがあればそれを返しつつ、バックグラウンドで更新
      const fetchPromise = fetch(e.request).then(response => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return response;
      }).catch(() => cached); // オフライン時はキャッシュにフォールバック

      return cached || fetchPromise;
    })
  );
});

// 新バージョン検知時にクライアントに通知
self.addEventListener('message', (e) => {
  if (e.data === 'skipWaiting') self.skipWaiting();
});
