'use strict';

(() => {
  const api = typeof browser !== 'undefined' ? browser : chrome;
  const DEFAULTS = Object.freeze({
    enabled: true,
    blur: 18,
    threshold: 0.45,
    maskScale: 1.35,
    scanSize: 416,
    disabledHosts: []
  });

  const state = {
    ...DEFAULTS,
    modelReady: false,
    modelError: '',
    processing: false,
    queue: [],
    queued: new WeakSet(),
    observed: new WeakSet(),
    overlays: new Map(),
    cache: new Map(),
    mediaCount: 0,
    faceCount: 0,
    videoTimer: 0,
    resizeTimer: 0
  };

  const intersection = new IntersectionObserver((entries) => {
    for (const entry of entries) if (entry.isIntersecting) enqueue(entry.target);
  }, { rootMargin: '350px', threshold: 0.01 });

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const idle = () => new Promise((resolve) => {
    if ('requestIdleCallback' in window) requestIdleCallback(resolve, { timeout: 250 });
    else setTimeout(resolve, 0);
  });

  function normalizeSettings(raw = {}) {
    const number = (key) => Number.isFinite(Number(raw[key])) ? Number(raw[key]) : DEFAULTS[key];
    return {
      enabled: typeof raw.enabled === 'boolean' ? raw.enabled : DEFAULTS.enabled,
      blur: number('blur'),
      threshold: number('threshold'),
      maskScale: number('maskScale'),
      scanSize: number('scanSize'),
      disabledHosts: Array.isArray(raw.disabledHosts) ? raw.disabledHosts.filter(Boolean) : []
    };
  }

  function siteEnabled() {
    return state.enabled && !state.disabledHosts.includes(location.hostname);
  }

  async function loadSettings() {
    Object.assign(state, normalizeSettings(await api.storage.local.get(DEFAULTS)));
  }

  async function loadModel() {
    try {
      await faceapi.nets.tinyFaceDetector.loadFromUri(api.runtime.getURL('models/'));
      state.modelReady = true;
    } catch (error) {
      state.modelError = /NetworkError|fetch/i.test(String(error?.message || error)) ? 'Detector files are missing. Run vendor.cmd, then reload the add-on.' : String(error?.message || error);
      throw error;
    }
  }

  function isMedia(el) {
    return el instanceof HTMLImageElement || el instanceof HTMLVideoElement || el instanceof HTMLCanvasElement || Boolean(backgroundUrl(el));
  }

  function isVisible(el) {
    if (!el?.isConnected) return false;
    const rect = el.getBoundingClientRect();
    if (rect.width < 40 || rect.height < 40) return false;
    const style = getComputedStyle(el);
    return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0;
  }

  function backgroundUrl(el) {
    if (!(el instanceof Element) || el.dataset?.faceblur === 'true') return '';
    const value = getComputedStyle(el).backgroundImage;
    if (!value || value === 'none') return '';
    const match = value.match(/url\((?:"|')?(.*?)(?:"|')?\)/i);
    return match?.[1] || '';
  }

  function mediaCandidates(root = document) {
    const found = new Set();
    if (root instanceof Element && isMedia(root)) found.add(root);
    const elements = root.querySelectorAll?.('img,video,canvas,*[style*="background"],*[class]') || [];
    for (const el of elements) {
      if (el.matches?.('img,video,canvas') || backgroundUrl(el)) found.add(el);
    }
    return found;
  }

  function observe(el) {
    if (state.observed.has(el)) return;
    state.observed.add(el);
    intersection.observe(el);
    state.mediaCount += 1;
  }

  function scan(root = document) {
    for (const el of mediaCandidates(root)) observe(el);
  }

  function enqueue(el, force = false) {
    if (!siteEnabled() || !state.modelReady || !isVisible(el) || state.queued.has(el)) return;
    state.queued.add(el);
    state.queue.push({ el, force });
    drain();
  }

  async function drain() {
    if (state.processing) return;
    state.processing = true;
    while (state.queue.length) {
      const { el, force } = state.queue.shift();
      state.queued.delete(el);
      try {
        await idle();
        await processElement(el, force);
      } catch (_) {
        removeOverlay(el);
      }
      await sleep(12);
    }
    state.processing = false;
  }

  async function fetchImage(url) {
    if (!url) throw new Error('Missing image URL');
    if (/^(data:|blob:)/i.test(url)) return url;
    const reply = await api.runtime.sendMessage({ type: 'FACEBLUR_FETCH_IMAGE', url });
    if (!reply?.ok) throw new Error(reply?.error || 'Image fetch failed');
    return reply.dataUrl;
  }

  async function decodedImage(url) {
    const img = new Image();
    img.decoding = 'async';
    img.src = await fetchImage(url);
    if (img.decode) await img.decode();
    else await new Promise((resolve, reject) => { img.onload = resolve; img.onerror = reject; });
    return img;
  }

  function sourceIdentity(el) {
    if (el instanceof HTMLImageElement) return `img:${el.currentSrc || el.src}|${el.naturalWidth}x${el.naturalHeight}`;
    if (el instanceof HTMLCanvasElement) return `canvas:${el.width}x${el.height}:${Math.floor(performance.now() / 3000)}`;
    if (el instanceof HTMLVideoElement) return `video:${el.currentSrc || el.src}|${el.videoWidth}x${el.videoHeight}:${Math.floor(el.currentTime * 2)}`;
    return `bg:${backgroundUrl(el)}`;
  }

  async function renderSource(el) {
    let source;
    let sourceWidth;
    let sourceHeight;

    if (el instanceof HTMLImageElement) {
      if (!el.complete || !el.naturalWidth) throw new Error('Image not ready');
      source = await decodedImage(el.currentSrc || el.src);
      sourceWidth = source.naturalWidth;
      sourceHeight = source.naturalHeight;
    } else if (el instanceof HTMLVideoElement) {
      if (el.readyState < 2 || !el.videoWidth) throw new Error('Video not ready');
      source = el;
      sourceWidth = el.videoWidth;
      sourceHeight = el.videoHeight;
    } else if (el instanceof HTMLCanvasElement) {
      if (!el.width || !el.height) throw new Error('Canvas is empty');
      source = el;
      sourceWidth = el.width;
      sourceHeight = el.height;
    } else {
      source = await decodedImage(backgroundUrl(el));
      sourceWidth = source.naturalWidth;
      sourceHeight = source.naturalHeight;
    }

    const longest = Math.max(sourceWidth, sourceHeight);
    const scale = Math.min(1, state.scanSize / longest);
    const width = Math.max(32, Math.round(sourceWidth * scale));
    const height = Math.max(32, Math.round(sourceHeight * scale));
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d', { alpha: false, willReadFrequently: true });
    ctx.drawImage(source, 0, 0, width, height);
    return { canvas, sourceWidth, sourceHeight };
  }

  function getFit(el) {
    const style = getComputedStyle(el);
    if (el instanceof HTMLImageElement || el instanceof HTMLVideoElement) {
      return { fit: style.objectFit || 'fill', position: style.objectPosition || '50% 50%' };
    }
    const size = style.backgroundSize || 'auto';
    const fit = size === 'cover' || size === 'contain' ? size : 'fill';
    return { fit, position: style.backgroundPosition || '50% 50%' };
  }

  function parsePosition(value) {
    const parts = String(value).trim().split(/\s+/);
    const parse = (part, fallback) => {
      if (!part) return fallback;
      if (part === 'left' || part === 'top') return 0;
      if (part === 'right' || part === 'bottom') return 1;
      if (part === 'center') return 0.5;
      if (part.endsWith('%')) return Math.max(0, Math.min(1, parseFloat(part) / 100));
      return fallback;
    };
    return [parse(parts[0], 0.5), parse(parts[1] || parts[0], 0.5)];
  }

  function mapBoxToElement(box, sourceWidth, sourceHeight, el) {
    const rect = el.getBoundingClientRect();
    const { fit, position } = getFit(el);
    let drawnWidth = rect.width;
    let drawnHeight = rect.height;

    if (fit === 'contain' || fit === 'cover') {
      const ratio = fit === 'contain'
        ? Math.min(rect.width / sourceWidth, rect.height / sourceHeight)
        : Math.max(rect.width / sourceWidth, rect.height / sourceHeight);
      drawnWidth = sourceWidth * ratio;
      drawnHeight = sourceHeight * ratio;
    }

    const [px, py] = parsePosition(position);
    const offsetX = (rect.width - drawnWidth) * px;
    const offsetY = (rect.height - drawnHeight) * py;
    const scaleX = drawnWidth / sourceWidth;
    const scaleY = drawnHeight / sourceHeight;

    const cx = (box.x + box.width / 2) * scaleX + offsetX;
    const cy = (box.y + box.height / 2) * scaleY + offsetY;
    const width = box.width * scaleX * state.maskScale;
    const height = box.height * scaleY * state.maskScale;

    return {
      x: (cx - width / 2) / rect.width,
      y: (cy - height / 2) / rect.height,
      width: width / rect.width,
      height: height / rect.height
    };
  }

  function removeOverlay(el) {
    const overlay = state.overlays.get(el);
    if (overlay) overlay.root.remove();
    state.overlays.delete(el);
    recalculateFaceCount();
  }

  function recalculateFaceCount() {
    let count = 0;
    for (const value of state.overlays.values()) count += value.boxes.length;
    state.faceCount = count;
  }

  function updateOverlay(el) {
    const overlay = state.overlays.get(el);
    if (!overlay) return;
    if (!el.isConnected || !siteEnabled() || !isVisible(el)) return removeOverlay(el);
    const rect = el.getBoundingClientRect();
    overlay.root.style.left = `${rect.left}px`;
    overlay.root.style.top = `${rect.top}px`;
    overlay.root.style.width = `${rect.width}px`;
    overlay.root.style.height = `${rect.height}px`;
    for (const mask of overlay.root.children) mask.style.setProperty('--faceblur-strength', `${state.blur}px`);
  }

  function renderMasks(el, boxes) {
    removeOverlay(el);
    if (!boxes.length || !siteEnabled()) return;
    const root = document.createElement('div');
    root.className = 'faceblur-overlay-root';
    root.dataset.faceblur = 'true';
    for (const box of boxes) {
      const x = Math.max(0, box.x);
      const y = Math.max(0, box.y);
      const width = Math.min(1 - x, box.width);
      const height = Math.min(1 - y, box.height);
      if (width <= 0 || height <= 0) continue;
      const mask = document.createElement('div');
      mask.className = 'faceblur-face-mask';
      mask.style.left = `${x * 100}%`;
      mask.style.top = `${y * 100}%`;
      mask.style.width = `${width * 100}%`;
      mask.style.height = `${height * 100}%`;
      mask.style.setProperty('--faceblur-strength', `${state.blur}px`);
      root.appendChild(mask);
    }
    if (!root.childElementCount) return;
    document.documentElement.appendChild(root);
    state.overlays.set(el, { root, boxes });
    updateOverlay(el);
    recalculateFaceCount();
  }

  async function processElement(el, force = false) {
    if (!siteEnabled() || !isVisible(el)) return removeOverlay(el);
    const identity = sourceIdentity(el);
    let cached = !force ? state.cache.get(identity) : null;
    let rawBoxes;
    let sourceWidth;
    let sourceHeight;

    if (cached) {
      ({ rawBoxes, sourceWidth, sourceHeight } = cached);
    } else {
      const rendered = await renderSource(el);
      sourceWidth = rendered.sourceWidth;
      sourceHeight = rendered.sourceHeight;
      const detections = await faceapi.detectAllFaces(
        rendered.canvas,
        new faceapi.TinyFaceDetectorOptions({ inputSize: state.scanSize, scoreThreshold: state.threshold })
      );
      const sx = sourceWidth / rendered.canvas.width;
      const sy = sourceHeight / rendered.canvas.height;
      rawBoxes = detections.map(({ box }) => ({
        x: box.x * sx,
        y: box.y * sy,
        width: box.width * sx,
        height: box.height * sy
      }));
      state.cache.set(identity, { rawBoxes, sourceWidth, sourceHeight });
      if (state.cache.size > 350) state.cache.delete(state.cache.keys().next().value);
    }

    const boxes = rawBoxes.map((box) => mapBoxToElement(box, sourceWidth, sourceHeight, el));
    renderMasks(el, boxes);
  }

  function clearAll() {
    for (const el of [...state.overlays.keys()]) removeOverlay(el);
  }

  function status() {
    return {
      modelReady: state.modelReady,
      error: state.modelError,
      faces: state.faceCount,
      media: state.mediaCount
    };
  }

  const mutation = new MutationObserver((records) => {
    for (const record of records) {
      if (record.type === 'attributes') {
        if (isMedia(record.target)) observe(record.target);
        enqueue(record.target, true);
      }
      for (const node of record.addedNodes) if (node instanceof Element) scan(node);
      for (const node of record.removedNodes) {
        if (!(node instanceof Element)) continue;
        if (state.overlays.has(node)) removeOverlay(node);
        for (const el of node.querySelectorAll?.('img,video,canvas,*') || []) if (state.overlays.has(el)) removeOverlay(el);
      }
    }
  });

  function repositionAll() {
    for (const el of state.overlays.keys()) updateOverlay(el);
  }

  api.runtime.onMessage.addListener(async (message) => {
    if (message?.type === 'FACEBLUR_STATUS') return status();
    if (message?.type === 'FACEBLUR_SETTINGS') {
      const oldThreshold = state.threshold;
      const oldScale = state.maskScale;
      Object.assign(state, normalizeSettings({ ...state, ...message.settings }));
      if (!siteEnabled()) clearAll();
      else {
        if (state.threshold !== oldThreshold) state.cache.clear();
        if (state.maskScale !== oldScale || message.settings?.blur !== undefined) {
          for (const el of state.overlays.keys()) enqueue(el, state.maskScale !== oldScale);
        }
        scan();
      }
      return status();
    }
    if (message?.type === 'FACEBLUR_RESCAN') {
      scan();
      for (const el of mediaCandidates(document)) enqueue(el, true);
      while (state.processing || state.queue.length) await sleep(40);
      return status();
    }
    if (message?.type === 'FACEBLUR_CLEAR_CACHE') {
      state.cache.clear();
      clearAll();
      scan();
      for (const el of mediaCandidates(document)) enqueue(el, true);
      return status();
    }
    return undefined;
  });

  (async () => {
    await loadSettings();
    await loadModel();
    scan();
    mutation.observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['src', 'srcset', 'style', 'class', 'poster']
    });
    addEventListener('scroll', repositionAll, { passive: true });
    addEventListener('resize', () => {
      clearTimeout(state.resizeTimer);
      state.resizeTimer = setTimeout(() => {
        repositionAll();
        for (const el of state.overlays.keys()) enqueue(el);
      }, 120);
    }, { passive: true });
    state.videoTimer = setInterval(() => {
      for (const video of document.querySelectorAll('video')) {
        if (!video.paused && isVisible(video)) enqueue(video, true);
      }
      repositionAll();
    }, 1100);
  })().catch((error) => {
    state.modelError = String(error?.message || error);
    console.error('[FaceBlur]', error);
  });
})();
