import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

# Input & output files
input_video = 'input.mp4'
output_video = 'output_blurred.mp4'

# Capture input video
cap = cv2.VideoCapture(input_video)
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Set up video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get segmentation mask
    results = selfie_segmentation.process(rgb_frame)
    mask = results.segmentation_mask

    # Threshold the mask
    condition = mask > 0.5

    # Blur the frame
    blurred_frame = cv2.GaussianBlur(frame, (55, 55), 0)

    # Combine person + blurred background
    output_frame = np.where(condition[..., None], frame, blurred_frame)

    # Write frame
    out.write(output_frame)

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()
