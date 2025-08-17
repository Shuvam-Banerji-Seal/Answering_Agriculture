// IndicAgri Service Worker for Offline Functionality
const CACHE_NAME = 'indicagri-v1.0.0';
const STATIC_CACHE_NAME = 'indicagri-static-v1';
const DYNAMIC_CACHE_NAME = 'indicagri-dynamic-v1';

// Files to cache for offline use
const STATIC_FILES = [
  '/',
  '/static/css/main.css',
  '/static/css/responsive.css', 
  '/static/js/app.js',
  '/static/js/speech.js',
  '/static/manifest.json',
  // Add your essential static files
];

// API endpoints to cache responses
const CACHEABLE_APIS = [
  '/api/v1/query',
  '/health'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {
        console.log('📦 Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Cache installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker activated');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE_NAME && cacheName !== DYNAMIC_CACHE_NAME) {
            console.log('🗑️ Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleAPIRequest(request));
    return;
  }
  
  // Handle static files
  if (STATIC_FILES.some(file => url.pathname === file)) {
    event.respondWith(handleStaticRequest(request));
    return;
  }
  
  // Handle other requests
  event.respondWith(handleOtherRequests(request));
});

// API request handler - Cache-first for better performance
async function handleAPIRequest(request) {
  const cache = await caches.open(DYNAMIC_CACHE_NAME);
  
  try {
    // Try network first for fresh data
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    console.log('📡 Network failed, trying cache...');
    
    // Fallback to cache
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log('💾 Serving from cache');
      return cachedResponse;
    }
    
    // Return offline response for queries
    if (request.url.includes('/api/v1/query')) {
      return new Response(
        JSON.stringify({
          answer: "आप ऑफ़लाइन हैं। इंटरनेट कनेक्शन वापस आने पर कृपया दोबारा कोशिश करें।",
          sources: [],
          confidence: 0.0,
          offline: true
        }),
        {
          headers: { 'Content-Type': 'application/json' },
          status: 200
        }
      );
    }
    
    throw error;
  }
}

// Static file handler - Cache-first strategy
async function handleStaticRequest(request) {
  const cache = await caches.open(STATIC_CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.error('Failed to fetch static file:', request.url);
    throw error;
  }
}

// Other requests handler
async function handleOtherRequests(request) {
  try {
    return await fetch(request);
  } catch (error) {
    const cache = await caches.open(STATIC_CACHE_NAME);
    return cache.match('/') || new Response('Offline');
  }
}

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  console.log('🔄 Background sync triggered');
  // Handle queued requests when back online
}

// Push notification handling (for future use)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    
    const options = {
      body: data.body,
      icon: '/static/images/icons/icon-192x192.png',
      badge: '/static/images/icons/icon-72x72.png',
      vibrate: [200, 100, 200],
      data: data,
      actions: [
        {
          action: 'open',
          title: 'खोलें',
          icon: '/static/images/icons/open-icon.png'
        },
        {
          action: 'close',
          title: 'बंद करें',
          icon: '/static/images/icons/close-icon.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});
