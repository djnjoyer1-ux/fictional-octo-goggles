import subprocess
import os
import sys

def mute_video(input_file):
    # Check if input file exists
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found.")

    # Generate output filename
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}-muted{ext}"

    # ffmpeg command to remove audio
    command = [
        "ffmpeg", "-y",  # Overwrite output file if it exists
        "-i", input_file,  # Input file
        "-c:v", "copy",  # Copy video stream without re-encoding
        "-an",  # Remove audio stream
        output_file  # Output file
    ]

    # Run the ffmpeg command
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Muted video saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print("Error during video processing:", e.stderr.decode())
        raise

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mute_video.py <input_file>")
        sys.exit(1)

    input_video = sys.argv[1]
    try:
        mute_video(input_video)
    except Exception as e:
        print(f"Error: {e}")
