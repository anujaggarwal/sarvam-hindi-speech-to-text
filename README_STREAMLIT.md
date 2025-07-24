# 🎤 Sarvam.ai Speech-to-Text Streamlit App

A modern web application for Hindi speech-to-text conversion with advanced speaker diarization, built with Streamlit.

## ✨ Features

### 🎯 Regular STT
- Fast transcription for audio files ≤30 seconds
- Multiple language support (Hindi, English, Auto-detect)
- Simple and efficient processing

### 🎯 Batch STT with Speaker Diarization
- Process files up to 1 hour long
- Advanced speaker identification (SPEAKER_00, SPEAKER_01, etc.)
- Timestamped conversation output
- Speaker timing analysis with percentages
- Custom post-processing to reduce speaker mixing
- Automatic audio splitting for longer files

## 🚀 Live Demo

**Deploy on Streamlit Cloud:** [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- FFmpeg installed on your system
- Sarvam.ai API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anujaggarwal/sarvam-hindi-speech-to-text.git
   cd sarvam-hindi-speech-to-text
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key:**
   Create a `.env` file:
   ```
   SARVAM_API_KEY=your_api_key_here
   ```

5. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

6. **Open your browser:**
   Navigate to `http://localhost:8501`

## 🌐 Deployment on Streamlit Cloud

### Step 1: Prepare Repository
1. Make sure your repository is public on GitHub
2. Ensure all files are committed:
   - `streamlit_app.py` (main app)
   - `requirements.txt` (dependencies)
   - `packages.txt` (system packages)
   - `.streamlit/config.toml` (Streamlit config)

### Step 2: Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `anujaggarwal/sarvam-hindi-speech-to-text`
5. Set main file path: `streamlit_app.py`
6. Click "Deploy!"

### Step 3: Configure Secrets
1. In your Streamlit Cloud dashboard, go to app settings
2. Add secrets in the "Secrets" tab:
   ```toml
   SARVAM_API_KEY = "your_api_key_here"
   ```

## 📁 File Structure

```
├── streamlit_app.py          # Main Streamlit application
├── sarvam_stt.py            # Regular STT class
├── sarvam_batch_stt.py      # Batch STT with diarization
├── requirements.txt         # Python dependencies
├── packages.txt            # System packages (ffmpeg)
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── .env                    # Environment variables (local)
└── README_STREAMLIT.md     # This file
```

## 🎨 Features Overview

### User Interface
- **Modern Design**: Clean, responsive interface with custom CSS
- **File Upload**: Drag-and-drop audio file upload
- **Real-time Progress**: Progress bars and status updates
- **Download Options**: Multiple format downloads (TXT, JSON)

### Processing Modes
- **Regular STT**: Quick transcription for short files
- **Batch STT**: Advanced processing with speaker diarization

### Speaker Diarization
- **Speaker Identification**: Automatic speaker labeling
- **Timing Analysis**: Speaking time per speaker with percentages
- **Consistency Improvements**: Custom algorithm to reduce speaker mixing
- **Timestamped Output**: Conversation format with timestamps

## 🔧 Configuration Options

### Sidebar Settings
- **API Key Input**: Secure API key configuration
- **Processing Mode**: Choose between Regular and Batch STT
- **Language Selection**: Hindi, English, or Auto-detect
- **Speaker Settings**: Number of speakers and consistency improvements

## 📊 Performance

### Regular STT
- **Speed**: ~2-3 seconds for 30-second audio
- **Accuracy**: Optimized for Hindi and English
- **File Size**: Up to 200MB supported

### Batch STT
- **Speed**: ~20-25 seconds for 3-minute audio
- **Speaker Accuracy**: 62% reduction in speaker mixing
- **File Length**: Up to 1 hour (auto-splits longer files)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `streamlit run streamlit_app.py`
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/anujaggarwal/sarvam-hindi-speech-to-text/issues)
- **API Documentation**: [Sarvam.ai Docs](https://docs.sarvam.ai)
- **Streamlit Docs**: [Streamlit Documentation](https://docs.streamlit.io)

## 🙏 Acknowledgments

- **Sarvam.ai** for the excellent Hindi STT API
- **Streamlit** for the amazing web app framework
- **Contributors** who helped improve this project

---

**🚀 Ready to deploy? Make your repository public and deploy on Streamlit Cloud for free!**
