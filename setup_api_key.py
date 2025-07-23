#!/usr/bin/env python3
"""
Setup script to configure Sarvam AI API key
"""

import os
from pathlib import Path

def setup_api_key():
    """Setup Sarvam AI API key"""
    print("=== Sarvam AI API Key Setup ===\n")
    
    print("To get your API key:")
    print("1. Visit: https://dashboard.sarvam.ai/")
    print("2. Sign up or log in")
    print("3. Get your API subscription key")
    print()
    
    api_key = input("Enter your Sarvam AI API key: ").strip()
    
    if not api_key:
        print("No API key provided. Exiting...")
        return
    
    # Create .env file
    env_file = Path(".env")
    with open(env_file, "w") as f:
        f.write(f"SARVAM_API_KEY={api_key}\n")
    
    print(f"✓ API key saved to {env_file}")
    print("\n🎉 Setup completed! The script will now automatically load your API key.")
    
    print("\n🚀 Ready to use - try these commands:")
    print("  python sarvam_stt.py your_audio_file.mp3    # Main transcription")
    print("  python example_usage.py                     # See examples")
    print("  python clean_transcript.py old_file.txt     # Clean existing files")
    
    print("\n✨ New Features:")
    print("  ✅ Clean text output (no API metadata)")
    print("  ✅ Automatic API key loading from .env")
    print("  ✅ Improved text formatting with proper newlines")
    print("  ✅ Transcript cleaning utilities")
    
    # Also set environment variable for current session
    os.environ['SARVAM_API_KEY'] = api_key
    print("\n✓ API key set for current session")

if __name__ == "__main__":
    setup_api_key()
