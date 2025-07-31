#!/usr/bin/env python3
"""
Test script to verify Sarvam.ai transliteration API functionality

PURPOSE:
This script was created to debug and verify the transliteration functionality
when implementing the dual output system for the speech-to-text pipeline.

TESTS:
- Verifies API key is properly loaded from .env file
- Tests transliteration API with mixed Hindi/English text
- Checks response format and attribute access
- Validates that Hindi text is transliterated while English remains unchanged

USAGE:
- Run this script independently to test transliteration without full audio processing
- Useful for debugging transliteration issues in isolation
- Helps verify API connectivity and response format
"""

import os
from pathlib import Path
from sarvamai import SarvamAI

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

def test_transliteration():
    """Test transliteration functionality"""
    load_env_file()
    
    api_key = os.getenv('SARVAM_API_KEY')
    if not api_key:
        print("Error: SARVAM_API_KEY not found in environment")
        return
    
    client = SarvamAI(api_subscription_key=api_key)
    
    # Test Hindi text
    hindi_text = "मैं ऑफिस जा रहा हूँ। गेम ऑफ चांस versus game of skill।"
    
    print(f"Original text: {hindi_text}")
    print("Testing transliteration...")
    
    try:
        # Check if the method exists
        if hasattr(client, 'text') and hasattr(client.text, 'transliterate'):
            print("✓ transliterate method found")
            
            response = client.text.transliterate(
                input=hindi_text,
                source_language_code="hi-IN",
                target_language_code="en-IN",
                spoken_form=True,
            )
            
            print(f"✓ API call successful")
            print(f"Response type: {type(response)}")
            print(f"Response: {response}")
            
            if hasattr(response, 'transliterated_text'):
                transliterated_text = response.transliterated_text
                print(f"✓ Transliterated text: {transliterated_text}")
            else:
                print("✗ No transliterated_text attribute found")
                print(f"Available attributes: {dir(response)}")
                
        else:
            print("✗ transliterate method not found")
            print(f"Available methods in client.text: {dir(client.text) if hasattr(client, 'text') else 'No text attribute'}")
            
    except Exception as e:
        print(f"✗ Error during transliteration: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_transliteration()
