# FaceBlur Local for Firefox

FaceBlur detects faces locally and places a blur mask over only the detected face regions. It does not identify people and does not upload images.

## Install for testing

1. Install Node.js 18 or newer.
2. Run `npm run vendor` once. This downloads the local face-api.js runtime and Tiny Face Detector model into the extension folder.
3. Open `about:debugging#/runtime/this-firefox` in Firefox.
4. Click **Load Temporary Add-on** and choose `manifest.json`.

## Improvements in 0.3

- Fixed the `undefinedpx` popup bug with normalized settings and explicit defaults.
- Visible-media scanning through `IntersectionObserver`.
- Detection caching to avoid rescanning unchanged images.
- Dynamic content support through `MutationObserver`.
- Handles images, videos, canvases, and CSS background images.
- Corrects masks for `object-fit: contain` and `object-fit: cover`.
- Per-site pause switch.
- Adjustable blur, confidence threshold, mask size, and detection resolution.
- Status display with media and face counts.
- Cache clearing and forced rescanning.
- Local model files only; no remotely executed code.

## Notes

- Firefox internal pages and extension-store pages cannot be modified.
- Tiny, heavily occluded, stylized, or very low-resolution faces may be missed.
- Video is sampled periodically instead of tracking every frame.
- Some closed shadow roots and unusual compositing layouts may prevent exact overlay alignment.

## Fixing “Model error / NetworkError”
The detector cannot start until its three local runtime/model files exist. On Windows, double-click `vendor.cmd`, wait for “Detector files installed,” then reload the add-on from `about:debugging`. The extension does not upload page images; these files are only the detector runtime and weights.
