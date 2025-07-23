# Sarvam.ai Speech-to-Text Converter

Convert Hindi MP3 conference call recordings to clean, readable text using Sarvam AI's Saarika model.

## ✨ Latest Updates

- ✅ **Clean Text Output**: Transcripts now save as clean, readable text without API metadata
- ✅ **Automatic API Key Loading**: Reads API key from `.env` file automatically
- ✅ **Improved Text Formatting**: Proper newline handling for better readability
- ✅ **Transcript Cleanup Utility**: Added tool to clean existing transcript files

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
- Split long audio into chunks if needed
- Ask you to select language (Hindi by default)
- Save transcript to a text file

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

- ✅ **Smart Audio Processing**: Handles both short (<30s) and long audio files
- ✅ **Automatic Chunking**: Splits long audio into optimal chunks for processing
- ✅ **Clean Text Output**: Saves readable transcripts without API metadata
- ✅ **Multiple Language Support**: Hindi, English, auto-detect, code-mixed
- ✅ **Automatic API Key Loading**: Reads from `.env` file automatically
- ✅ **Progress Tracking**: Shows real-time progress for long transcriptions
- ✅ **Automatic Cleanup**: Removes temporary files after processing
- ✅ **Error Handling**: Robust error handling with helpful messages
- ✅ **Transcript Utilities**: Tools to clean and format existing transcripts

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
Input: ScreenRecordingAudio.mp3
Output: ScreenRecordingAudio_transcript.txt
--------------------------------------------------
Audio duration: 125.43 seconds
Audio is longer than 30 seconds, splitting into chunks...
Generated 5 audio chunks
Transcribing 5 chunks...
Processing chunk 1/5: ScreenRecordingAudio_000.mp3
✓ Chunk 1 transcribed successfully
Processing chunk 2/5: ScreenRecordingAudio_001.mp3
✓ Chunk 2 transcribed successfully
...
Cleaning up temporary chunks...
Transcription completed successfully!
Transcript saved to: ScreenRecordingAudio_transcript.txt

==================================================
TRANSCRIPTION RESULT:
==================================================
राइट।
तो वो डेली बेस पे नहीं है वो वीक में एक या दो ट्रांजैक्शन ऐसी होती है...
==================================================
```

### Clean Text File Output (`ScreenRecordingAudio_transcript.txt`):
```
राइट।
तो वो डेली बेस पे नहीं है वो वीक में एक या दो ट्रांजैक्षन ऐसी होती है जो रेगुलर बेस पे है तो वो मेरा 20 से 25 में कवर हम कर सकते हैं जो डेली में ट्रांजैक्षन है।
राइट।
और एक्सेप्शनली ऐसा कोई ऑप्शन होता है कि एक्सेप्शनली हम वीक में एक या दो ट्रक हमारे जो 40 प्लस चलते हैं उसको कवर कर सकें।
```

**Key Improvements:**
- ✅ No API metadata or response formatting
- ✅ Clean, readable Hindi text
- ✅ Proper line breaks and formatting
- ✅ Ready for further processing or reading
