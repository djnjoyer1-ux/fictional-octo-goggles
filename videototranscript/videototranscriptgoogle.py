import os
import moviepy.editor as mp
import speech_recognition as sr

def extract_audio(video_path, audio_path):
    try:
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, codec='pcm_s16le')
        print(f"Audio extracted successfully to {audio_path}")
        return True
    except Exception as e:
        print(f"Error extracting audio from {video_path}: {str(e)}")
        return False

def transcribe_audio(audio_path):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        transcript = recognizer.recognize_google(audio)
        return transcript
    except sr.RequestError as e:
        print(f"Error with the request: {str(e)}")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
    except Exception as e:
        print(f"Error transcribing audio from {audio_path}: {str(e)}")
    return None

if __name__ == "__main__":
    current_folder = os.getcwd()
    output_folder = os.path.join(current_folder, 'output_transcripts')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(current_folder):
        if filename.endswith('.mp4') or filename.endswith('.avi'):
            video_path = os.path.join(current_folder, filename)
            audio_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.wav")
            transcript_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")

            # Step 1: Extract audio from video
            if extract_audio(video_path, audio_path):
                # Step 2: Transcribe audio to text
                transcript = transcribe_audio(audio_path)
                if transcript:
                    # Step 3: Save transcript to a file
                    with open(transcript_path, 'w') as file:
                        file.write(transcript)
                    print(f"Transcript for {filename} saved to {transcript_path}")
                else:
                    print(f"Transcription for {filename} failed.")
            else:
                print(f"Audio extraction for {filename} failed.")
