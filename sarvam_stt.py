#!/usr/bin/env python3
"""
Sarvam.ai Speech-to-Text Script with Dual Output System
Converts Hindi/English mixed audio files to text using Sarvam AI's Saarika model

MAJOR IMPROVEMENTS & FIXES:

1. M4A FILE PROCESSING FIX:
   - Fixed M4A files failing with "Invalid file type: audio/mp4a-latm" error
   - Solution: Convert M4A chunks to AAC format during splitting for API compatibility

2. TRANSCRIPT EXTRACTION IMPROVEMENTS:
   - Fixed raw API responses appearing in output files instead of clean text
   - Enhanced parsing with multiple fallback patterns and proper error handling
   - Clean transcript output with proper formatting and line breaks

3. DUAL OUTPUT SYSTEM:
   - NEW FEATURE: Creates both Hindi (Devanagari) and Roman script versions
   - Hindi version: Original transcript with Devanagari script
   - Roman version: Hindi text transliterated to Roman script (English unchanged)
   - Uses Sarvam.ai transliteration API with chunked processing for long texts

4. LINE BREAK PRESERVATION:
   - Fixed transliteration API removing line breaks from responses
   - Solution: Placeholder system (<LINEBREAK>) to preserve original formatting
   - Maintains exact line structure and readability in both versions

5. ROBUST ERROR HANDLING:
   - Comprehensive error handling for API failures and network issues
   - Graceful fallbacks and meaningful error messages
   - Debug output for troubleshooting

SUPPORTED FORMATS: M4A, AAC, WAV, MP3
OUTPUT: Two files per audio - *_hindi.txt and *_roman.txt
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
        
        # CRITICAL FIX: M4A to AAC conversion for API compatibility
        # Problem: M4A files were being split with MIME type "audio/mp4a-latm" 
        # which Sarvam.ai API rejects with "Invalid file type" error
        # Solution: Convert M4A chunks to standard AAC format during splitting
        # This ensures all chunks are in a format the API accepts
        if ext == ".m4a":
            output_ext = ".aac"  # Change extension from .m4a to .aac
            codec = "aac"       # Use AAC codec for encoding
            print("Converting M4A chunks to AAC format for API compatibility...")
        elif ext == ".wav":
            output_ext = ext
            codec = "pcm_s16le"
        elif ext == ".aac":
            output_ext = ext
            codec = "aac"
        else:
            output_ext = ".mp3"
            codec = "libmp3lame"
        
        output_pattern = os.path.join(output_dir, f"{base_name}_%03d{output_ext}")
        
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
        print(f"Command: {' '.join(command)}")
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
            if f.endswith(output_ext) and f.startswith(base_name)
        ])
        
        print(f"Generated {len(output_files)} audio chunks")
        return output_files
    
    def extract_transcript_text(self, api_response):
        """
        Extract clean transcript text from API response
        
        CRITICAL FIX: Improved transcript extraction to avoid raw API responses
        Problem: Method was returning entire raw API response when parsing failed,
        causing output files to contain request_id and other API metadata
        Solution: Enhanced parsing with multiple fallback patterns and proper error handling
        """
        # IMPROVEMENT: First try to access the transcript attribute directly
        # This is the most reliable method when the API response object has the attribute
        try:
            if hasattr(api_response, 'transcript'):
                transcript = api_response.transcript
                if transcript:
                    return transcript.strip()
        except Exception as e:
            print(f"Warning: Could not access transcript attribute: {e}")
        
        # Fallback to string parsing
        response_str = str(api_response)
        
        # Extract transcript content using string parsing
        try:
            # Look for transcript='...' or transcript="..." pattern
            patterns = [
                ("transcript='", "' timestamps="),
                ("transcript='", "' diarized_transcript="),
                ("transcript='", "' language_code="),
                ('transcript="', '" timestamps='),
                ('transcript="', '" diarized_transcript='),
                ('transcript="', '" language_code=')
            ]
            
            for start_marker, end_marker in patterns:
                start_idx = response_str.find(start_marker)
                if start_idx != -1:
                    start_idx += len(start_marker)
                    end_idx = response_str.find(end_marker, start_idx)
                    
                    if end_idx != -1:
                        transcript = response_str[start_idx:end_idx]
                        # Replace \n with actual newlines and clean up
                        transcript = transcript.replace('\\n', '\n')
                        transcript = transcript.strip()
                        if transcript:  # Only return if we got actual content
                            return transcript
            
            # If no pattern matched, try to extract just the text content
            print(f"Warning: Could not parse transcript using standard patterns")
            print(f"Raw response: {response_str[:200]}...")  # Show first 200 chars for debugging
            return "[Error: Could not extract transcript text]"
            
        except Exception as e:
            print(f"Error parsing transcript: {e}")
            return "[Error: Could not extract transcript text]"
    
    def transliterate_to_roman(self, text):
        """
        Convert Hindi text to Roman script using Sarvam.ai transliteration API
        
        NEW FEATURE: Dual output system for Hindi and Roman script versions
        - Creates both Devanagari and Roman script versions of transcripts
        - Handles long text by splitting into chunks under 1000 characters (API limit)
        - Preserves English text unchanged while transliterating Hindi text
        
        CRITICAL FIX: Line break preservation using placeholder system
        Problem: Sarvam.ai transliteration API removes line breaks from responses
        Solution: Replace \n with <LINEBREAK> placeholders before API call,
        then restore them after transliteration to maintain original formatting
        """
        print(f"\n=== TRANSLITERATION DEBUG ===")
        print(f"Input text length: {len(text) if text else 0}")
        print(f"Input text preview: {text[:100] if text else 'None'}...")
        
        if not text or text.startswith("[Error:"):
            print("Skipping transliteration: empty or error text")
            return text
        
        # CRITICAL FIX: Replace line breaks with placeholders to preserve structure
        # The Sarvam.ai transliteration API treats line breaks as whitespace and removes them
        # We use <LINEBREAK> placeholders to preserve the original formatting
        text_with_placeholders = text.replace('\n', ' <LINEBREAK> ')
        
        # Split text into chunks of max 900 characters (leaving buffer for safety)
        max_chunk_size = 900
        
        if len(text_with_placeholders) <= max_chunk_size:
            # Single chunk processing
            result = self._transliterate_chunk(text_with_placeholders)
            # Restore line breaks
            return result.replace(' <LINEBREAK> ', '\n').replace('<LINEBREAK>', '\n')
        else:
            # Multi-chunk processing
            print(f"🔄 Text too long ({len(text_with_placeholders)} chars), splitting into chunks...")
            
            # Simple approach: split by character count and preserve structure
            chunks = []
            start = 0
            while start < len(text_with_placeholders):
                end = start + max_chunk_size
                if end >= len(text_with_placeholders):
                    chunks.append(text_with_placeholders[start:])
                    break
                
                # Try to find a good break point (space, <LINEBREAK>, or punctuation)
                break_point = end
                for i in range(end, max(start, end - 100), -1):
                    if text_with_placeholders[i] in [' ', '.', '!', '?', ','] or text_with_placeholders[i:i+11] == '<LINEBREAK>':
                        break_point = i + 1
                        break
                
                chunks.append(text_with_placeholders[start:break_point])
                start = break_point
            
            print(f"Split into {len(chunks)} chunks")
            
            transliterated_chunks = []
            for i, chunk in enumerate(chunks, 1):
                print(f"Processing chunk {i}/{len(chunks)} ({len(chunk)} chars)...")
                transliterated_chunk = self._transliterate_chunk(chunk)
                transliterated_chunks.append(transliterated_chunk)
            
            result = "".join(transliterated_chunks)
            # Restore line breaks
            result = result.replace(' <LINEBREAK> ', '\n').replace('<LINEBREAK>', '\n')
            print(f"✓ All chunks processed successfully")
            print(f"Final output length: {len(result)}")
            print(f"=== END TRANSLITERATION DEBUG ===\n")
            return result
    
    def _split_text_for_transliteration(self, text, max_size):
        """
        Split text into chunks while preserving line breaks and formatting
        Returns list of (chunk, separator) tuples
        """
        chunks_with_separators = []
        current_chunk = ""
        
        # Split text into lines to preserve line breaks
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_with_newline = line + ('\n' if i < len(lines) - 1 else '')
            
            # If adding this line would exceed the limit
            if len(current_chunk) + len(line_with_newline) > max_size:
                if current_chunk:
                    # Remove trailing newline from chunk and store it as separator
                    if current_chunk.endswith('\n'):
                        chunks_with_separators.append((current_chunk[:-1], '\n'))
                    else:
                        chunks_with_separators.append((current_chunk, ''))
                    current_chunk = ""
                
                # If the line itself is too long, split it by words
                if len(line_with_newline) > max_size:
                    words = line.split()
                    for j, word in enumerate(words):
                        word_with_space = word + (' ' if j < len(words) - 1 else '')
                        if len(current_chunk) + len(word_with_space) > max_size:
                            if current_chunk:
                                chunks_with_separators.append((current_chunk.rstrip(), ''))
                                current_chunk = word_with_space
                            else:
                                # Single word is too long, just add it
                                chunks_with_separators.append((word, ''))
                        else:
                            current_chunk += word_with_space
                    
                    # Add newline if this was not the last line
                    if i < len(lines) - 1:
                        current_chunk += '\n'
                else:
                    current_chunk = line_with_newline
            else:
                current_chunk += line_with_newline
        
        if current_chunk:
            # Remove trailing newline from last chunk
            if current_chunk.endswith('\n'):
                chunks_with_separators.append((current_chunk[:-1], ''))
            else:
                chunks_with_separators.append((current_chunk, ''))
        
        return chunks_with_separators
    
    def _transliterate_chunk(self, chunk):
        """
        Transliterate a single chunk of text
        """
        try:
            response = self.client.text.transliterate(
                input=chunk,
                source_language_code="hi-IN",
                target_language_code="en-IN",
                spoken_form=True,
            )
            
            if hasattr(response, 'transliterated_text'):
                return response.transliterated_text
            else:
                print(f"✗ No transliterated_text in response: {response}")
                return chunk
                
        except Exception as e:
            print(f"✗ Chunk transliteration failed: {e}")
            return chunk
    
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
            if transcript and not transcript.startswith("[Error:"):
                # Clean up the transcript
                transcript = transcript.strip()
                if transcript:  # Only add non-empty transcripts
                    full_transcript.append(transcript)
                    print(f"✓ Chunk {idx} transcribed successfully: {transcript[:50]}...")
            else:
                print(f"✗ Failed to transcribe chunk {idx}: {transcript}")
        
        if not full_transcript:
            return "[Error: No chunks were successfully transcribed]"
        
        # Combine transcripts with proper formatting
        import re
        
        # Join chunks with line breaks for better readability
        combined_chunks = []
        for i, transcript in enumerate(full_transcript):
            # Clean up individual transcript
            transcript = transcript.strip()
            
            # Add chunk number as a subtle marker every 10 chunks for reference
            if i % 10 == 0 and len(full_transcript) > 10:
                combined_chunks.append(f"\n--- Chunk {i+1}-{min(i+10, len(full_transcript))} ---")
            
            combined_chunks.append(transcript)
        
        # Join with double line breaks between chunks for readability
        combined = "\n\n".join(combined_chunks).strip()
        
        # Clean up formatting issues while preserving intentional line breaks
        combined = re.sub(r' +', ' ', combined)  # Replace multiple spaces with single space
        combined = combined.replace(' .', '.').replace(' ,', ',')  # Fix punctuation spacing
        combined = combined.replace(' ?', '?').replace(' !', '!')  # Fix other punctuation
        
        # Add some structure by breaking on sentence endings followed by capitals
        combined = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\2', combined)
        
        # Break long lines at natural pause points
        combined = re.sub(r'([.!?])\s+', r'\1\n', combined)
        
        # Clean up excessive line breaks
        combined = re.sub(r'\n{3,}', '\n\n', combined)
        
        return combined
    
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
            
            # NEW FEATURE: Create both Hindi and Roman script versions
            # This dual output system provides users with two formats:
            # 1. Hindi version: Original transcript with Devanagari script
            # 2. Roman version: Hindi text transliterated to Roman script (English unchanged)
            if output_file:
                # Generate file names for both versions with clear suffixes
                base_name = os.path.splitext(output_file)[0]
                hindi_file = f"{base_name}_hindi.txt"  # Original Devanagari script
                roman_file = f"{base_name}_roman.txt"  # Roman transliteration
                
                # Save Hindi version
                with open(hindi_file, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                print(f"✓ Hindi transcript saved to: {hindi_file}")
                
                # Create and save Roman script version
                print("\nCreating Roman script version...")
                roman_transcript = self.transliterate_to_roman(transcript)
                
                with open(roman_file, 'w', encoding='utf-8') as f:
                    f.write(roman_transcript)
                print(f"✓ Roman script transcript saved to: {roman_file}")
                
                print(f"\n🎉 Both versions created successfully!")
                print(f"   Hindi version: {hindi_file}")
                print(f"   Roman version: {roman_file}")
            
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
                    # Create both Hindi and Roman script versions for code-mixed too
                    base_name = os.path.splitext(output_file)[0]
                    hindi_file = f"{base_name}_hindi.txt"
                    roman_file = f"{base_name}_roman.txt"
                    
                    # Save Hindi version
                    with open(hindi_file, 'w', encoding='utf-8') as f:
                        f.write(transcript)
                    print(f"✓ Hindi transcript saved to: {hindi_file}")
                    
                    # Create and save Roman script version
                    print("\nCreating Roman script version...")
                    roman_transcript = stt.transliterate_to_roman(transcript)
                    
                    with open(roman_file, 'w', encoding='utf-8') as f:
                        f.write(roman_transcript)
                    print(f"✓ Roman script transcript saved to: {roman_file}")
        except Exception as e:
            print(f"Error in code-mixed transcription: {e}")
            transcript = None
    
    if transcript:
        print("\n" + "="*50)
        print("TRANSCRIPTION RESULT (Hindi Version):")
        print("="*50)
        print(transcript)
        print("="*50)
        
        # Show file information
        base_name = os.path.splitext(output_file)[0]
        print(f"\n🎉 Transcription completed! Two versions created:")
        print(f"   🇦🇳 Hindi version: {base_name}_hindi.txt")
        print(f"   🅰️ Roman version: {base_name}_roman.txt")
    else:
        print("Transcription failed. Please check your API key and audio file.")

if __name__ == "__main__":
    main()
