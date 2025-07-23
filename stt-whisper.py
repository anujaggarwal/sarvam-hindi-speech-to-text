import whisper
import os
import subprocess
from tqdm import tqdm

def trim_audio(input_file, output_file, start_time, duration):
    command = [
        "ffmpeg",
        "-i", input_file,
        "-ss", str(start_time),
        "-t", str(duration),
        "-c", "copy",
        output_file
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"Trimmed audio saved to: {os.path.abspath(output_file)}")
    except subprocess.CalledProcessError as e:
        print(f"Error trimming audio: {e.stderr.decode()}")
        raise

def transcribe_audio(file_path, output_path="transcription.txt"):
    model = whisper.load_model("small")  # Change to "tiny", "small", etc. for speed/accuracy trade-off
    result = model.transcribe(file_path, language="hi")
    transcription = result["text"]

    # Save transcription to a file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(transcription)
    
    print(f"Transcription saved to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    audio_file = "ScreenRecordingAudio.mp3"  # Replace with your file path
    trimmed_audio_file = "trimmed_audio.mp3"
    # Simulate progress for trimming (ffmpeg doesn't provide direct progress to Python)
    print("Trimming audio...")
    for _ in tqdm(range(100), desc="Trimming Progress"): # This is a dummy progress bar
        pass # In a real scenario, you'd monitor ffmpeg's output
    trim_audio(audio_file, trimmed_audio_file, 0, 0.5 * 60)  # Trim to first 3 minutes (in seconds)
    print("Audio trimming complete. Starting transcription...")
    transcribe_audio(trimmed_audio_file)