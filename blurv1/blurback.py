import cv2
import numpy as np
from retinaface import RetinaFace

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

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect faces with RetinaFace
    faces = RetinaFace.detect_faces(frame)

    if faces is None:
        # No faces detected, write frame as is
        out.write(frame)
        continue

    for key, face in faces.items():
        x1, y1, x2, y2 = face["facial_area"]

        # Clamp coordinates inside frame boundaries
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(width - 1, x2), min(height - 1, y2)

        face_img = frame[y1:y2, x1:x2]

        if face_img.size == 0:
            continue

        # Prepare blob for gender classification
        face_blob = cv2.dnn.blobFromImage(
            cv2.resize(face_img, (227, 227)), 1.0, (227, 227),
            (78.4263377603, 87.7689143744, 114.895847746), swapRB=False
        )
        gender_net.setInput(face_blob)
        gender_preds = gender_net.forward()
        gender = gender_list[gender_preds[0].argmax()]

        if gender == 'Male':
            # Blur male face area
            face_blur = cv2.GaussianBlur(face_img, (55, 55), 0)
            frame[y1:y2, x1:x2] = face_blur

    out.write(frame)

cap.release()
out.release()
cv2.destroyAllWindows()
