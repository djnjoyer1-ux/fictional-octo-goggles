$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$files = @{
  "vendor\face-api.min.js" = "https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js"
  "models\tiny_face_detector_model-weights_manifest.json" = "https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/tiny_face_detector_model-weights_manifest.json"
  "models\tiny_face_detector_model-shard1" = "https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/tiny_face_detector_model-shard1"
}
foreach ($relative in $files.Keys) {
  $target = Join-Path $root $relative
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
  Write-Host "Downloading $relative..."
  Invoke-WebRequest -UseBasicParsing -Uri $files[$relative] -OutFile $target
}
Write-Host "Done."
