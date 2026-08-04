'use strict';

const api = typeof browser !== 'undefined' ? browser : chrome;
const DEFAULTS = Object.freeze({
  enabled: true,
  blur: 18,
  threshold: 0.45,
  maskScale: 1.35,
  scanSize: 416,
  disabledHosts: []
});

const $ = (id) => document.getElementById(id);
const controls = ['enabled', 'blur', 'threshold', 'maskScale', 'scanSize'];
let activeTab = null;
let activeHost = '';
let settings = { ...DEFAULTS };

function safeNumber(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function normalize(raw = {}) {
  return {
    enabled: typeof raw.enabled === 'boolean' ? raw.enabled : DEFAULTS.enabled,
    blur: safeNumber(raw.blur, DEFAULTS.blur),
    threshold: safeNumber(raw.threshold, DEFAULTS.threshold),
    maskScale: safeNumber(raw.maskScale, DEFAULTS.maskScale),
    scanSize: safeNumber(raw.scanSize, DEFAULTS.scanSize),
    disabledHosts: Array.isArray(raw.disabledHosts) ? raw.disabledHosts.filter(Boolean) : []
  };
}

function updateOutputs() {
  $('blurOut').value = `${safeNumber($('blur').value, DEFAULTS.blur)} px`;
  $('thresholdOut').value = safeNumber($('threshold').value, DEFAULTS.threshold).toFixed(2);
  $('maskOut').value = `${safeNumber($('maskScale').value, DEFAULTS.maskScale).toFixed(2)}×`;
  $('scanSizeOut').value = `${safeNumber($('scanSize').value, DEFAULTS.scanSize)} px`;
}

function populate() {
  $('enabled').checked = settings.enabled;
  $('blur').value = settings.blur;
  $('threshold').value = settings.threshold;
  $('maskScale').value = settings.maskScale;
  $('scanSize').value = settings.scanSize;
  $('siteDisabled').checked = Boolean(activeHost && settings.disabledHosts.includes(activeHost));
  $('siteName').textContent = activeHost || 'Current website';
  updateOutputs();
}

async function send(message) {
  if (!activeTab?.id) return null;
  try { return await api.tabs.sendMessage(activeTab.id, message); }
  catch { return null; }
}

async function savePatch(patch) {
  settings = normalize({ ...settings, ...patch });
  await api.storage.local.set(patch);
  await send({ type: 'FACEBLUR_SETTINGS', settings: patch });
}

function showStatus(reply) {
  const dot = $('statusDot');
  dot.className = 'dot';
  if (!reply) {
    dot.classList.add('error');
    $('statusText').textContent = 'Unavailable here';
    $('statsText').textContent = 'Protected page';
    return;
  }
  if (reply.error) {
    dot.classList.add('error');
    $('statusText').textContent = 'Model error';
    $('statsText').textContent = reply.error;
    return;
  }
  if (reply.modelReady) dot.classList.add('ready');
  $('statusText').textContent = reply.modelReady ? 'Detector ready' : 'Loading model…';
  $('statsText').textContent = `${reply.faces || 0} faces · ${reply.media || 0} media`;
}

async function init() {
  [activeTab] = await api.tabs.query({ active: true, currentWindow: true });
  try { activeHost = new URL(activeTab?.url || '').hostname; } catch { activeHost = ''; }
  settings = normalize(await api.storage.local.get(DEFAULTS));
  populate();
  showStatus(await send({ type: 'FACEBLUR_STATUS' }));
}

for (const id of controls) {
  $(id).addEventListener(id === 'enabled' ? 'change' : 'input', async (event) => {
    updateOutputs();
    const value = id === 'enabled' ? event.target.checked : safeNumber(event.target.value, DEFAULTS[id]);
    await savePatch({ [id]: value });
  });
}

$('siteDisabled').addEventListener('change', async (event) => {
  if (!activeHost) return;
  const set = new Set(settings.disabledHosts);
  event.target.checked ? set.add(activeHost) : set.delete(activeHost);
  await savePatch({ disabledHosts: [...set] });
});

$('rescan').addEventListener('click', async () => {
  $('statusText').textContent = 'Scanning…';
  showStatus(await send({ type: 'FACEBLUR_RESCAN' }));
});

$('clearCache').addEventListener('click', async () => {
  showStatus(await send({ type: 'FACEBLUR_CLEAR_CACHE' }));
});

document.addEventListener('DOMContentLoaded', init);
