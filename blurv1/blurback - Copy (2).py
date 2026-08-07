import cv2
import numpy as np

# Load face detector DNN model (better with occlusions)
face_net = cv2.dnn.readNetFromCaffe(
    'deploy.prototxt',
    'res10_300x300_ssd_iter_140000.caffemodel'
)

# Load gender detection DNN model
gender_net = cv2.dnn.readNetFromCaffe(
    'deploy_gender.prototxt',
    'gender_net.caffemodel'
)
gender_list = ['Male', 'Female']

input_video = 'input.mp4'
output_video = 'output_male_blurred.mp4'

cap = cv2.VideoCapture(input_video)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]

    # Prepare input blob for face detector
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    face_net.setInput(blob)
    detections = face_net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.6:  # threshold for detection
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")

            # Clamp box to frame size
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w - 1, x2), min(h - 1, y2)

            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                continue

            # Gender classification prep
            face_blob = cv2.dnn.blobFromImage(
                cv2.resize(face, (227, 227)), 1.0, (227, 227),
                (78.4263377603, 87.7689143744, 114.895847746), swapRB=False
            )
            gender_net.setInput(face_blob)
            gender_preds = gender_net.forward()
            gender = gender_list[gender_preds[0].argmax()]

            if gender == 'Male':
                # Blur male face area
                face_blur = cv2.GaussianBlur(face, (55, 55), 0)
                frame[y1:y2, x1:x2] = face_blur

    out.write(frame)

cap.release()
out.release()
cv2.destroyAllWindows()
