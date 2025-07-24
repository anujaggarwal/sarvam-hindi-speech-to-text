import whisper
import os
import time
import subprocess
from pathlib import Path

class OptimizedWhisperSTT:
    def __init__(self, model_size="medium"):
        """
        Initialize Whisper model once for reuse
        model_size options: tiny, small, medium, large, large-v2, large-v3
        """
        print(f"Loading Whisper {model_size} model...")
        start_time = time.time()
        
        # Load model with optimizations for MacBook Pro
        self.model = whisper.load_model(
            model_size,
            device="cpu",  # MacBook Pro M-series can use MPS, but CPU is more stable
            download_root=None,
            in_memory=True
        )
        
        load_time = time.time() - start_time
        print(f"Model loaded in {load_time:.2f} seconds")
        
    def preprocess_audio(self, input_file, output_file=None):
        """
        Convert audio to optimal format for Whisper (16kHz WAV)
        """
        if output_file is None:
            output_file = input_file.replace('.mp3', '_processed.wav')
            
        command = [
            "ffmpeg", "-y",  # -y to overwrite existing files
            "-i", input_file,
            "-ar", "16000",  # 16kHz sample rate (Whisper's native)
            "-ac", "1",      # Mono channel
            "-c:a", "pcm_s16le",  # 16-bit PCM
            output_file
        ]
        
        try:
            subprocess.run(command, check=True, capture_output=True)
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"Error preprocessing audio: {e.stderr.decode()}")
            return input_file  # Return original if preprocessing fails
    
    def transcribe_with_timing(self, file_path, language="hi", output_path=None):
        """
        Transcribe audio with detailed timing information
        """
        print(f"Starting transcription of: {file_path}")
        
        # Preprocess audio for better performance
        processed_file = self.preprocess_audio(file_path)
        
        # Start timing
        start_time = time.time()
        
        # Transcribe with optimized parameters
        result = self.model.transcribe(
            processed_file,
            language=language,
            fp16=False,  # Use fp32 for better CPU performance
            beam_size=5,  # Balance between speed and accuracy
            best_of=5,    # Number of candidates to consider
            temperature=0.0,  # Deterministic output
            condition_on_previous_text=True,  # Better context awareness
            verbose=True  # Show progress
        )
        
        transcription_time = time.time() - start_time
        
        # Get audio duration for speed calculation
        audio_duration = result.get('duration', 0)
        speed_ratio = audio_duration / transcription_time if transcription_time > 0 else 0
        
        print(f"\n=== TRANSCRIPTION COMPLETE ===")
        print(f"Audio duration: {audio_duration:.2f} seconds")
        print(f"Processing time: {transcription_time:.2f} seconds")
        print(f"Speed ratio: {speed_ratio:.2f}x real-time")
        print(f"Quality: {len(result['text'])} characters transcribed")
        
        # Save transcription
        if output_path is None:
            output_path = f"whisper_transcription_{int(time.time())}.txt"
            
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"=== WHISPER TRANSCRIPTION ===\n")
            f.write(f"File: {file_path}\n")
            f.write(f"Duration: {audio_duration:.2f}s\n")
            f.write(f"Processing time: {transcription_time:.2f}s\n")
            f.write(f"Speed: {speed_ratio:.2f}x real-time\n")
            f.write(f"Language: {language}\n")
            f.write(f"Model: {self.model.dims.n_mels} mel bins\n")
            f.write("="*50 + "\n\n")
            f.write(result["text"])
            
            # Add detailed segments if available
            if "segments" in result:
                f.write("\n\n=== DETAILED SEGMENTS ===\n")
                for segment in result["segments"]:
                    f.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s]: {segment['text']}\n")
        
        print(f"Transcription saved to: {os.path.abspath(output_path)}")
        
        # Cleanup processed file if it was created
        if processed_file != file_path and os.path.exists(processed_file):
            os.remove(processed_file)
            
        return {
            'text': result['text'],
            'duration': audio_duration,
            'processing_time': transcription_time,
            'speed_ratio': speed_ratio,
            'output_file': output_path
        }

def benchmark_models(audio_file):
    """
    Benchmark different Whisper models on the same audio file
    """
    models_to_test = ["small", "medium"]  # Start with these for speed
    results = {}
    
    for model_size in models_to_test:
        print(f"\n{'='*60}")
        print(f"TESTING MODEL: {model_size.upper()}")
        print(f"{'='*60}")
        
        try:
            stt = OptimizedWhisperSTT(model_size)
            result = stt.transcribe_with_timing(audio_file)
            results[model_size] = result
            
            # Clean up model to free memory
            del stt
            
        except Exception as e:
            print(f"Error with {model_size} model: {e}")
            results[model_size] = {"error": str(e)}
    
    # Print comparison
    print(f"\n{'='*60}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*60}")
    
    for model, result in results.items():
        if "error" not in result:
            print(f"{model.upper():10} | {result['processing_time']:6.2f}s | {result['speed_ratio']:5.2f}x | {len(result['text']):4d} chars")
        else:
            print(f"{model.upper():10} | ERROR: {result['error']}")
    
    return results

if __name__ == "__main__":
    # Test with your audio file
    audio_file = "trimmed_audio_30s.mp3"  # Update this path
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        print("Please update the audio_file variable with the correct path")
        exit(1)
    
    # Option 1: Quick test with medium model
    print("=== QUICK TEST WITH MEDIUM MODEL ===")
    stt = OptimizedWhisperSTT("medium")
    result = stt.transcribe_with_timing(audio_file)
    
    # Option 2: Uncomment to benchmark multiple models
    # print("=== BENCHMARKING MULTIPLE MODELS ===")
    # benchmark_results = benchmark_models(audio_file)
