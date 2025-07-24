#!/usr/bin/env python3
"""
Sarvam.ai Batch Speech-to-Text Script with Speaker Diarization
Processes audio files using Sarvam AI's Batch API for speaker identification
Supports files up to 1 hour with automatic splitting for longer files
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from sarvamai import SarvamAI


class SarvamBatchSTT:
    def __init__(self, api_key):
        """Initialize Sarvam AI client with API key"""
        self.client = SarvamAI(api_subscription_key=api_key)
        self.max_duration_ms = 60 * 60 * 1000  # 1 hour in milliseconds
        
    def get_audio_duration_ms(self, audio_path: str) -> int:
        """Get audio duration in milliseconds using ffprobe"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration_seconds = float(result.stdout.strip())
            return int(duration_seconds * 1000)  # Convert to milliseconds
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0
    
    def split_audio_if_needed(self, audio_path: str) -> List[str]:
        """Split audio file into 1-hour chunks if longer than 1 hour"""
        duration_ms = self.get_audio_duration_ms(audio_path)
        
        if duration_ms <= self.max_duration_ms:
            return [audio_path]  # No splitting needed
        
        print(f"Audio duration: {duration_ms/1000/60:.1f} minutes")
        print("Audio is longer than 1 hour, splitting into chunks...")
        
        # Create chunks directory
        base_name = Path(audio_path).stem
        chunks_dir = Path("batch_chunks")
        chunks_dir.mkdir(exist_ok=True)
        
        # Split audio using ffmpeg
        chunk_duration_seconds = self.max_duration_ms // 1000  # Convert to seconds
        ext = Path(audio_path).suffix.lower()
        output_pattern = chunks_dir / f"{base_name}_chunk_%02d{ext}"
        
        # Choose codec based on file type
        codec = "pcm_s16le" if ext == ".wav" else "libmp3lame"
        
        cmd = [
            "ffmpeg", "-i", audio_path,
            "-f", "segment", "-segment_time", str(chunk_duration_seconds),
            "-c:a", codec, "-y", str(output_pattern)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("Audio splitting completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error splitting audio: {e}")
            return [audio_path]  # Return original file if splitting fails
        
        # Get list of generated chunks
        chunk_paths = sorted([str(f) for f in chunks_dir.glob(f"{base_name}_chunk_*{ext}")])
        
        for chunk_path in chunk_paths:
            print(f"Created chunk: {chunk_path}")
        
        return chunk_paths
    
    def process_batch_transcription(self, audio_paths: List[str], language_code: str = "hi-IN", 
                                  num_speakers: Optional[int] = None, improve_diarization: bool = True) -> Dict:
        """Process audio files using Sarvam Batch API with diarization"""
        print(f"Processing {len(audio_paths)} audio file(s) with Batch API...")
        
        try:
            # Create batch job with diarization
            job_params = {
                "language_code": language_code,
                "model": "saarika:v2.5",
                "with_timestamps": True,
                "with_diarization": True,
            }
            
            if num_speakers:
                job_params["num_speakers"] = num_speakers
            else:
                # Default to 2 speakers for better diarization when not specified
                job_params["num_speakers"] = 2
            
            print("Creating batch transcription job...")
            job = self.client.speech_to_text_job.create_job(**job_params)
            
            # Upload files
            print("Uploading audio files...")
            job.upload_files(file_paths=audio_paths)
            
            # Start job
            print("Starting transcription job...")
            job.start()
            
            # Wait for completion
            print("Waiting for transcription to complete...")
            start_time = time.time()
            
            final_status = job.wait_until_complete()
            
            processing_time = time.time() - start_time
            print(f"Job completed in {processing_time:.2f} seconds")
            
            if job.is_failed():
                print("Transcription job failed!")
                return {"success": False, "error": "Job failed"}
            
            # Download results
            output_dir = Path(f"batch_output_{job.job_id}")
            output_dir.mkdir(exist_ok=True)
            
            print(f"Downloading results to {output_dir}...")
            job.download_outputs(output_dir=str(output_dir))
            
            # Parse results
            results = self.parse_transcription_results(output_dir, improve_diarization)
            results["job_id"] = job.job_id
            results["processing_time"] = processing_time
            results["success"] = True
            
            return results
            
        except Exception as e:
            print(f"Error in batch transcription: {e}")
            return {"success": False, "error": str(e)}
    
    def improve_speaker_consistency(self, entries: List[Dict]) -> List[Dict]:
        """Post-process diarization to reduce speaker mixing"""
        if len(entries) < 3:
            return entries
        
        improved_entries = entries.copy()
        
        # Rule 1: If a speaker has very short segments (< 2 seconds) between longer segments 
        # of another speaker, reassign to the dominant speaker
        for i in range(1, len(improved_entries) - 1):
            current = improved_entries[i]
            prev_entry = improved_entries[i-1]
            next_entry = improved_entries[i+1]
            
            current_duration = current.get("end_time_seconds", 0) - current.get("start_time_seconds", 0)
            
            # If current segment is very short (< 2 seconds) and surrounded by same speaker
            if (current_duration < 2.0 and 
                prev_entry["speaker_id"] == next_entry["speaker_id"] and 
                current["speaker_id"] != prev_entry["speaker_id"]):
                
                print(f"Reassigning short segment from {current['speaker_id']} to {prev_entry['speaker_id']}")
                improved_entries[i]["speaker_id"] = prev_entry["speaker_id"]
        
        # Rule 2: Merge consecutive segments from same speaker
        merged_entries = []
        current_merged = None
        
        for entry in improved_entries:
            if (current_merged is None or 
                current_merged["speaker_id"] != entry["speaker_id"] or
                entry.get("start_time_seconds", 0) - current_merged.get("end_time_seconds", 0) > 3.0):
                
                if current_merged:
                    merged_entries.append(current_merged)
                current_merged = entry.copy()
            else:
                # Merge with previous segment
                current_merged["transcript"] += " " + entry["transcript"]
                current_merged["end_time_seconds"] = entry.get("end_time_seconds", current_merged.get("end_time_seconds", 0))
        
        if current_merged:
            merged_entries.append(current_merged)
        
        return merged_entries
    
    def parse_transcription_results(self, output_dir: Path, improve_diarization: bool = True) -> Dict:
        """Parse downloaded transcription results"""
        results = {
            "transcriptions": {},
            "conversations": {},
            "speaker_timings": {}
        }
        
        # Find all JSON result files
        json_files = list(output_dir.glob("*.json"))
        
        if not json_files:
            print(f"No JSON files found in {output_dir}")
            return results
        
        for json_file in json_files:
            try:
                print(f"Processing result file: {json_file.name}")
                
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                file_stem = json_file.stem
                
                # Store raw transcription data
                results["transcriptions"][file_stem] = data
                
                # Parse diarized transcript
                diarized = data.get("diarized_transcript", {}).get("entries", [])
                
                # Improve speaker consistency if requested
                if diarized and improve_diarization:
                    print(f"Applying speaker consistency improvements...")
                    original_segments = len(diarized)
                    diarized = self.improve_speaker_consistency(diarized)
                    print(f"Segments after improvement: {len(diarized)} (was {original_segments})")
                
                if diarized:
                    # Create conversation format
                    conversation_lines = []
                    speaker_times = {}
                    
                    for entry in diarized:
                        speaker = entry["speaker_id"]
                        text = entry["transcript"]
                        start_time = entry.get("start_time_seconds", 0)
                        end_time = entry.get("end_time_seconds", 0)
                        
                        # Format: [MM:SS] SPEAKER: text
                        time_str = f"[{int(start_time//60):02d}:{int(start_time%60):02d}]"
                        conversation_lines.append(f"{time_str} {speaker}: {text}")
                        
                        # Calculate speaker timing
                        duration = end_time - start_time
                        speaker_times[speaker] = speaker_times.get(speaker, 0.0) + duration
                    
                    # Save conversation format
                    conversation_text = "\n".join(conversation_lines)
                    conversation_file = output_dir / f"{file_stem}_conversation.txt"
                    
                    with open(conversation_file, "w", encoding="utf-8") as f:
                        f.write(conversation_text)
                    
                    results["conversations"][file_stem] = {
                        "text": conversation_text,
                        "file_path": str(conversation_file)
                    }
                    
                    # Save speaker timing analysis
                    timing_file = output_dir / f"{file_stem}_speaker_timing.json"
                    timing_data = {
                        "total_speakers": len(speaker_times),
                        "speaker_times_seconds": speaker_times,
                        "speaker_percentages": {}
                    }
                    
                    total_time = sum(speaker_times.values())
                    if total_time > 0:
                        for speaker, time_sec in speaker_times.items():
                            timing_data["speaker_percentages"][speaker] = (time_sec / total_time) * 100
                    
                    with open(timing_file, "w", encoding="utf-8") as f:
                        json.dump(timing_data, f, indent=2)
                    
                    results["speaker_timings"][file_stem] = timing_data
                    
                    print(f"✓ Processed {file_stem}: {len(diarized)} segments, {len(speaker_times)} speakers")
                
                else:
                    # Fallback for non-diarized results
                    transcript = data.get("transcript", "")
                    conversation_file = output_dir / f"{file_stem}_transcript.txt"
                    
                    with open(conversation_file, "w", encoding="utf-8") as f:
                        f.write(transcript)
                    
                    results["conversations"][file_stem] = {
                        "text": transcript,
                        "file_path": str(conversation_file)
                    }
                    
                    print(f"✓ Processed {file_stem}: No diarization data, saved transcript only")
                    
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
        
        return results
    
    def print_results_summary(self, results: Dict):
        """Print a summary of transcription results"""
        if not results.get("success"):
            print(f"❌ Transcription failed: {results.get('error', 'Unknown error')}")
            return
        
        print("\n" + "="*60)
        print("BATCH TRANSCRIPTION RESULTS SUMMARY")
        print("="*60)
        
        print(f"Job ID: {results.get('job_id', 'N/A')}")
        print(f"Processing Time: {results.get('processing_time', 0):.2f} seconds")
        print(f"Files Processed: {len(results['transcriptions'])}")
        
        for file_stem, timing_data in results["speaker_timings"].items():
            print(f"\n📁 File: {file_stem}")
            print(f"   Speakers: {timing_data['total_speakers']}")
            
            for speaker, percentage in timing_data["speaker_percentages"].items():
                time_sec = timing_data["speaker_times_seconds"][speaker]
                print(f"   {speaker}: {time_sec:.1f}s ({percentage:.1f}%)")
        
        print("\n📄 Output Files:")
        for file_stem, conv_data in results["conversations"].items():
            print(f"   Conversation: {conv_data['file_path']}")
        
        print("="*60)


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
    print("=== Sarvam.ai Batch Speech-to-Text with Speaker Diarization ===\n")
    
    # Load .env file
    load_env_file()
    
    # Get API key
    api_key = os.getenv('SARVAM_API_KEY')
    if not api_key:
        api_key = input("Enter your Sarvam AI API key: ").strip()
        if not api_key:
            print("Error: API key is required")
            sys.exit(1)
    
    # Initialize Batch STT client
    batch_stt = SarvamBatchSTT(api_key)
    
    # Get audio file path
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = input("Enter path to your audio file: ").strip()
    
    if not audio_file or not Path(audio_file).exists():
        print("Error: Valid audio file path is required")
        sys.exit(1)
    
    # Language selection
    print("\nSupported languages:")
    print("1. Hindi (hi-IN) - Default")
    print("2. English (en-IN)")
    print("3. Auto-detect")
    
    lang_choice = input("Select language (1-3, default=1): ").strip()
    
    language_map = {
        "1": "hi-IN",
        "2": "en-IN", 
        "3": "auto"
    }
    
    language_code = language_map.get(lang_choice, "hi-IN")
    
    # Number of speakers (optional)
    num_speakers_input = input("Expected number of speakers (default=2, press Enter for default): ").strip()
    num_speakers = None
    if num_speakers_input.isdigit():
        num_speakers = int(num_speakers_input)
        print(f"Using {num_speakers} speakers for diarization")
    else:
        print("Using default: 2 speakers for diarization")
    
    # Speaker consistency improvement option
    improve_choice = input("Apply speaker consistency improvements? (Y/n, default=Y): ").strip().lower()
    improve_diarization = improve_choice != 'n'
    
    print(f"\nStarting batch transcription...")
    print(f"Input: {audio_file}")
    print(f"Language: {language_code}")
    if num_speakers:
        print(f"Expected speakers: {num_speakers}")
    print(f"Speaker improvements: {'Enabled' if improve_diarization else 'Disabled'}")
    print("-" * 50)
    
    # Split audio if needed
    audio_paths = batch_stt.split_audio_if_needed(audio_file)
    
    # Process transcription
    results = batch_stt.process_batch_transcription(
        audio_paths, 
        language_code=language_code,
        num_speakers=num_speakers,
        improve_diarization=improve_diarization
    )
    
    # Clean up chunks if created
    if len(audio_paths) > 1 and Path("batch_chunks").exists():
        print("Cleaning up temporary chunks...")
        for chunk_path in audio_paths:
            try:
                os.remove(chunk_path)
            except:
                pass
        try:
            os.rmdir("batch_chunks")
        except:
            pass
    
    # Display results
    batch_stt.print_results_summary(results)
    
    # Show sample conversation
    if results.get("success") and results["conversations"]:
        first_file = next(iter(results["conversations"].values()))
        conversation_text = first_file["text"]
        
        print(f"\n📝 SAMPLE CONVERSATION (first 500 characters):")
        print("-" * 50)
        print(conversation_text[:500] + ("..." if len(conversation_text) > 500 else ""))
        print("-" * 50)
        
        print(f"\n✅ Full results saved in the output directory")
        print("Check the generated files for complete transcription and analysis!")


if __name__ == "__main__":
    main()
