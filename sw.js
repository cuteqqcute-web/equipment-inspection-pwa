/* ============================================================
   設備巡檢 PWA — Service Worker（離線快取策略）
   版本: 1.0.0
   最後更新: 2026-07-06
   ============================================================
   重要：修改 sw.js 後請務必遞增 CACHE_NAME 版本號（如下方 v1→v2），
   否則瀏覽器可能不重新下載靜態資源。
   ============================================================ */

// [CFO] 低維護：每次修改 sw.js 時遞增此版本號，確保用戶取得最新資源
const CACHE_NAME = 'equipment-inspection-v2';
const STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.json',
];

// ===== 安裝階段：預載靜態資源 =====
self.addEventListener('install', (event) => {
  console.log('[SW] 安裝中...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).then(() => {
        console.log('[SW] 靜態資源快取完成');
      });
    }).catch((err) => {
      console.warn('[SW] 部分資源快取失敗（可能離線安裝）:', err);
      // 即使快取失敗也繼續，讓 SW 啟用
    })
  );
  // 立即啟用，不等舊 SW 關閉
  self.skipWaiting();
});

// ===== 啟用階段：清除舊快取 =====
self.addEventListener('activate', (event) => {
  console.log('[SW] 已啟用');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[SW] 清除舊快取:', name);
            return caches.delete(name);
          })
      );
    }).then(() => {
      // 控制所有未控制的客戶端
      return self.clients.claim();
    })
  );
});

// ===== 請求攔截：快取策略 =====
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  const path = url.pathname;

  // 照片 blob 請求（格式：photo_{id}）
  if (path.startsWith('/photo_') || url.pathname.includes('photo_')) {
    event.respondWith(servePhoto(event.request));
    return;
  }

  // 靜態資源：Cache First
  if (isStaticAsset(path)) {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // 其他請求（如 devices.json 更新）：Network First
  event.respondWith(networkFirst(event.request));
});

// ===== 快取策略實作 =====

/**
 * Cache First 策略：離線優先，網路更新背景進行
 */
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    // 有快取就回傳，同時背景更新
    fetchAndUpdateCache(request);
    return cached;
  }

  // 無快取時從網路載入
  try {
    const response = await fetch(request);
    if (response.ok) {
      await updateCache(request, response.clone());
    }
    return response;
  } catch (err) {
    console.warn('[SW] 離線且無快取:', request.url);
    return new Response('離線模式：請連線後重新載入', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

/**
 * Network First 策略：優先從網路載入，離線時 fallback 到快取
 */
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      await updateCache(request, response.clone());
    }
    return response;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    console.warn('[SW] 離線且無快取（network first）:', request.url);
    return new Response('離線模式', { status: 503 });
  }
}

/**
 * 照片 blob 處理：從快取讀取
 */
async function servePhoto(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  // 嘗試匹配 key name（去除路徑前綴）
  const key = request.url.split('/').pop().split('?')[0];
  const cache = await caches.open(CACHE_NAME);
  const keys = await cache.keys();
  for (const req of keys) {
    if (req.url.includes(key)) {
      return cache.match(req);
    }
  }

  return new Response('照片未找到', { status: 404 });
}

// ===== 輔助函式 =====

/**
 * 判斷是否為靜態資源
 */
function isStaticAsset(path) {
  const assets = [
    '/index.html',
    '/manifest.json',
    '/sw.js'
  ];
  // 直接比對或開頭比對
  return assets.some(asset =>
    path === asset ||
    path.endsWith(asset)
  );
}

/**
 * 從網路抓取並更新快取（背景執行，不阻塞回應）
 */
async function fetchAndUpdateCache(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      await updateCache(request, response.clone());
    }
  } catch (e) {
    // 離線時安靜失敗
  }
}

/**
 * 更新快取（如果請求是 GET）
 */
async function updateCache(request, response) {
  if (request.method !== 'GET') return;
  try {
    const cache = await caches.open(CACHE_NAME);
    await cache.put(request, response);
  } catch (e) {
    console.warn('[SW] 快取更新失敗:', request.url);
  }
}

// ===== 訊息處理 =====
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
  if (event.data === 'clearPhotoCache') {
    caches.open(CACHE_NAME).then(cache => {
      cache.keys().then(keys => {
        keys.forEach(req => {
          if (req.url.includes('photo_')) {
            cache.delete(req);
          }
        });
      });
    });
  }
});
