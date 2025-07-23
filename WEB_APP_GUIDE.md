# 🌐 Sarvam.ai Speech-to-Text Web Application

A simple, minimal web interface for Hindi speech-to-text conversion using Sarvam.ai API.

## ✨ Features

- **🎙️ Audio Upload**: Support for MP3, WAV, M4A, FLAC files (up to 100MB)
- **🌐 Language Selection**: Hindi, English, Auto-detect, Code-mixed
- **📊 Real-time Progress**: Live progress tracking for large files
- **📄 Multiple Downloads**: TXT and PDF format downloads
- **🔒 Secure**: Users bring their own API keys (no server-side storage)
- **📱 Responsive**: Works on desktop and mobile devices

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Open Browser**:
   Navigate to `http://localhost:5000`

### Usage

1. **Get API Key**: Visit [dashboard.sarvam.ai](https://dashboard.sarvam.ai/) to get your free API key
2. **Upload Audio**: Select your audio file (MP3, WAV, M4A, FLAC)
3. **Choose Language**: Select Hindi, English, auto-detect, or code-mixed
4. **Transcribe**: Click "Start Transcription" and wait for results
5. **Download**: Get your transcript as TXT or PDF

## 🌍 Deployment Options

### 1. Heroku (Free Tier Available)

Create `Procfile`:
```
web: python app.py
```

Create `runtime.txt`:
```
python-3.11.0
```

Deploy:
```bash
git add .
git commit -m "Add web app"
git push heroku main
```

### 2. Railway

1. Connect your GitHub repository
2. Railway will auto-detect Flask app
3. Set environment variables if needed
4. Deploy automatically

### 3. Render

1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python app.py`
4. Deploy

### 4. DigitalOcean App Platform

1. Create new app from GitHub
2. Select repository
3. Configure build settings
4. Deploy

## 🔧 Configuration

### Environment Variables

- `PORT`: Port to run the application (default: 5000)
- `FLASK_ENV`: Set to `production` for production deployment

### File Size Limits

- Default: 100MB maximum file size
- Modify `MAX_CONTENT_LENGTH` in `app.py` to change

### Security Considerations

- API keys are never stored on the server
- Uploaded files are automatically deleted after processing
- Old jobs are cleaned up automatically (1 hour retention)

## 📁 File Structure

```
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── sarvam_stt.py         # Core transcription logic
├── requirements.txt      # Dependencies
└── temp_uploads/         # Temporary file storage (auto-created)
```

## 🛠️ Technical Details

### Architecture

- **Backend**: Flask (Python)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **File Processing**: Background threads for transcription
- **Progress Tracking**: Real-time polling
- **PDF Generation**: ReportLab library

### API Endpoints

- `GET /` - Main interface
- `POST /upload` - File upload and transcription start
- `GET /status/<job_id>` - Progress tracking
- `GET /download/<job_id>/<format>` - File download
- `GET /cleanup` - Manual cleanup (optional)

### Performance

- **Large Files**: Automatic chunking for files > 30 seconds
- **Concurrent Users**: Supports multiple simultaneous transcriptions
- **Memory Management**: Automatic cleanup of temporary files
- **Error Handling**: Robust error handling with user feedback

## 🎯 Production Deployment Tips

### 1. Use Production WSGI Server

Replace the development server with Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. Add Health Check Endpoint

Add to `app.py`:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}
```

### 3. Configure Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 4. Add Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)
```

## 🔒 Security Best Practices

1. **API Key Handling**: Never log or store API keys
2. **File Validation**: Strict file type and size validation
3. **Temporary Files**: Automatic cleanup after processing
4. **Input Sanitization**: All user inputs are sanitized
5. **HTTPS**: Use HTTPS in production (handled by deployment platform)

## 📊 Monitoring

### Basic Metrics to Track

- Number of transcriptions per day
- Average processing time
- File sizes processed
- Error rates
- API key validation failures

### Log Analysis

The app logs important events:
- File uploads
- Transcription starts/completions
- Errors and failures
- Cleanup operations

## 🆘 Troubleshooting

### Common Issues

1. **Large File Timeouts**:
   - Increase server timeout limits
   - Consider chunking very large files client-side

2. **Memory Issues**:
   - Monitor memory usage with large files
   - Implement file size limits based on server capacity

3. **API Rate Limits**:
   - Implement client-side rate limiting
   - Add queue system for high traffic

4. **FFmpeg Not Found**:
   - Ensure FFmpeg is installed on deployment server
   - For Heroku, add FFmpeg buildpack

## 🎉 Community Deployment

This web app is designed for community use where:
- Users bring their own Sarvam.ai API keys
- No server-side API key storage required
- Scalable for multiple concurrent users
- Easy to deploy on free hosting platforms

Perfect for:
- Educational institutions
- Community centers
- Open source projects
- Personal use

---

**Ready to deploy your Hindi Speech-to-Text web application! 🚀**
