import os
import sys
import subprocess
from pathlib import Path

# Function to check and install required packages
def install_packages():
    required_packages = ["ffmpeg-python"]
    for package in required_packages:
        try:
            __import__(package.split("-")[0])  # Attempt to import the package
        except ImportError:
            print(f"{package} not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Function to convert MKV to WebM
def convert_mkv_to_webm(directory):
    import ffmpeg

    converted_dir = Path(directory) / "converted"
    converted_dir.mkdir(exist_ok=True)  # Create the 'converted' subfolder if it doesn't exist

    for file in Path(directory).glob("*.mkv"):  # Only look in the current directory
        output_file = converted_dir / f"{file.stem}.webm"
        print(f"Converting {file} to {output_file}...")
        try:
            ffmpeg.input(str(file)).output(str(output_file), vcodec="libvpx", acodec="libvorbis").run()
            print(f"Conversion successful: {output_file}")
        except Exception as e:
            print(f"Failed to convert {file}: {e}")

if __name__ == "__main__":
    # Ensure packages are installed
    install_packages()

    # Use the folder where the script is located as the target directory
    script_directory = os.path.dirname(os.path.abspath(__file__))

    print(f"Converting MKV files in the script's directory: {script_directory}")
    
    # Convert MKV files to WebM and save in 'converted' subfolder
    convert_mkv_to_webm(script_directory)
