# Sarvam.ai Speech-to-Text Converter with Dual Output System

Convert Hindi/English mixed audio files to text using Sarvam AI's Saarika model with automatic dual output generation.

## 🎉 Major Updates - Dual Output System

- ✅ **NEW: Dual Output System**: Creates both Hindi (Devanagari) and Roman script versions
- ✅ **M4A File Support**: Fixed M4A processing with automatic AAC conversion
- ✅ **Line Break Preservation**: Maintains original formatting in both versions
- ✅ **Clean Text Output**: No more raw API responses in output files
- ✅ **Smart Transliteration**: Hindi → Roman script, English unchanged
- ✅ **Robust Error Handling**: Comprehensive error handling and debugging

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get API Key
1. Visit [Sarvam AI Dashboard](https://dashboard.sarvam.ai/)
2. Sign up or log in
3. Get your API subscription key

### 3. Configure API Key
**Option A: Using Setup Script (Recommended)**
```bash
python setup_api_key.py
```
This creates a `.env` file that the script automatically reads.

**Option B: Environment Variable**
```bash
export SARVAM_API_KEY="your_api_key_here"
```

**Option C: Manual Entry**
The script will prompt for your API key if not found in `.env` or environment variables.

## Usage

### Method 1: Command Line (Recommended)
```bash
python sarvam_stt.py ScreenRecordingAudio.mp3
```

The script will:
- Automatically detect if audio is longer than 30 seconds
- Split long audio into chunks if needed (M4A → AAC conversion)
- Ask you to select language (Hindi by default)
- Create TWO output files:
  - `filename_hindi.txt` - Original with Devanagari script
  - `filename_roman.txt` - Hindi transliterated to Roman script

### Method 2: Interactive Mode
```bash
python sarvam_stt.py
```
Then enter the audio file path when prompted.

### Method 3: Programmatic Usage
```python
from sarvam_stt import SarvamSTT

# Initialize with API key
stt = SarvamSTT("your_api_key")

# Transcribe audio
transcript = stt.transcribe_audio(
    audio_path="ScreenRecordingAudio.mp3",
    language_code="hi-IN",  # Hindi
    output_file="transcript.txt"
)

print(transcript)
```

### Method 4: Clean Existing Transcripts
If you have transcript files with API metadata, clean them:
```bash
python clean_transcript.py your_transcript_file.txt
```
This extracts only the clean transcript text and saves it to a new file.

## Language Options

1. **Hindi (hi-IN)** - Default for Hindi audio
2. **English (en-IN)** - For English audio
3. **Auto-detect (unknown)** - Let AI detect language
4. **Code-mixed** - For mixed Hindi-English speech

## Features

### 🎆 **NEW: Dual Output System**
- ✅ **Two File Formats**: Automatically creates both Hindi and Roman script versions
- ✅ **Smart Transliteration**: Hindi → Roman script using Sarvam.ai API
- ✅ **English Preservation**: English text remains unchanged in Roman version
- ✅ **Line Break Preservation**: Maintains exact formatting in both versions
- ✅ **Chunked Processing**: Handles long texts by splitting into API-compatible chunks

### 🛠️ **Core Features**
- ✅ **M4A File Support**: Fixed M4A processing with automatic AAC conversion
- ✅ **Smart Audio Processing**: Handles both short (<30s) and long audio files
- ✅ **Automatic Chunking**: Splits long audio into optimal chunks for processing
- ✅ **Clean Text Output**: Saves readable transcripts without API metadata
- ✅ **Multiple Language Support**: Hindi, English, auto-detect, code-mixed
- ✅ **Automatic API Key Loading**: Reads from `.env` file automatically
- ✅ **Progress Tracking**: Shows real-time progress for long transcriptions
- ✅ **Automatic Cleanup**: Removes temporary files after processing
- ✅ **Robust Error Handling**: Comprehensive debugging and fallback mechanisms

## File Structure

```
├── sarvam_stt.py          # Main transcription script with clean output
├── setup_api_key.py       # API key configuration helper
├── clean_transcript.py    # Utility to clean existing transcript files
├── example_usage.py       # Usage examples and programmatic interface
├── requirements.txt       # Python dependencies
├── .env                   # API key storage (created by setup script)
└── README_Sarvam.md      # This documentation
```

## Troubleshooting

### Common Errors

1. **403 Forbidden (invalid_api_key_error)**
   - Solution: Check your API key is correct

2. **429 Too Many Requests (insufficient_quota_error)**
   - Solution: Check your API quota or wait before retrying

3. **FFmpeg not found**
   - Solution: Install FFmpeg
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt install ffmpeg
   ```

4. **Audio file not supported**
   - Solution: Convert to MP3 or WAV format

### Tips for Better Results

- Use clear audio with minimal background noise
- Ensure good audio quality (not too compressed)
- For conference calls, try to use the highest quality recording
- If transcription quality is poor, try different language settings

## Support

- **Documentation**: [docs.sarvam.ai](https://docs.sarvam.ai)
- **Community**: [Discord Community](https://discord.gg/hTuVuPNF)

## Example Output

### Console Output:
```
=== Sarvam.ai Speech-to-Text Converter ===

Starting transcription...
Input: Anshuman-30Jul2025.m4a
Output: Anshuman-30Jul2025_transcript
--------------------------------------------------
Audio duration: 1247.83 seconds
Audio is longer than 30 seconds, splitting into chunks...
Converting M4A chunks to AAC format for API compatibility...
Generated 43 audio chunks
Transcribing 43 chunks...
Processing chunk 1/43: Anshuman-30Jul2025_000.aac
✓ Chunk 1 transcribed successfully
Processing chunk 2/43: Anshuman-30Jul2025_001.aac
✓ Chunk 2 transcribed successfully
...
Cleaning up temporary chunks...
Transcription completed successfully!
✓ Hindi transcript saved to: Anshuman-30Jul2025_transcript_hindi.txt

Creating Roman script version...
🔄 Text too long (15,847 chars), splitting into chunks...
Split into 18 chunks
Processing chunk 1/18 (885 chars)...
Processing chunk 2/18 (892 chars)...
...
✓ All chunks processed successfully
✓ Roman script transcript saved to: Anshuman-30Jul2025_transcript_roman.txt

🎉 Both versions created successfully!
   Hindi version: Anshuman-30Jul2025_transcript_hindi.txt
   Roman version: Anshuman-30Jul2025_transcript_roman.txt

==================================================
TRANSCRIPTION RESULT (Hindi Version):
==================================================
game of chance versus game of skill.
Start with that.
That's the heading.
गुड बी चांस बीइंग द नेचर ऑफ कार्ड्स डेल्ट।
==================================================
```

### Dual Output Files:

#### Hindi Version (`filename_hindi.txt`):
```
game of chance versus game of skill.
Start with that.
That's the heading.
One.
Game of chance is one how will you define it?
Is where no skill is involved and depends on the outcome.
often uncertain.
Something like that.
While a game of skill
गुड बी चांस बीइंग द नेचर ऑफ कार्ड्स डेल्ट।
रिफर टू लक्ष्मण सेश कोट दैट।
```

#### Roman Version (`filename_roman.txt`):
```
Game of chance versus game of skill.
Start with that.
That's the heading.
One.
Game of chance is one how will you define it?
Is where no skill is involved and depends on the outcome.
Often uncertain.
Something like that.
While a game of skill
Good be chance being the nature of cards dealt.
Refer to Laxman Sesh Coat that.
```

### 🎆 **Key Improvements:**
- ✅ **Dual Output**: Both Devanagari and Roman script versions
- ✅ **M4A Support**: Automatic conversion to AAC format
- ✅ **Line Preservation**: Exact formatting maintained in both files
- ✅ **Smart Transliteration**: Hindi → Roman, English unchanged
- ✅ **No API Metadata**: Clean, readable text output
- ✅ **Production Ready**: Robust error handling and debugging
