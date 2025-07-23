# Git Repository: Sarvam.ai Speech-to-Text

## 📦 Repository Contents

### 🚀 Core Scripts
- **`sarvam_stt.py`** - Main transcription script with clean output
- **`setup_api_key.py`** - API key configuration helper
- **`clean_transcript.py`** - Utility to clean existing transcript files
- **`example_usage.py`** - Usage examples and demonstrations

### 📚 Documentation
- **`README_Sarvam.md`** - Comprehensive documentation
- **`UPDATES.md`** - Latest improvements and features
- **`requirements.txt`** - Python dependencies
- **`.gitignore`** - Git ignore rules (excludes large files and sensitive data)

### 🎵 Test Audio Files
- **`trimmed_audio_15s.mp3`** (235KB) - Short audio for testing
- **`trimmed_audio_30s.mp3`** (469KB) - 30-second test file
- **`trimmed_audio.mp3`** (2.7MB) - Longer test file

### 🚫 Excluded Files
- `ScreenRecordingAudio.mp3` (49MB) - Too large for git
- `*.txt` transcript files - May contain sensitive content
- `.env` - Contains API keys
- `chunks/` - Temporary processing files

## ✨ Key Features Committed

### 1. Clean Text Output
- Extracts only transcript text from API responses
- No metadata or formatting artifacts
- Ready for immediate use

### 2. Smart Audio Processing
- Automatic chunking for long audio files
- Progress tracking for large transcriptions
- Automatic cleanup of temporary files

### 3. Multiple Language Support
- Hindi (hi-IN) - Primary target
- English (en-IN)
- Auto-detect (unknown)
- Code-mixed speech

### 4. User-Friendly Features
- Automatic API key loading from .env
- Clear progress indicators
- Comprehensive error handling
- Multiple usage methods (CLI, programmatic)

## 🎯 Usage After Clone

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
python setup_api_key.py

# 3. Test with included audio
python sarvam_stt.py trimmed_audio_15s.mp3

# 4. See examples
python example_usage.py

# 5. Clean old transcripts (if any)
python clean_transcript.py old_transcript.txt
```

## 📊 Commit Statistics
- **12 files** committed
- **970 lines** of code added
- **Test files included** for immediate testing
- **Complete documentation** provided

---
**Repository ready for Hindi conference call transcriptions! 🎉**
