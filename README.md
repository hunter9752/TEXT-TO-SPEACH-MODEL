# 🎤 TEXT-TO-SPEECH AI Analysis System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GROQ](https://img.shields.io/badge/AI-GROQ%20%7C%20OpenAI-green.svg)](https://groq.com/)

A comprehensive, production-ready system that converts speech to text and provides intelligent AI analysis using GROQ or OpenAI APIs.

## ✨ Features

- 🎤 **Real-time Speech Processing**: Live microphone input with instant transcription
- 🧠 **Multi-Provider AI Analysis**: GROQ (primary) and OpenAI support
- 📁 **Multi-format Audio Support**: WAV, MP3, M4A, FLAC (with FFmpeg)
- 🌐 **Modern Web Interface**: Bootstrap-powered responsive UI
- 💻 **CLI Tools**: Command-line interface for batch processing
- 📊 **Multiple Analysis Types**: General, Sentiment, Intent, Summary
- 📈 **Session Management**: Conversation history and analytics
- 🔧 **Production Ready**: Comprehensive error handling and testing

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/hunter9752/TEXT-TO-SPEACH-MODEL.git
cd TEXT-TO-SPEACH-MODEL
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# For GROQ (recommended - faster and often free):
GROQ_API_KEY=gsk_your_groq_api_key_here
AI_PROVIDER=groq

# Or for OpenAI:
OPENAI_API_KEY=sk_your_openai_api_key_here
AI_PROVIDER=openai
```

### 4. Run the System
```bash
# Web Interface (recommended)
python main.py --mode web

# CLI Mode
python main.py --mode cli

# Process Audio File
python main.py --mode file --file audio.wav
```

## 🏗️ Architecture

```
Audio Input → Speech Recognition → AI Analysis → Intelligent Response
     ↓              ↓                  ↓              ↓
File Upload    Google/Whisper      GROQ/OpenAI    Web/CLI/JSON
Microphone     Speech APIs         Analysis       Export Options
```

## 📁 Project Structure

```
speech-to-text-model/
├── src/
│   ├── speech_to_text/     # Speech recognition engines
│   ├── ai_analysis/        # AI analysis with GROQ/OpenAI
│   ├── audio_handler/      # Audio input processing
│   ├── output_processor/   # Response formatting
│   └── web_interface/      # Flask web application
├── tests/                  # Comprehensive test suite
├── templates/              # HTML templates
├── static/                 # Web assets
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── .env.example           # Configuration template
```

## 🎯 Usage Examples

### Web Interface
1. Open http://localhost:5000
2. Upload audio files or use microphone
3. Choose analysis type (General, Sentiment, Intent, Summary)
4. Get instant AI-powered responses

### Command Line
```bash
# Live speech processing
python main.py --mode cli

# Batch file processing
python main.py --mode file --file recording.wav

# Web server
python main.py --mode web --port 5000
```

## 🔧 Configuration

### API Providers

**GROQ (Recommended)**
- Faster inference
- Better free tier
- Open source models (Llama, Mixtral)
```env
GROQ_API_KEY=gsk_your_key_here
AI_PROVIDER=groq
AI_MODEL=llama3-8b-8192
```

**OpenAI**
- GPT models
- Advanced capabilities
```env
OPENAI_API_KEY=sk_your_key_here
AI_PROVIDER=openai
AI_MODEL=gpt-3.5-turbo
```

### Audio Processing
- **WAV files**: Work out of the box
- **MP3/M4A/FLAC**: Require FFmpeg installation

## 📋 Requirements

- **Python**: 3.8 or higher
- **API Key**: GROQ (free) or OpenAI account
- **Optional**: FFmpeg for audio format conversion
- **Optional**: Microphone for real-time input

## 🧪 Testing

```bash
# Run system tests
python test_system.py

# Test specific components
python test_groq.py
python test_openai.py

# Complete system test
python test_complete_system.py
```

## 🚀 Deployment

The system is production-ready with:
- Comprehensive error handling
- Logging and monitoring
- Health check endpoints
- Session management
- Export capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **GROQ** for fast AI inference
- **OpenAI** for advanced language models
- **Google** for speech recognition services
- **Flask** for the web framework

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/hunter9752/TEXT-TO-SPEACH-MODEL/issues)
- 📖 **Documentation**: See project files and comments
- 💬 **Discussions**: [GitHub Discussions](https://github.com/hunter9752/TEXT-TO-SPEACH-MODEL/discussions)

---

**Built with ❤️ for the AI community**
