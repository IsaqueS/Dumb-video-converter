import os
import sys
import tomllib
import subprocess
from pathlib import Path
from typing import Any

class Settings():
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}
        try:
            with open("settings.toml", "rb") as file:
                self.data = tomllib.load(file)
            print("Settings loaded:", self.data)
        except FileNotFoundError:
            print("❌ Error: settings.toml not found. Please create it.")
            sys.exit(1)
    
    def __getitem__(self, arg):
        return self.data[arg]

def convert_videos(settings: Settings) -> None:
    source_dir = Path(settings["path"]["source"])
    output_dir = Path(settings["path"]["output"])

    remove_on_finish: bool = settings["path"]["remove-on-finish"]

    # --- Improvement: Create the output directory if it doesn't exist ---
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        videos = os.listdir(source_dir)
        if not videos:
            print(f"No videos found in '{source_dir}'. Nothing to do.")
            return
    except FileNotFoundError:
        print(f"❌ Error: Source directory not found at '{source_dir}'")
        sys.exit(1)

    print(f"Found {len(videos)} videos to process...")

    for video in videos:
        # Construct full, absolute paths for clarity and robustness
        input_path = source_dir.resolve() / video
        # Create a new filename for the output, e.g., video.mov -> video.mp4
        output_filename = Path(video).stem + ".mp4"
        output_path = output_dir.resolve() / output_filename

        print(f"\n--- Processing: {video} ---")
        print(f"Input:  {input_path}")
        print(f"Output: {output_path}")

        # --- FIX 1: Command list with clean string arguments (no extra quotes) ---
        command: list[str] = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '20',
            '-vf', f'scale=-1:{settings["video"]["resolution"]}',
            '-c:a', 'aac',
            '-b:a', '192k',
            str(output_path)
        ]
        
        try:
            # --- FIX 2: Pass the LIST directly to subprocess.run ---
            # Added check=True to raise an error if FFmpeg fails
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"✅ Successfully converted {video}")

            if remove_on_finish:
                print("Input file removed...")
                os.remove(input_path)

        except FileNotFoundError:
            print("❌ FATAL ERROR: 'ffmpeg' command not found.")
            print("Please ensure FFmpeg is installed and in your system's PATH.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            # This will catch errors from FFmpeg itself (e.g., bad file, wrong settings)
            print(f"❌ Error converting {video}.")
            print("FFmpeg stderr output:")
            print(e.stderr)
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred: {e}")

    print("\nAll videos processed.")

if __name__ == "__main__":
    # Assuming settings.toml is in the same directory as the script
    # Example settings.toml:
    # [path]
    # source = "Videos a converter"
    # output = "Videos convertidos"
    #
    # [video]
    # resolution = 540
    convert_videos(Settings())
