#!/usr/bin/env python3
"""
Simple timing comparison between Whisper and Sarvam.ai
"""

import time
import os
from sarvam_stt import SarvamSTT

def test_sarvam():
    """Test Sarvam.ai with 30-second file"""
    audio_file = 'trimmed_audio_30s.mp3'
    
    # Check if API key exists in environment or .env file
    api_key = os.getenv('SARVAM_API_KEY')
    
    # Try to load from .env file if not in environment
    if not api_key:
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('SARVAM_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except FileNotFoundError:
            pass
    
    if not api_key:
        print("❌ SARVAM_API_KEY not found in environment or .env file")
        return None
    
    print(f"🎵 Testing Sarvam.ai with: {audio_file}")
    print(f"📊 File size: {os.path.getsize(audio_file) / (1024*1024):.2f} MB")
    
    stt = SarvamSTT(api_key)
    
    print("⏱️  Starting Sarvam.ai transcription...")
    start_time = time.time()
    
    try:
        result = stt.transcribe_audio(audio_file, language_code='hi-IN')
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        print(f"\n✅ SARVAM.AI RESULTS:")
        print(f"   Processing time: {processing_time:.2f} seconds")
        print(f"   Speed ratio: {30.0 / processing_time:.2f}x real-time")
        print(f"   Text length: {len(result) if result else 0} characters")
        
        if result:
            print(f"   First 100 chars: {result[:100]}...")
            
        return {
            'service': 'Sarvam.ai',
            'processing_time': processing_time,
            'text_length': len(result) if result else 0,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Sarvam.ai error: {e}")
        return None

def print_whisper_results():
    """Print the Whisper results from the previous test"""
    print(f"\n🖥️  WHISPER MEDIUM MODEL RESULTS:")
    print(f"   Model loading: 7.40 seconds")
    print(f"   Processing time: 382.37 seconds")
    print(f"   Total time: 389.77 seconds")
    print(f"   Speed ratio: 0.08x real-time (very slow)")
    print(f"   Text length: 524 characters")

def main():
    print("="*60)
    print("🏁 PERFORMANCE COMPARISON: 30-SECOND AUDIO FILE")
    print("="*60)
    
    # Test Sarvam.ai
    sarvam_result = test_sarvam()
    
    # Print Whisper results from previous test
    print_whisper_results()
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY & RECOMMENDATIONS")
    print("="*60)
    
    if sarvam_result:
        sarvam_time = sarvam_result['processing_time']
        whisper_time = 389.77  # From previous test
        
        print(f"⚡ Sarvam.ai: {sarvam_time:.2f}s ({30.0/sarvam_time:.1f}x real-time)")
        print(f"🐌 Whisper:   {whisper_time:.2f}s ({30.0/whisper_time:.2f}x real-time)")
        print(f"🚀 Speed advantage: Sarvam.ai is {whisper_time/sarvam_time:.1f}x faster")
        
        print(f"\n💡 RECOMMENDATION:")
        if sarvam_time < 10:
            print(f"   ✅ Stick with Sarvam.ai - it's much faster and optimized for Hindi")
            print(f"   ✅ Cloud processing beats local Whisper on your MacBook Pro")
        else:
            print(f"   ⚠️  Both are slow, but Sarvam.ai is still better for Hindi")
    else:
        print("❌ Could not test Sarvam.ai - API key issue")
        print("🐌 Whisper took 6.5 minutes for 30 seconds of audio")
        print("💡 This confirms Whisper is too slow for practical use")

if __name__ == "__main__":
    main()
