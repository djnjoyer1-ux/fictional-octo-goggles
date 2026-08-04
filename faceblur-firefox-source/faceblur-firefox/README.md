# FaceBlur Local for Firefox

A privacy-focused Firefox extension that detects faces in page images and places a live CSS `backdrop-filter` blur over each detected face. Detection runs locally with Tiny Face Detector from face-api.js.

## Build

1. Install Node.js 18 or newer.
2. In this folder run: `npm run vendor`
3. Open Firefox and visit `about:debugging#/runtime/this-firefox`.
4. Click **Load Temporary Add-on** and choose `manifest.json`.

For permanent installation, zip the folder after running `npm run vendor`, then sign/publish it through Firefox Add-ons.

## What it handles

- Normal `<img>` elements, including cross-origin images
- CSS background images
- `<canvas>` elements
- Videos, rescanned about every 1.5 seconds
- Infinite-scroll and lazy-loaded pages

## Limits

- Firefox internal pages and some protected extension pages cannot be modified.
- Faces that are tiny, heavily occluded, or stylized may be missed.
- Video detection is periodic rather than frame-perfect.
- Some sites use unusual compositing or closed shadow roots that can prevent overlays from lining up perfectly.

## Privacy

Image fetches are performed by the local extension background page only to bypass canvas cross-origin restrictions. No image data is sent to a server operated by this extension.
