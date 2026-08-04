import { mkdir, writeFile } from 'node:fs/promises';
const files = {
  'vendor/face-api.min.js':'https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js',
  'models/tiny_face_detector_model-weights_manifest.json':'https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/tiny_face_detector_model-weights_manifest.json',
  'models/tiny_face_detector_model-shard1':'https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/tiny_face_detector_model-shard1'
};
for (const [path,url] of Object.entries(files)) {
  await mkdir(path.split('/').slice(0,-1).join('/'),{recursive:true});
  const res=await fetch(url); if(!res.ok) throw new Error(`${url}: ${res.status}`);
  await writeFile(path,Buffer.from(await res.arrayBuffer())); console.log(`Downloaded ${path}`);
}
