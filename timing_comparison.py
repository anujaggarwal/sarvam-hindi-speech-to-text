#!/usr/bin/env python3
"""
Timing comparison between Whisper and Sarvam.ai
Run this to get actual performance metrics on your MacBook Pro
"""

import time
import os
from pathlib import Path

def test_sarvam_timing(audio_file):
    """Test Sarvam.ai transcription timing"""
    try:
        from sarvam_stt import transcribe_audio_file
        
        print("=== TESTING SARVAM.AI ===")
        start_time = time.time()
        
        # Use your existing Sarvam function
        result = transcribe_audio_file(audio_file, language="hi")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            'service': 'Sarvam.ai',
            'processing_time': processing_time,
            'text_length': len(result) if result else 0,
            'success': True
        }
        
    except Exception as e:
        return {
            'service': 'Sarvam.ai',
            'processing_time': 0,
            'text_length': 0,
            'success': False,
            'error': str(e)
        }

def test_whisper_timing(audio_file, model_size="medium"):
    """Test Whisper transcription timing"""
    try:
        from stt_whisper_optimized import OptimizedWhisperSTT
        
        print(f"=== TESTING WHISPER ({model_size.upper()}) ===")
        
        # Model loading time
        load_start = time.time()
        stt = OptimizedWhisperSTT(model_size)
        load_time = time.time() - load_start
        
        # Transcription time
        result = stt.transcribe_with_timing(audio_file)
        
        return {
            'service': f'Whisper-{model_size}',
            'model_load_time': load_time,
            'processing_time': result['processing_time'],
            'total_time': load_time + result['processing_time'],
            'text_length': len(result['text']),
            'speed_ratio': result['speed_ratio'],
            'success': True
        }
        
    except Exception as e:
        return {
            'service': f'Whisper-{model_size}',
            'model_load_time': 0,
            'processing_time': 0,
            'total_time': 0,
            'text_length': 0,
            'success': False,
            'error': str(e)
        }

def run_comparison(audio_file):
    """Run complete timing comparison"""
    
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    # Get file size for reference
    file_size = os.path.getsize(audio_file) / (1024 * 1024)  # MB
    print(f"📁 Testing file: {audio_file}")
    print(f"📊 File size: {file_size:.2f} MB")
    print("="*70)
    
    results = []
    
    # Test Sarvam.ai
    sarvam_result = test_sarvam_timing(audio_file)
    results.append(sarvam_result)
    
    # Test Whisper models
    for model in ["small", "medium"]:
        whisper_result = test_whisper_timing(audio_file, model)
        results.append(whisper_result)
    
    # Print comparison table
    print("\n" + "="*70)
    print("🏁 PERFORMANCE COMPARISON RESULTS")
    print("="*70)
    print(f"{'Service':<15} {'Load Time':<10} {'Process Time':<12} {'Total Time':<11} {'Speed':<8} {'Quality'}")
    print("-"*70)
    
    for result in results:
        if result['success']:
            service = result['service']
            load_time = result.get('model_load_time', 0)
            process_time = result['processing_time']
            total_time = result.get('total_time', process_time)
            speed = result.get('speed_ratio', 'N/A')
            quality = result['text_length']
            
            print(f"{service:<15} {load_time:<10.2f} {process_time:<12.2f} {total_time:<11.2f} {speed:<8} {quality} chars")
        else:
            print(f"{result['service']:<15} ❌ ERROR: {result.get('error', 'Unknown')}")
    
    print("\n" + "="*70)
    print("📈 RECOMMENDATIONS:")
    
    # Find fastest successful result
    successful_results = [r for r in results if r['success']]
    if successful_results:
        fastest = min(successful_results, key=lambda x: x.get('total_time', x['processing_time']))
        print(f"🚀 Fastest: {fastest['service']} ({fastest.get('total_time', fastest['processing_time']):.2f}s)")
        
        # Quality vs Speed analysis
        sarvam = next((r for r in successful_results if 'Sarvam' in r['service']), None)
        if sarvam:
            print(f"☁️  Sarvam.ai: {sarvam['processing_time']:.2f}s (cloud-based, optimized for Hindi)")
            
        whisper_results = [r for r in successful_results if 'Whisper' in r['service']]
        if whisper_results:
            best_whisper = min(whisper_results, key=lambda x: x['total_time'])
            print(f"🖥️  Best Whisper: {best_whisper['service']} - {best_whisper['total_time']:.2f}s total")
            print(f"   (includes {best_whisper.get('model_load_time', 0):.2f}s model loading)")

if __name__ == "__main__":
    # Test with your audio file
    test_files = [
        "ScreenRecordingAudio.mp3",
        "trimmed_audio.mp3",
        # Add other test files here
    ]
    
    for audio_file in test_files:
        if os.path.exists(audio_file):
            print(f"\n🎵 Testing with: {audio_file}")
            run_comparison(audio_file)
            break
    else:
        print("❌ No test audio files found!")
        print("Available files:")
        for f in os.listdir("."):
            if f.endswith(('.mp3', '.wav', '.m4a')):
                print(f"  - {f}")
