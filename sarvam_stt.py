#!/usr/bin/env python3
"""
Sarvam.ai Speech-to-Text Script
Converts Hindi MP3 audio files to text using Sarvam AI's Saarika model
"""

import os
import sys
import subprocess
from pathlib import Path
from sarvamai import SarvamAI

class SarvamSTT:
    def __init__(self, api_key):
        """Initialize Sarvam AI client with API key"""
        self.client = SarvamAI(api_subscription_key=api_key)
        self.chunk_duration = 29  # seconds (under 30s limit)
        
    def split_audio_ffmpeg(self, audio_path, output_dir="chunks"):
        """
        Split large audio file into smaller chunks using FFmpeg
        """
        print(f"Splitting audio file: {audio_path}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get file extension and base name
        ext = os.path.splitext(audio_path)[1].lower()
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_pattern = os.path.join(output_dir, f"{base_name}_%03d{ext}")
        
        # Choose codec based on file type
        codec = "pcm_s16le" if ext == ".wav" else "libmp3lame"
        
        # FFmpeg command to split audio
        command = [
            "ffmpeg",
            "-i", audio_path,
            "-f", "segment",
            "-segment_time", str(self.chunk_duration),
            "-c:a", codec,
            "-y",  # Overwrite output files
            output_pattern
        ]
        
        print("Running FFmpeg command...")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print("Audio splitting completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error splitting audio: {e}")
            print(f"STDERR: {e.stderr}")
            return []
        
        # Get list of generated chunks
        output_files = sorted([
            os.path.join(output_dir, f) for f in os.listdir(output_dir)
            if f.endswith(ext) and f.startswith(base_name)
        ])
        
        print(f"Generated {len(output_files)} audio chunks")
        return output_files
    
    def extract_transcript_text(self, api_response):
        """
        Extract clean transcript text from API response
        """
        response_str = str(api_response)
        
        # Extract transcript content using string parsing
        try:
            # Look for transcript='...' pattern
            start_marker = "transcript='"
            end_marker = "' timestamps="
            
            start_idx = response_str.find(start_marker)
            if start_idx == -1:
                return response_str  # Return original if pattern not found
            
            start_idx += len(start_marker)
            end_idx = response_str.find(end_marker, start_idx)
            
            if end_idx == -1:
                # Try alternative end marker
                end_marker = "' diarized_transcript="
                end_idx = response_str.find(end_marker, start_idx)
            
            if end_idx == -1:
                return response_str  # Return original if pattern not found
            
            transcript = response_str[start_idx:end_idx]
            # Replace \n with actual newlines
            transcript = transcript.replace('\\n', '\n')
            return transcript
            
        except Exception as e:
            print(f"Warning: Could not parse transcript, using raw response: {e}")
            return response_str
    
    def transcribe_chunk(self, chunk_path, language_code="hi-IN"):
        """
        Transcribe a single audio chunk
        """
        try:
            with open(chunk_path, "rb") as audio_file:
                response = self.client.speech_to_text.transcribe(
                    file=audio_file,
                    model="saarika:v2.5",
                    language_code=language_code
                )
                return self.extract_transcript_text(response)
        except Exception as e:
            print(f"Error transcribing chunk {chunk_path}: {e}")
            return ""
    
    def transcribe_audio_chunks(self, chunk_paths, language_code="hi-IN"):
        """
        Transcribe multiple audio chunks and combine results
        """
        full_transcript = []
        
        print(f"Transcribing {len(chunk_paths)} chunks...")
        
        for idx, chunk_path in enumerate(chunk_paths, 1):
            print(f"Processing chunk {idx}/{len(chunk_paths)}: {os.path.basename(chunk_path)}")
            
            transcript = self.transcribe_chunk(chunk_path, language_code)
            if transcript:
                full_transcript.append(transcript)
                print(f"✓ Chunk {idx} transcribed successfully")
            else:
                print(f"✗ Failed to transcribe chunk {idx}")
        
        return " ".join(full_transcript).strip()
    
    def transcribe_short_audio(self, audio_path, language_code="hi-IN"):
        """
        Transcribe short audio file (< 30 seconds) directly
        """
        print(f"Transcribing short audio file: {audio_path}")
        
        try:
            with open(audio_path, "rb") as audio_file:
                response = self.client.speech_to_text.transcribe(
                    file=audio_file,
                    model="saarika:v2.5",
                    language_code=language_code
                )
                return self.extract_transcript_text(response)
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""
    
    def get_audio_duration(self, audio_path):
        """
        Get audio duration using FFprobe
        """
        try:
            command = [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                audio_path
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
            return duration
        except:
            return None
    
    def transcribe_audio(self, audio_path, language_code="hi-IN", output_file=None):
        """
        Main method to transcribe audio file (handles both short and long files)
        """
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found: {audio_path}")
            return None
        
        print(f"Starting transcription for: {audio_path}")
        print(f"Language code: {language_code}")
        
        # Get audio duration
        duration = self.get_audio_duration(audio_path)
        if duration:
            print(f"Audio duration: {duration:.2f} seconds")
        
        # Decide whether to split or transcribe directly
        if duration and duration > 30:
            print("Audio is longer than 30 seconds, splitting into chunks...")
            chunks = self.split_audio_ffmpeg(audio_path)
            if not chunks:
                print("Failed to split audio file")
                return None
            
            transcript = self.transcribe_audio_chunks(chunks, language_code)
            
            # Clean up chunks
            print("Cleaning up temporary chunks...")
            for chunk in chunks:
                try:
                    os.remove(chunk)
                except:
                    pass
            
            # Remove chunks directory if empty
            chunks_dir = os.path.dirname(chunks[0]) if chunks else "chunks"
            try:
                os.rmdir(chunks_dir)
            except:
                pass
        else:
            print("Audio is short enough for direct transcription...")
            transcript = self.transcribe_short_audio(audio_path, language_code)
        
        if transcript:
            print("Transcription completed successfully!")
            
            # Save to file if specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                print(f"Transcript saved to: {output_file}")
            
            return transcript
        else:
            print("Transcription failed")
            return None

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def main():
    """Main function"""
    print("=== Sarvam.ai Speech-to-Text Converter ===\n")
    
    # Load .env file
    load_env_file()
    
    # Get API key
    api_key = os.getenv('SARVAM_API_KEY')
    if not api_key:
        api_key = input("Enter your Sarvam AI API key: ").strip()
        if not api_key:
            print("Error: API key is required")
            sys.exit(1)
    
    # Initialize STT client
    stt = SarvamSTT(api_key)
    
    # Get audio file path
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = input("Enter path to your MP3/WAV file: ").strip()
    
    if not audio_file:
        print("Error: Audio file path is required")
        sys.exit(1)
    
    # Language selection
    print("\nSupported languages:")
    print("1. Hindi (hi-IN) - Default")
    print("2. English (en-IN)")
    print("3. Auto-detect (unknown)")
    print("4. Code-mixed (leave empty)")
    
    lang_choice = input("Select language (1-4, default=1): ").strip()
    
    language_map = {
        "1": "hi-IN",
        "2": "en-IN", 
        "3": "unknown",
        "4": None
    }
    
    language_code = language_map.get(lang_choice, "hi-IN")
    
    # Generate output filename
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    output_file = f"{base_name}_transcript.txt"
    
    # Perform transcription
    print(f"\nStarting transcription...")
    print(f"Input: {audio_file}")
    print(f"Output: {output_file}")
    print("-" * 50)
    
    if language_code:
        transcript = stt.transcribe_audio(audio_file, language_code, output_file)
    else:
        # Code-mixed transcription (no language_code parameter)
        print("Using code-mixed transcription...")
        try:
            with open(audio_file, "rb") as audio_file_obj:
                response = stt.client.speech_to_text.transcribe(
                    file=audio_file_obj,
                    model="saarika:v2.5"
                )
                transcript = stt.extract_transcript_text(response)
                
                if transcript:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(transcript)
                    print(f"Transcript saved to: {output_file}")
        except Exception as e:
            print(f"Error in code-mixed transcription: {e}")
            transcript = None
    
    if transcript:
        print("\n" + "="*50)
        print("TRANSCRIPTION RESULT:")
        print("="*50)
        print(transcript)
        print("="*50)
        print(f"\nTranscript also saved to: {output_file}")
    else:
        print("Transcription failed. Please check your API key and audio file.")

if __name__ == "__main__":
    main()
