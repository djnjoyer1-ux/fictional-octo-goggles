'use strict';

browser.runtime.onMessage.addListener(async (message) => {
  if (message?.type !== 'FACEBLUR_FETCH_IMAGE') return undefined;
  try {
    const response = await fetch(message.url, { credentials: 'omit', cache: 'force-cache' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const blob = await response.blob();
    if (!blob.type.startsWith('image/')) throw new Error('Not an image');
    const buffer = await blob.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    let binary = '';
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    return { ok: true, dataUrl: `data:${blob.type};base64,${btoa(binary)}` };
  } catch (error) {
    return { ok: false, error: String(error?.message || error) };
  }
});
