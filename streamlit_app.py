#!/usr/bin/env python3
"""
Sarvam.ai Speech-to-Text Streamlit Web Application
Modern web interface for Hindi speech-to-text conversion with speaker diarization
"""

import streamlit as st
import os
import tempfile
import time
from pathlib import Path
import io
from datetime import datetime
import json

# Import our existing classes
from sarvam_stt import SarvamSTT
from sarvam_batch_stt import SarvamBatchSTT

# Page configuration
st.set_page_config(
    page_title="Sarvam.ai Speech-to-Text | Krishyam Techlabs",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

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

def get_audio_duration_display(file_path):
    """Get audio duration for display purposes"""
    try:
        import subprocess
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration_seconds = float(result.stdout.strip())
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        return f"{minutes}:{seconds:02d}"
    except:
        return "Unknown"

def create_download_content(transcript, filename, format_type):
    """Create downloadable content in specified format"""
    if format_type == "txt":
        content = f"""Speech-to-Text Transcript
Original File: {filename}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Language: Hindi (हिन्दी)
{'-' * 50}

{transcript}
"""
        return content.encode('utf-8'), f"{Path(filename).stem}_transcript.txt", "text/plain"
    
    elif format_type == "json":
        data = {
            "original_file": filename,
            "generated_at": datetime.now().isoformat(),
            "language": "Hindi",
            "transcript": transcript
        }
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return content.encode('utf-8'), f"{Path(filename).stem}_transcript.json", "application/json"

def main():
    # Load environment variables
    load_env_file()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎤 Sarvam.ai Speech-to-Text</h1>
        <p>Convert Hindi audio to text with advanced speaker diarization</p>
        <p style="font-size: 14px; margin-top: 10px; opacity: 0.9;">Powered by <strong>Krishyam Techlabs</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Sarvam.ai API Key",
            type="password",
            value=os.getenv('SARVAM_API_KEY', ''),
            help="Enter your Sarvam.ai API key. You can also set it in a .env file."
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your Sarvam.ai API key to continue.")
            st.info("Get your API key from [Sarvam.ai](https://www.sarvam.ai/)")
            return
        
        st.success("✅ API key configured")
        
        # Company info
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 10px; margin: 1rem 0;">
            <h4 style="color: #4CAF50; margin-bottom: 0.5rem;">🏢 Krishyam Techlabs</h4>
            <p style="font-size: 12px; color: #666; margin: 0;">Advanced AI Solutions</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Processing mode selection
        st.subheader("🔧 Processing Mode")
        processing_mode = st.radio(
            "Choose processing type:",
            ["Regular STT", "Batch STT (with Speaker Diarization)"],
            help="Regular STT: For files ≤30 seconds\nBatch STT: For longer files with speaker identification"
        )
        
        # Language selection
        st.subheader("🌐 Language")
        language_options = {
            "Hindi (hi-IN)": "hi-IN",
            "English (en-IN)": "en-IN",
            "Auto-detect": "auto"
        }
        selected_language = st.selectbox(
            "Select language:",
            options=list(language_options.keys()),
            index=0
        )
        language_code = language_options[selected_language]
        
        # Additional options for Batch STT
        if processing_mode == "Batch STT (with Speaker Diarization)":
            st.subheader("👥 Speaker Settings")
            num_speakers = st.number_input(
                "Expected number of speakers:",
                min_value=1,
                max_value=10,
                value=2,
                help="Leave as 2 if unsure. The system will auto-detect."
            )
            
            improve_diarization = st.checkbox(
                "Apply speaker consistency improvements",
                value=True,
                help="Reduces speaker mixing and merges consecutive segments"
            )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Upload Audio File")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'm4a', 'flac'],
            help="Supported formats: MP3, WAV, M4A, FLAC"
        )
        
        if uploaded_file is not None:
            # Display file info
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            
            st.markdown(f"""
            <div class="feature-box">
                <h4>📄 File Information</h4>
                <p><strong>Name:</strong> {uploaded_file.name}</p>
                <p><strong>Size:</strong> {file_size_mb:.2f} MB</p>
                <p><strong>Type:</strong> {uploaded_file.type}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Process button
            if st.button("🚀 Start Transcription", type="primary", use_container_width=True):
                process_audio(uploaded_file, api_key, language_code, processing_mode, 
                            num_speakers if processing_mode == "Batch STT (with Speaker Diarization)" else None,
                            improve_diarization if processing_mode == "Batch STT (with Speaker Diarization)" else True)
    
    with col2:
        st.header("ℹ️ Information")
        
        if processing_mode == "Regular STT":
            st.markdown("""
            <div class="feature-box">
                <h4>🎯 Regular STT Features</h4>
                <ul>
                    <li>Best for files ≤30 seconds</li>
                    <li>Fast processing</li>
                    <li>Simple transcription</li>
                    <li>Multiple language support</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="feature-box">
                <h4>🎯 Batch STT Features</h4>
                <ul>
                    <li>Files up to 1 hour</li>
                    <li>Speaker diarization</li>
                    <li>Timestamped output</li>
                    <li>Speaker timing analysis</li>
                    <li>Consistency improvements</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-box">
            <h4>💡 Tips</h4>
            <ul>
                <li>Clear audio gives better results</li>
                <li>Minimize background noise</li>
                <li>For multiple speakers, use Batch STT</li>
                <li>Hindi and English both supported</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def process_audio(uploaded_file, api_key, language_code, processing_mode, num_speakers, improve_diarization):
    """Process the uploaded audio file"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Show processing status
        st.header("🔄 Processing")
        
        # Progress bar and status
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        if processing_mode == "Regular STT":
            # Regular STT processing
            status_text.text("Initializing Sarvam STT...")
            progress_bar.progress(10)
            
            stt = SarvamSTT(api_key)
            
            status_text.text("Processing audio file...")
            progress_bar.progress(50)
            
            start_time = time.time()
            transcript = stt.transcribe_audio(tmp_file_path, language_code)
            processing_time = time.time() - start_time
            
            progress_bar.progress(100)
            status_text.text("✅ Transcription completed!")
            
            if transcript:
                display_regular_results(transcript, uploaded_file.name, processing_time)
            else:
                st.error("❌ Transcription failed. Please check your API key and try again.")
        
        else:
            # Batch STT processing
            status_text.text("Initializing Batch STT...")
            progress_bar.progress(10)
            
            batch_stt = SarvamBatchSTT(api_key)
            
            status_text.text("Checking audio duration...")
            progress_bar.progress(20)
            
            # Split audio if needed
            audio_paths = batch_stt.split_audio_if_needed(tmp_file_path)
            
            status_text.text("Starting batch transcription...")
            progress_bar.progress(30)
            
            start_time = time.time()
            results = batch_stt.process_batch_transcription(
                audio_paths,
                language_code=language_code,
                num_speakers=num_speakers,
                improve_diarization=improve_diarization
            )
            processing_time = time.time() - start_time
            
            progress_bar.progress(100)
            status_text.text("✅ Batch transcription completed!")
            
            # Clean up chunks if created
            if len(audio_paths) > 1:
                for chunk_path in audio_paths:
                    try:
                        os.remove(chunk_path)
                    except:
                        pass
                try:
                    chunk_dir = Path(audio_paths[0]).parent
                    chunk_dir.rmdir()
                except:
                    pass
            
            if results.get("success"):
                display_batch_results(results, uploaded_file.name, processing_time)
            else:
                st.error(f"❌ Batch transcription failed: {results.get('error', 'Unknown error')}")
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
        except:
            pass

def display_regular_results(transcript, filename, processing_time):
    """Display results for regular STT"""
    st.header("📝 Transcription Results")
    
    # Processing info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Processing Time", f"{processing_time:.2f}s")
    with col2:
        st.metric("Characters", len(transcript))
    with col3:
        st.metric("Words", len(transcript.split()))
    
    # Transcript display
    st.subheader("📄 Transcript")
    st.text_area("", transcript, height=200, disabled=True)
    
    # Download options
    st.subheader("💾 Download Options")
    col1, col2 = st.columns(2)
    
    with col1:
        # TXT download
        txt_content, txt_filename, txt_mimetype = create_download_content(transcript, filename, "txt")
        st.download_button(
            label="📄 Download as TXT",
            data=txt_content,
            file_name=txt_filename,
            mime=txt_mimetype,
            use_container_width=True
        )
    
    with col2:
        # JSON download
        json_content, json_filename, json_mimetype = create_download_content(transcript, filename, "json")
        st.download_button(
            label="📋 Download as JSON",
            data=json_content,
            file_name=json_filename,
            mime=json_mimetype,
            use_container_width=True
        )

def display_batch_results(results, filename, processing_time):
    """Display results for batch STT with diarization"""
    st.header("📝 Batch Transcription Results")
    
    # Processing info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Processing Time", f"{processing_time:.2f}s")
    with col2:
        st.metric("Files Processed", len(results.get('transcriptions', {})))
    with col3:
        st.metric("Job ID", results.get('job_id', 'N/A')[:8] + "...")
    with col4:
        st.metric("Status", "✅ Success" if results.get('success') else "❌ Failed")
    
    # Speaker analysis
    if results.get('speaker_timings'):
        st.subheader("👥 Speaker Analysis")
        
        for file_stem, timing_data in results['speaker_timings'].items():
            st.write(f"**File: {file_stem}**")
            
            # Speaker metrics
            cols = st.columns(len(timing_data['speaker_times_seconds']))
            for i, (speaker, time_sec) in enumerate(timing_data['speaker_times_seconds'].items()):
                percentage = timing_data['speaker_percentages'].get(speaker, 0)
                with cols[i]:
                    st.metric(
                        speaker,
                        f"{time_sec:.1f}s",
                        f"{percentage:.1f}%"
                    )
    
    # Conversation display
    if results.get('conversations'):
        st.subheader("💬 Conversation")
        
        for file_stem, conv_data in results['conversations'].items():
            conversation_text = conv_data['text']
            
            # Show first 1000 characters with expand option
            if len(conversation_text) > 1000:
                with st.expander("📄 View Full Conversation", expanded=False):
                    st.text_area("", conversation_text, height=400, disabled=True)
                st.text_area("Preview (first 1000 characters):", conversation_text[:1000] + "...", height=200, disabled=True)
            else:
                st.text_area("", conversation_text, height=300, disabled=True)
    
    # Download options
    st.subheader("💾 Download Options")
    
    if results.get('conversations'):
        for file_stem, conv_data in results['conversations'].items():
            st.write(f"**Downloads for: {file_stem}**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Conversation TXT
                st.download_button(
                    label="💬 Download Conversation",
                    data=conv_data['text'].encode('utf-8'),
                    file_name=f"{file_stem}_conversation.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                # Speaker timing JSON
                if file_stem in results.get('speaker_timings', {}):
                    timing_json = json.dumps(results['speaker_timings'][file_stem], ensure_ascii=False, indent=2)
                    st.download_button(
                        label="⏱️ Download Timing Analysis",
                        data=timing_json.encode('utf-8'),
                        file_name=f"{file_stem}_timing.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            with col3:
                # Raw transcription JSON
                if file_stem in results.get('transcriptions', {}):
                    raw_json = json.dumps(results['transcriptions'][file_stem], ensure_ascii=False, indent=2)
                    st.download_button(
                        label="📋 Download Raw JSON",
                        data=raw_json.encode('utf-8'),
                        file_name=f"{file_stem}_raw.json",
                        mime="application/json",
                        use_container_width=True
                    )

# Footer
def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🚀 Developed by <strong>Krishyam Techlabs</strong> | Powered by <strong>Sarvam.ai</strong> | Built with ❤️ using Streamlit</p>
        <p>For support or feedback, visit our <a href="https://github.com/anujaggarwal/sarvam-hindi-speech-to-text" target="_blank">GitHub repository</a></p>
        <p style="font-size: 12px; margin-top: 10px; opacity: 0.8;">© 2025 Krishyam Techlabs. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_footer()
