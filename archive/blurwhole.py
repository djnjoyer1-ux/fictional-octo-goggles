from moviepy.editor import VideoFileClip
import cv2
import numpy as np

def blur_frame(frame):
    """
    Applies a blur to the given frame using Gaussian blur.
    :param frame: The frame to be blurred.
    :return: Blurred frame.
    """
    return cv2.GaussianBlur(frame, (21, 21), 0)

def blur_video(input_video_path, output_video_path):
    """
    Blurs an entire video.
    :param input_video_path: Path to the input video (MP4).
    :param output_video_path: Path to save the blurred output video.
    """
    # Load the video file
    video_clip = VideoFileClip(input_video_path)

    # Get video details
    fps = video_clip.fps
    width, height = video_clip.size

    # Apply the blur frame by frame
    def process_frame(get_frame, t):
        # Get frame at time t
        frame = get_frame(t)
        # Convert the frame to numpy array for OpenCV processing
        frame = np.array(frame)
        # Apply blur to the frame
        blurred_frame = blur_frame(frame)
        return blurred_frame

    # Process video and save the output
    blurred_video = video_clip.fl(process_frame)

    # Write the result to a new file
    blurred_video.write_videofile(output_video_path, codec='libx264', fps=fps)

# Input and output file paths
input_video = 'rapidsave.com_-yot55iresc4f1.mp4'  # Replace with your input file
output_video = 'output_blurred_video.mp4'  # Replace with your desired output file

# Call the function to blur the video
blur_video(input_video, output_video)

print(f"Blurred video saved as: {output_video}")
