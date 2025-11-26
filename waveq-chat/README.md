# WaveQ Chat - AI Audio Processing Platform

Conversational AI interface for WaveQ audio processing powered by Vercel AI SDK and GPT-4.

## ✨ Features

- 🎤 **Natural Language Processing** - Chat with AI to process audio
- 📤 **Drag & Drop Upload** - Easy file upload with progress
- 🎵 **Audio Player** - Built-in player with seek and volume
- 📝 **Real-time Results** - See processing status live
- ⬇️ **Download Results** - Download all processed files
- 🇮🇱 **Hebrew Support** - Full RTL interface
- 🎨 **Beautiful UI** - Modern gradient design

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Create .env.local
OPENAI_API_KEY=your-openai-key
WAVEQ_API_URL=http://localhost:8000
WAVEQ_API_KEY=waveq_demo_key_123

# Run dev server
npm run dev
```

Visit: http://localhost:3000

## 🎯 Usage

1. **Upload** audio file (drag & drop or click)
2. **Chat** with AI: "תנקה רעש ותמלל"
3. **Watch** real-time processing
4. **Download** results

## 📦 Components

- **FileUploadZone** - Drag & drop with validation
- **AudioPlayer** - Full-featured player
- **TaskProgress** - Real-time status
- **ResultCard** - Unified results display
- **TranscriptViewer** - Copy & download transcripts
- **SentimentCard** - Emotion analysis

## 🛠️ Tech Stack

- Next.js 15 + TypeScript
- Vercel AI SDK + GPT-4
- Tailwind CSS
- WaveQ API Backend

## 🎬 Demo Flow

```
User: [uploads meeting.mp3]
AI: "קיבלתי! מה לעשות?"

User: "תנקה רעש ותמלל"
AI: [Shows progress]
   🔇 ניקוי רעש - 100% ✓
   📝 תמלול - 100% ✓

AI: "סיימתי! הנה:"
   [Audio player] + [Download]
   [Transcript] + [Copy/Download]
```

## 📄 License

MIT
