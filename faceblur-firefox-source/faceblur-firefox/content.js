'use strict';

(() => {
  const api = typeof browser !== 'undefined' ? browser : chrome;
  const state = {
    enabled: true,
    blur: 18,
    threshold: 0.45,
    maskScale: 1.35,
    maxDimension: 416,
    modelReady: false,
    queue: [],
    queued: new WeakSet(),
    processing: false,
    overlays: new Map(),
  };

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  async function loadSettings() {
    const saved = await api.storage.local.get({
      enabled: true,
      blur: 18,
      threshold: 0.45,
      maskScale: 1.35,
      maxDimension: 416,
    });
    Object.assign(state, saved);
  }

  async function loadModel() {
    const modelUri = api.runtime.getURL('models');
    await faceapi.nets.tinyFaceDetector.loadFromUri(modelUri);
    state.modelReady = true;
  }

  function isVisible(el) {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width >= 48 && r.height >= 48 && s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity) !== 0;
  }

  function candidates(root = document) {
    const result = [...root.querySelectorAll?.('img, video, canvas') || []];
    const all = root.querySelectorAll?.('*') || [];
    for (const el of all) {
      const bg = getComputedStyle(el).backgroundImage;
      if (bg && bg !== 'none' && /^url\(/.test(bg)) result.push(el);
    }
    return result;
  }

  function enqueue(el) {
    if (!state.enabled || !state.modelReady || state.queued.has(el) || !isVisible(el)) return;
    state.queued.add(el);
    state.queue.push(el);
    drain();
  }

  async function drain() {
    if (state.processing) return;
    state.processing = true;
    while (state.queue.length) {
      const el = state.queue.shift();
      state.queued.delete(el);
      try { await processElement(el); } catch (e) { /* unsupported media is skipped */ }
      await sleep(20);
    }
    state.processing = false;
  }

  function getBackgroundUrl(el) {
    const value = getComputedStyle(el).backgroundImage;
    const match = value.match(/^url\(["']?(.*?)["']?\)$/);
    return match?.[1] || null;
  }

  async function loadImageSource(url) {
    if (!url) throw new Error('No image URL');
    if (url.startsWith('data:') || url.startsWith('blob:')) return url;
    const reply = await api.runtime.sendMessage({ type: 'FACEBLUR_FETCH_IMAGE', url });
    if (!reply?.ok) throw new Error(reply?.error || 'Fetch failed');
    return reply.dataUrl;
  }

  async function sourceCanvas(el) {
    const rect = el.getBoundingClientRect();
    const scale = Math.min(1, state.maxDimension / Math.max(rect.width, rect.height));
    const width = Math.max(32, Math.round(rect.width * scale));
    const height = Math.max(32, Math.round(rect.height * scale));
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });

    if (el instanceof HTMLImageElement) {
      const src = await loadImageSource(el.currentSrc || el.src);
      const img = new Image();
      img.src = src;
      await img.decode();
      ctx.drawImage(img, 0, 0, width, height);
    } else if (el instanceof HTMLVideoElement || el instanceof HTMLCanvasElement) {
      ctx.drawImage(el, 0, 0, width, height);
    } else {
      const src = await loadImageSource(getBackgroundUrl(el));
      const img = new Image();
      img.src = src;
      await img.decode();
      ctx.drawImage(img, 0, 0, width, height);
    }
    return { canvas, scale };
  }

  function removeOverlay(el) {
    const item = state.overlays.get(el);
    if (item) item.root.remove();
    state.overlays.delete(el);
  }

  function renderMasks(el, boxes) {
    removeOverlay(el);
    if (!boxes.length || !state.enabled) return;
    const root = document.createElement('div');
    root.className = 'faceblur-overlay-root';
    root.dataset.faceblur = 'true';
    document.documentElement.appendChild(root);

    const update = () => {
      if (!el.isConnected || !state.enabled) return removeOverlay(el);
      const r = el.getBoundingClientRect();
      root.style.left = `${r.left + scrollX}px`;
      root.style.top = `${r.top + scrollY}px`;
      root.style.width = `${r.width}px`;
      root.style.height = `${r.height}px`;
    };

    for (const box of boxes) {
      const mask = document.createElement('div');
      mask.className = 'faceblur-face-mask';
      mask.style.setProperty('--faceblur-strength', `${state.blur}px`);
      mask.style.left = `${box.x * 100}%`;
      mask.style.top = `${box.y * 100}%`;
      mask.style.width = `${box.width * 100}%`;
      mask.style.height = `${box.height * 100}%`;
      root.appendChild(mask);
    }
    update();
    state.overlays.set(el, { root, update });
  }

  async function processElement(el) {
    if (!isVisible(el) || !state.enabled) return removeOverlay(el);
    if (el instanceof HTMLImageElement && !el.complete) {
      el.addEventListener('load', () => enqueue(el), { once: true });
      return;
    }
    if (el instanceof HTMLVideoElement && el.readyState < 2) return;

    const rect = el.getBoundingClientRect();
    const { canvas } = await sourceCanvas(el);
    const detections = await faceapi.detectAllFaces(
      canvas,
      new faceapi.TinyFaceDetectorOptions({ inputSize: 416, scoreThreshold: state.threshold })
    );

    const boxes = detections.map(({ box }) => {
      const cx = (box.x + box.width / 2) / canvas.width;
      const cy = (box.y + box.height / 2) / canvas.height;
      const w = Math.min(1, (box.width / canvas.width) * state.maskScale);
      const h = Math.min(1, (box.height / canvas.height) * state.maskScale);
      return {
        x: Math.max(0, Math.min(1 - w, cx - w / 2)),
        y: Math.max(0, Math.min(1 - h, cy - h / 2)),
        width: w,
        height: h,
      };
    });
    if (rect.width && rect.height) renderMasks(el, boxes);
  }

  function scan(root = document) {
    for (const el of candidates(root)) enqueue(el);
  }

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (!(node instanceof Element)) continue;
        if (node.matches?.('img, video, canvas')) enqueue(node);
        scan(node);
      }
    }
  });

  const reposition = () => {
    for (const { update } of state.overlays.values()) update();
  };

  api.runtime.onMessage.addListener(async (message) => {
    if (message?.type === 'FACEBLUR_SETTINGS') {
      Object.assign(state, message.settings);
      if (!state.enabled) {
        for (const el of [...state.overlays.keys()]) removeOverlay(el);
      } else scan();
      return { ok: true };
    }
    if (message?.type === 'FACEBLUR_RESCAN') {
      scan();
      return { ok: true };
    }
    return undefined;
  });

  (async () => {
    await loadSettings();
    await loadModel();
    scan();
    observer.observe(document.documentElement, { childList: true, subtree: true });
    addEventListener('scroll', reposition, { passive: true });
    addEventListener('resize', reposition, { passive: true });
    setInterval(() => {
      reposition();
      document.querySelectorAll('video').forEach(enqueue);
    }, 1500);
  })().catch(console.error);
})();
