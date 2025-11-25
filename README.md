# WaveQ - AI Audio Agent SDK/API

![Architecture](docs/architecture.png)

**WaveQ** is a comprehensive Python SDK and API for AI-powered audio processing. It provides an intelligent orchestrator that analyzes your audio needs and automatically applies the right combination of AI tools.

## ✨ Features

- 🎙️ **AI Denoising & Enhancement** - Remove background noise and enhance audio quality
- 📝 **Speech-to-Text with Diarization** - Transcribe audio with speaker identification
- ✂️ **Smart Trimming** - Automatically remove silence and trim audio
- 🎵 **Source Separation** - Separate vocals, drums, bass, and other instruments
- 😊 **Sentiment Analysis** - Analyze emotions and sentiment in audio
- 🗣️ **Text-to-Speech** - Convert text to natural-sounding speech
- 🤖 **AI Orchestrator** - Intelligent workflow management and intent classification

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/waveq.git
cd waveq

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
```

### Start the API Server

```bash
# Run with uvicorn
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Using the SDK

```python
from waveq import WaveQClient

# Initialize client
client = WaveQClient(api_key="your-api-key")

# Denoise audio
result = client.denoise_audio("noisy_audio.wav")
print(f"Task ID: {result.task_id}")

# Transcribe with speaker diarization
result = client.transcribe_audio(
    "meeting.mp3",
    enable_diarization=True
)
print(f"Transcript: {result.transcript}")

# Text to speech
result = client.text_to_speech(
    text="Hello, this is WaveQ!",
    language="en"
)
```

## 📦 Project Structure

```
waveq-python-api/
├── waveq/                      # SDK package
│   ├── __init__.py            # Package initialization
│   ├── client.py              # Main SDK client
│   ├── models.py              # Pydantic models
│   └── exceptions.py          # Custom exceptions
├── api/                        # API server
│   ├── __init__.py
│   ├── routes.py              # API endpoints
│   └── auth.py                # Authentication
├── orchestrator/               # AI orchestrator
│   ├── __init__.py
│   └── orchestrator.py        # Workflow management
├── audio_tools/                # Audio processing tools
│   ├── denoiser.py
│   ├── transcription.py
│   ├── trimming.py
│   ├── separator.py
│   ├── sentiment.py
│   └── tts.py
├── examples/                   # Example code
│   └── example_client.py
├── main.py                     # FastAPI app entry
├── config.py                   # Configuration
├── utils.py                    # Utilities
└── requirements.txt            # Dependencies
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/denoise` | POST | Remove noise from audio |
| `/api/v1/transcribe` | POST | Transcribe audio to text |
| `/api/v1/trim` | POST | Smart trimming and silence removal |
| `/api/v1/separate` | POST | Separate audio sources |
| `/api/v1/sentiment` | POST | Analyze audio sentiment |
| `/api/v1/tts` | POST | Text-to-speech conversion |
| `/api/v1/tasks/{task_id}` | GET | Get task status |

## 🎯 Use Cases

### Podcast Production
```python
# Automatically denoise, trim, and transcribe
client.denoise_audio("podcast_raw.wav")
client.trim_audio("podcast_raw.wav")
client.transcribe_audio("podcast_raw.wav", enable_diarization=True)
```

### Music Production
```python
# Separate vocals from instrumentals
result = client.separate_audio(
    "song.mp3",
    separation_type="vocals"
)
```

### Call Center Analytics
```python
# Transcribe and analyze sentiment
transcription = client.transcribe_audio("call.wav")
sentiment = client.analyze_sentiment("call.wav", include_emotions=True)
```

## 🔐 Authentication

The API uses Bearer token authentication. Include your API key in requests:

```bash
curl -X POST "http://localhost:8000/api/v1/denoise" \
  -H "Authorization: Bearer your-api-key" \
  -F "audio_file=@audio.wav"
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t waveq-api .

# Run container
docker run -p 8000:8000 waveq-api
```

## ⚙️ Configuration

Edit `.env` file to configure:

- **API Settings**: Port, debug mode, CORS origins
- **AI Models**: Whisper model size, device (CPU/GPU), Demucs model
- **Database**: Database URL for task storage
- **Third-party APIs**: OpenAI, ElevenLabs API keys

## 📊 Monitoring

Check server logs and task statuses:

```python
# Get task status
status = client.get_task_status(task_id)
print(f"Status: {status.status}")
print(f"Progress: {status.metadata}")
```

## 🛠️ Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub or contact support@waveq.ai

---

**Built with ❤️ using FastAPI, OpenAI Whisper, and Demucs**
