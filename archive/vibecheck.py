import cv2
import numpy as np
import moviepy.editor as mp
import librosa
import librosa.display
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pyAudioAnalysis import audioTrainTest as aT

def extract_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def count_laughs(audio_path):
    # Use pre-trained laughter detection model
    feature_and_label = aT.file_classification(audio_path, "laughterModel", "svm")
    laugh_prob = feature_and_label[1][1]  # Assuming laughter is the second class
    return laugh_prob

if __name__ == "__main__":
    video_file = "test.webm"
    audio_file = "extracted_audio.wav"
    
    extract_audio(video_file, audio_file)
    laughs = count_laughs(audio_file)
    print(f"Estimated number of laughs in the video: {laughs}")
