# fast_blur_male_faces.py
# pip install opencv-python numpy

from pathlib import Path
import time
import urllib.request
import cv2
import numpy as np

INPUT_VIDEO = "input.mp4"
OUTPUT_DIR = "outputs"

SUPPORTED = {".mp4", ".mov", ".avi", ".mkv"}

FACE_CONFIDENCE = 0.55
MALE_CONFIDENCE = 0.65
ANALYZE_EVERY_N_FRAMES = 8
DOWNSCALE_WIDTH = 640
BLUR_STRENGTH = 55

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

MODELS = {
    "face_prototxt": (
        MODEL_DIR / "deploy.prototxt",
        "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
    ),
    "face_model": (
        MODEL_DIR / "res10_300x300_ssd_iter_140000.caffemodel",
        "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel",
    ),
    "gender_prototxt": (
        MODEL_DIR / "deploy_gender.prototxt",
        "https://raw.githubusercontent.com/GilLevi/AgeGenderDeepLearning/master/models/deploy_gender.prototxt",
    ),
    "gender_model": (
        MODEL_DIR / "gender_net.caffemodel",
        "https://raw.githubusercontent.com/GilLevi/AgeGenderDeepLearning/master/models/gender_net.caffemodel",
    ),
}

GENDER_LIST = ["Male", "Female"]
GENDER_MEAN = (78.4263377603, 87.7689143744, 114.895847746)


def download_models():
    for name, (path, url) in MODELS.items():
        if not path.exists():
            print(f"Downloading {name}...")
            urllib.request.urlretrieve(url, path)
            print(f"Saved {path}")


def odd(n):
    return n if n % 2 == 1 else n + 1


def blur_box(frame, box):
    x1, y1, x2, y2 = box
    h, w = frame.shape[:2]

    pad_x = int((x2 - x1) * 0.18)
    pad_y = int((y2 - y1) * 0.25)

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x)
    y2 = min(h, y2 + pad_y)

    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return

    k = odd(BLUR_STRENGTH)
    frame[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (k, k), 30)


def detect_faces(frame, face_net):
    h, w = frame.shape[:2]

    scale = DOWNSCALE_WIDTH / w if w > DOWNSCALE_WIDTH else 1.0
    small = cv2.resize(frame, None, fx=scale, fy=scale)
    sh, sw = small.shape[:2]

    blob = cv2.dnn.blobFromImage(
        small,
        scalefactor=1.0,
        size=(300, 300),
        mean=(104.0, 177.0, 123.0),
    )

    face_net.setInput(blob)
    detections = face_net.forward()

    boxes = []
    inv = 1 / scale

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence < FACE_CONFIDENCE:
            continue

        box = detections[0, 0, i, 3:7] * np.array([sw, sh, sw, sh])
        x1, y1, x2, y2 = box.astype(int)

        boxes.append((
            int(x1 * inv),
            int(y1 * inv),
            int(x2 * inv),
            int(y2 * inv),
        ))

    return boxes


def is_male(frame, box, gender_net):
    x1, y1, x2, y2 = box
    h, w = frame.shape[:2]

    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    face = frame[y1:y2, x1:x2]
    if face.size == 0:
        return False

    blob = cv2.dnn.blobFromImage(
        face,
        scalefactor=1.0,
        size=(227, 227),
        mean=GENDER_MEAN,
        swapRB=False,
    )

    gender_net.setInput(blob)
    preds = gender_net.forward()[0]

    male_score = float(preds[0])
    return male_score >= MALE_CONFIDENCE


def format_time(seconds):
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    if h:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"


def process_video(input_file):
    download_models()

    input_path = Path(input_file)
    if input_path.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Supported filetypes: {', '.join(sorted(SUPPORTED))}")

    face_net = cv2.dnn.readNetFromCaffe(
        str(MODELS["face_prototxt"][0]),
        str(MODELS["face_model"][0]),
    )

    gender_net = cv2.dnn.readNetFromCaffe(
        str(MODELS["gender_prototxt"][0]),
        str(MODELS["gender_model"][0]),
    )

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    output_path = Path(OUTPUT_DIR) / f"{input_path.stem}_male_faces_blurred.mp4"

    out = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    frame_id = 0
    male_boxes = []
    start = time.time()
    male_face_hits = 0

    print("Processing started...")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Resolution: {width}x{height}, FPS: {fps:.2f}")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_id % ANALYZE_EVERY_N_FRAMES == 0:
            male_boxes = []

            face_boxes = detect_faces(frame, face_net)

            for box in face_boxes:
                if is_male(frame, box, gender_net):
                    male_boxes.append(box)
                    male_face_hits += 1

        for box in male_boxes:
            blur_box(frame, box)

        out.write(frame)

        frame_id += 1

        if frame_id % 60 == 0:
            elapsed = time.time() - start
            current_fps = frame_id / elapsed

            if total_frames:
                progress = frame_id / total_frames
                eta = elapsed / progress - elapsed
                print(
                    f"{progress * 100:5.1f}% | "
                    f"Frame {frame_id}/{total_frames} | "
                    f"{current_fps:.1f} fps | "
                    f"ETA {format_time(eta)} | "
                    f"Male face hits: {male_face_hits}"
                )
            else:
                print(
                    f"Frame {frame_id} | "
                    f"{current_fps:.1f} fps | "
                    f"Male face hits: {male_face_hits}"
                )

    cap.release()
    out.release()

    elapsed = time.time() - start
    print("\nDone.")
    print(f"Saved to: {output_path}")
    print(f"Elapsed: {format_time(elapsed)}")
    print(f"Average speed: {frame_id / elapsed:.1f} fps")


if __name__ == "__main__":
    process_video(INPUT_VIDEO)
