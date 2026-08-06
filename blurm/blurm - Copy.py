# optimized_blur_male_faces.py
# pip install opencv-python deepface tf-keras

from pathlib import Path
import cv2
from deepface import DeepFace

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}

INPUT_VIDEO = "input.mp4"
OUTPUT_DIR = "outputs"

DOWNSCALE_WIDTH = 640
ANALYZE_EVERY_N_FRAMES = 12
GENDER_THRESHOLD = 0.75
BLUR_STRENGTH = 51

MIN_FACE_SIZE = 45
TRACKER_REFRESH_LIMIT = 45


def make_odd(n):
    return n if n % 2 == 1 else n + 1


def blur_box(frame, box):
    x, y, w, h = map(int, box)
    H, W = frame.shape[:2]

    pad_x = int(w * 0.18)
    pad_y = int(h * 0.22)

    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(W, x + w + pad_x)
    y2 = min(H, y + h + pad_y)

    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return frame

    k = make_odd(BLUR_STRENGTH)
    frame[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (k, k), 30)
    return frame


def classify_male(face_crop):
    try:
        result = DeepFace.analyze(
            face_crop,
            actions=["gender"],
            enforce_detection=False,
            detector_backend="skip",
            silent=True,
        )

        if isinstance(result, list):
            result = result[0]

        male_score = result.get("gender", {}).get("Man", 0) / 100.0
        return male_score >= GENDER_THRESHOLD

    except Exception:
        return False


def detect_faces_fast(frame, face_detector):
    H, W = frame.shape[:2]

    scale = DOWNSCALE_WIDTH / W if W > DOWNSCALE_WIDTH else 1.0
    small = cv2.resize(frame, None, fx=scale, fy=scale)

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.15,
        minNeighbors=5,
        minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE),
    )

    boxes = []
    inv = 1 / scale

    for x, y, w, h in faces:
        boxes.append((
            int(x * inv),
            int(y * inv),
            int(w * inv),
            int(h * inv),
        ))

    return boxes


def create_tracker():
    if hasattr(cv2, "legacy"):
        return cv2.legacy.TrackerKCF_create()
    return cv2.TrackerKCF_create()


def process_video(input_file):
    input_path = Path(input_file)

    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Supported files: {SUPPORTED_EXTENSIONS}")

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    output_path = Path(OUTPUT_DIR) / f"{input_path.stem}_male_blurred.mp4"

    out = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (W, H),
    )

    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    frame_id = 0
    trackers = []
    male_boxes = []
    frames_since_detection = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        should_redetect = (
            frame_id % ANALYZE_EVERY_N_FRAMES == 0
            or frames_since_detection > TRACKER_REFRESH_LIMIT
            or not trackers
        )

        if should_redetect:
            trackers = []
            male_boxes = []

            face_boxes = detect_faces_fast(frame, face_detector)

            for box in face_boxes:
                x, y, w, h = box
                face_crop = frame[y:y+h, x:x+w]

                if face_crop.size == 0:
                    continue

                if classify_male(face_crop):
                    male_boxes.append(box)

                    tracker = create_tracker()
                    tracker.init(frame, tuple(box))
                    trackers.append(tracker)

            frames_since_detection = 0

        else:
            updated_boxes = []
            alive_trackers = []

            for tracker in trackers:
                ok, box = tracker.update(frame)

                if ok:
                    updated_boxes.append(box)
                    alive_trackers.append(tracker)

            male_boxes = updated_boxes
            trackers = alive_trackers
            frames_since_detection += 1

        for box in male_boxes:
            blur_box(frame, box)

        out.write(frame)
        frame_id += 1

    cap.release()
    out.release()

    print(f"Saved: {output_path}")


if __name__ == "__main__":
    process_video(INPUT_VIDEO)
