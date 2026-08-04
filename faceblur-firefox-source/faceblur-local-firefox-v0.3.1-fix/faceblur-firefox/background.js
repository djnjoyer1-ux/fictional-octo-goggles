'use strict';

const api = typeof browser !== 'undefined' ? browser : chrome;
const MAX_BYTES = 25 * 1024 * 1024;

api.runtime.onMessage.addListener(async (message) => {
  if (message?.type !== 'FACEBLUR_FETCH_IMAGE') return undefined;
  try {
    const response = await fetch(message.url, {
      credentials: 'omit',
      cache: 'force-cache',
      redirect: 'follow'
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const type = response.headers.get('content-type') || '';
    if (!type.startsWith('image/')) throw new Error('Resource is not an image');
    const length = Number(response.headers.get('content-length') || 0);
    if (length > MAX_BYTES) throw new Error('Image is too large');
    const blob = await response.blob();
    if (blob.size > MAX_BYTES) throw new Error('Image is too large');
    const buffer = await blob.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i += 0x8000) {
      binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    }
    return { ok: true, dataUrl: `data:${blob.type};base64,${btoa(binary)}` };
  } catch (error) {
    return { ok: false, error: String(error?.message || error) };
  }
});
