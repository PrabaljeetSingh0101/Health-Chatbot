# Medical Intake Partner - System Overview

## Description
An AI-powered medical intake assistant that conducts multilingual voice-based patient interviews, performs symptom triage, and generates clinical reports. The system uses Google's Gemini AI for intelligent questioning and data extraction, with support for voice interaction in multiple languages.

## Key Features

### Multilingual Support
- **Languages**: English, Hindi, French, Spanish
- **Voice I/O**: Speech recognition for input, text-to-speech for output
- **Auto-translation**: Seamless conversation in user's preferred language

### Clinical Workflow
1. **Patient Registration**: Collects name, age, and gender with validation
2. **Symptom Detection**: AI identifies symptoms from natural language descriptions
3. **Dynamic Triage**: Adaptive questioning based on clinical relevance (red flags, severity)
4. **Data Extraction**: Synthesizes severity (1-10 scale), duration, urgency level, and clinical summary
5. **Verification Loop**: Allows corrections before finalizing report

### Output & Storage
- **PDF Report**: Professional clinical intake document with patient profile and medical evaluation
- **MongoDB Integration**: Optional encrypted storage with patient data hashing
- **Structured Data**: JSON-formatted medical records for downstream systems

## Technical Stack

**AI & NLP**
- Google Gemini API (`gemini-3-pro-preview`)
- Speech recognition (Google Speech API)
- Edge TTS for voice synthesis
- Deep Translator for multilingual support

**Data Processing**
- Async/await architecture for concurrent operations
- Robust JSON extraction with regex fallbacks
- Fuzzy matching for language selection

**Storage & Export**
- FPDF for clinical report generation
- MongoDB for persistent storage
- SHA-256 hashing for patient anonymization

## Configuration

### Required Environment Variables
```env
GEMINI_API_KEY=<your_api_key>
MONGO_URI=<mongodb_connection_string>  # Optional
TEXT_MODE=0  # Set to 1 to disable voice
```

### Dependencies
```
google-generativeai, edge-tts, speech_recognition
pygame, fpdf, deep-translator, pymongo, thefuzz
```

## Usage Flow
```
Language Selection → Disclaimer/Consent → Bio Collection → 
Symptom Interview → AI Triage (per symptom) → 
Summary Verification → PDF Generation → Database Storage
```

## Safety Features
- Medical disclaimer requirement before proceeding
- Confirmation loops for voice recognition accuracy
- Fallback to text input on recognition failure
- Urgency flagging (low/med/high) for clinical prioritization
- 30-second audio timeout protection

## Output Location
- **PDF Reports**: `./Output/Summary/report.pdf`
- **Temp Audio**: `./Output/Audio/` (auto-cleaned)

## Notes
- Not a substitute for professional medical advice
- Designed for intake automation, not diagnosis
- Rate-limited API calls to prevent throttling
- Color-coded urgency in PDF (red for high-priority symptoms)
