#!/usr/bin/env python3
"""
Example usage of Sarvam AI Speech-to-Text with Clean Output
Demonstrates the improved features including clean transcript extraction
"""

import os
from sarvam_stt import SarvamSTT
from pathlib import Path

def example_transcription():
    """Example of how to use the SarvamSTT class directly with clean output"""
    
    # Your API key (automatically loaded from .env file)
    api_key = os.getenv('SARVAM_API_KEY') or "YOUR_SARVAM_AI_API_KEY"
    
    if api_key == "YOUR_SARVAM_AI_API_KEY":
        print("⚠️  Please set your API key using: python setup_api_key.py")
        return
    
    # Initialize the STT client
    stt = SarvamSTT(api_key)
    
    # Path to your audio file
    audio_file = "ScreenRecordingAudio.mp3"  # Your Hindi conference call recording
    
    # Transcribe the audio with clean output
    # Language options:
    # - "hi-IN" for Hindi (recommended for your conference call)
    # - "en-IN" for English 
    # - "unknown" for auto-detect
    # - None for code-mixed speech
    
    print("🎯 Starting transcription with clean output...")
    print(f"📁 Input: {audio_file}")
    print(f"💾 Output: hindi_transcript_clean.txt")
    print("-" * 50)
    
    transcript = stt.transcribe_audio(
        audio_path=audio_file,
        language_code="hi-IN",  # Hindi
        output_file="hindi_transcript_clean.txt"
    )
    
    if transcript:
        print("\n✅ Transcription successful!")
        print("\n📄 Clean transcript preview:")
        print("=" * 40)
        # Show first 300 characters of clean transcript
        preview = transcript[:300] + "..." if len(transcript) > 300 else transcript
        print(preview)
        print("=" * 40)
        print(f"\n💾 Full transcript saved to: hindi_transcript_clean.txt")
        print("\n🎉 The transcript is clean and ready to use!")
    else:
        print("❌ Transcription failed")

def example_clean_existing_transcript():
    """Example of how to clean existing transcript files with API metadata"""
    
    # Check if there are any transcript files to clean
    transcript_files = list(Path(".").glob("*transcript*.txt"))
    
    if not transcript_files:
        print("📁 No transcript files found to clean")
        return
    
    print("🧹 Cleaning existing transcript files...")
    print(f"Found {len(transcript_files)} transcript files:")
    
    for file_path in transcript_files:
        print(f"  - {file_path.name}")
    
    # Import and use the cleaning function
    try:
        import subprocess
        import sys
        
        for file_path in transcript_files:
            if "_clean" not in file_path.name:  # Skip already cleaned files
                print(f"\n🧹 Cleaning: {file_path.name}")
                result = subprocess.run([
                    sys.executable, "clean_transcript.py", str(file_path)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Successfully cleaned: {file_path.name}")
                else:
                    print(f"❌ Failed to clean: {file_path.name}")
                    print(f"Error: {result.stderr}")
        
        print("\n🎉 Transcript cleaning completed!")
        
    except Exception as e:
        print(f"❌ Error during cleaning: {e}")

def main():
    """Main function to demonstrate all features"""
    print("🎆 Sarvam.ai Speech-to-Text Examples")
    print("=" * 50)
    
    print("\n1️⃣ Example: New Transcription with Clean Output")
    example_transcription()
    
    print("\n\n2️⃣ Example: Clean Existing Transcript Files")
    example_clean_existing_transcript()
    
    print("\n\n📚 Additional Usage:")
    print("- Run 'python sarvam_stt.py your_audio.mp3' for command-line usage")
    print("- Run 'python clean_transcript.py old_transcript.txt' to clean files")
    print("- Run 'python setup_api_key.py' to configure your API key")

if __name__ == "__main__":
    main()
