# AutoU Case - Email Classification & Auto-Reply System

A comprehensive email management system that automatically classifies emails as productive or unproductive using machine learning, and provides AI-powered response suggestions using Retrieval Augmented Generation (RAG).

## 🚀 Features

### Core Functionality
- **Email Classification**: Automatically classifies emails as productive or unproductive using the fine-tuned model `MiguelJeronimoOliveira/email-classifier`
- **AI-Powered Response Suggestions**: Generates contextual email response suggestions using RAG (Retrieval Augmented Generation) with Gemini API
- **Email Integration**: Full IMAP/SMTP integration for receiving and sending emails
- **Auto-Reply System**: Configurable automatic email replies with customizable rules
- **Email History**: Track and manage all processed emails with their classifications
- **File Processing**: Support for analyzing emails from `.txt` and `.pdf` files
- **Real-time Processing**: Background task continuously monitors and processes incoming emails

### Technical Features
- **RESTful API**: FastAPI-based backend with comprehensive API documentation
- **Modern Frontend**: React + TypeScript frontend with Tailwind CSS
- **Vector Database**: ChromaDB for RAG knowledge base storage
- **ML Model**: Fine-tuned transformer model for email classification (Hugging Face compatible)
- **Multilingual Support**: RAG system supports multilingual embeddings

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Training](#training)
- [Testing](#testing)

## 🔧 Prerequisites

### Backend Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Frontend Requirements
- Node.js 16 or higher
- npm or yarn

### External Services
- Google Gemini API key (for RAG response generation)
- Email account with IMAP/SMTP access (Gmail recommended)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "AutoU Case"
```

### 2. Backend Setup

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# API Configuration
API_TITLE=Email Classification API
API_VERSION=1.0.0

# Server Configuration
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Gemini API (Required for RAG)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-2.5-flash

# ML Model Configuration
MODEL_PATH=MiguelJeronimoOliveira/email-classifier
DEFAULT_MODEL_NAME=MiguelJeronimoOliveira/email-classifier

# RAG Configuration
RAG_ENABLED=true
RAG_KNOWLEDGE_BASE_PATH=rag_knowledge_base
RAG_EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
RAG_TOP_K_RESULTS=3
RAG_MIN_SIMILARITY_SCORE=0.5

# Email Configuration (Required for email integration)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=465
EMAIL_USE_SSL=true
EMAIL_CHECK_INTERVAL=60

# Auto-Reply Configuration
EMAIL_AUTO_REPLY_ENABLED=false
EMAIL_AUTO_REPLY_ONLY_PRODUCTIVE=true
EMAIL_AUTO_REPLY_MIN_CONFIDENCE=0.7
```

> **Note on ML Model**: By default, the system uses the pre-trained model `MiguelJeronimoOliveira/email-classifier` from Hugging Face. You can train your own custom model using the training instructions provided in the [Training](#-training) section below.

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### Gmail App Password Setup

For Gmail integration, you'll need to create an app-specific password:

1. Go to your Google Account settings
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate a new app password for "Mail"
5. Use this password in `EMAIL_PASSWORD`

## 🚀 Usage

### Starting the Backend

```bash
# Activate virtual environment (if not already activated)
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Run the server
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Starting the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Using the Application

1. **Home Page**: Upload email files or paste email content for analysis
2. **Emails Page**: View all received emails with their classifications
3. **History Page**: Browse email history and response suggestions
4. **Settings Page**: Configure auto-reply settings and email storage preferences

## 📚 API Documentation

### Endpoints

#### Health Check
- `GET /api/v1/health` - Check API health status

#### Email Analysis
- `POST /api/v1/email/analyze` - Analyze email content or file
  - Request body: `{ "email_content": "..." }` or `{ "file_path": "..." }`
  - Returns: Classification result with confidence score and suggested response

#### Email Flow
- `GET /api/v1/emails` - List all received emails
- `GET /api/v1/emails/{email_id}` - Get specific email details
- `GET /api/v1/emails/{email_id}/suggestions` - Get response suggestions for an email
- `POST /api/v1/suggestions/{suggestion_id}/approve` - Approve and optionally send a suggestion
- `GET /api/v1/auto-reply/config` - Get auto-reply configuration
- `PUT /api/v1/auto-reply/config` - Update auto-reply configuration

#### RAG
- `POST /api/v1/rag/query` - Query the RAG knowledge base
- `POST /api/v1/rag/add-document` - Add document to knowledge base
- `GET /api/v1/rag/documents` - List all documents in knowledge base

### Example API Request

```bash
curl -X POST "http://localhost:8000/api/v1/email/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "email_content": "Hi, I would like to schedule a meeting to discuss the project timeline."
  }'
```

### Postman Collection

A Postman collection is available at `AutoU_Case_API.postman_collection.json` for testing the API endpoints.

## 📁 Project Structure

```
AutoU Case/
├── app/                          # Backend application
│   ├── api/                      # API routes and endpoints
│   │   ├── v1/
│   │   │   └── endpoints/        # API endpoint implementations
│   │   │       ├── email.py      # Email analysis endpoints
│   │   │       ├── email_flow.py # Email flow management
│   │   │       ├── health.py     # Health check endpoints
│   │   │       └── rag.py        # RAG endpoints
│   │   └── deps.py               # Dependency injection
│   ├── core/                     # Core configuration and utilities
│   │   ├── config.py             # Application settings
│   │   ├── constants.py          # Application constants
│   │   ├── exceptions.py         # Custom exceptions
│   │   └── logging.py            # Logging configuration
│   ├── services/                 # Business logic services
│   │   ├── email_service.py      # Email IMAP/SMTP service
│   │   ├── email_processor.py   # Email processing logic
│   │   ├── email_storage.py     # Email storage service
│   │   └── email_background_task.py # Background email monitoring
│   ├── classifier.py            # ML email classifier
│   ├── rag_retriever.py         # RAG retrieval system
│   ├── response_generator.py    # AI response generation
│   ├── file_processor.py        # File processing utilities
│   ├── models.py                # Pydantic models
│   └── main.py                  # FastAPI application entry point
├── frontend/                     # Frontend application
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── EmailCard.tsx
│   │   │   ├── EmailHistory.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   └── ...
│   │   ├── pages/               # Page components
│   │   │   ├── Home.tsx
│   │   │   ├── Emails.tsx
│   │   │   ├── History.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API service layer
│   │   └── types/               # TypeScript type definitions
│   └── package.json
├── tests/                        # Test suite
│   └── test_api/                # API endpoint tests
├── training/                     # ML model training scripts
├── scripts/                      # Utility scripts
├── rag_knowledge_base/          # RAG vector database
├── requirements.txt             # Python dependencies
└── README.md                     # This file
```

## 🛠️ Development

### Running in Development Mode

Backend with hot reload:
```bash
uvicorn app.main:app --reload
```

Frontend with hot reload:
```bash
cd frontend
npm run dev
```

### Code Style

- Backend: Follow PEP 8 Python style guide
- Frontend: ESLint and TypeScript strict mode enabled

### Adding New Features

1. Backend: Add endpoints in `app/api/v1/endpoints/`
2. Frontend: Add components in `frontend/src/components/` and pages in `frontend/src/pages/`
3. Update API models in `app/models.py` if needed
4. Add tests in `tests/test_api/`

## 🎓 Training

### Overview

The project includes training scripts to fine-tune transformer models for email classification. You can train models on your own data or use pre-trained models from Hugging Face.

### Prerequisites for Training

- GPU recommended (CUDA-compatible) for faster training, but CPU training is also supported
- Sufficient RAM (8GB+ recommended)
- Training data in JSON format (see format below)

### Training Data Format

Create a `training_data.json` file in the root directory with the following format:

```json
[
  {
    "text": "Hi, I would like to schedule a meeting to discuss the project timeline.",
    "label": 1
  },
  {
    "text": "Check out this amazing deal! Limited time offer!",
    "label": 0
  }
]
```

Where:
- `text`: The email content to classify
- `label`: `1` for productive emails, `0` for unproductive emails

### Generating Training Data

You can use the provided script to generate training data:

```bash
py .\training\generate_complex_training_data.py --productive AMOUNT --unproductive AMOUNT
```

This will create a `training_data.json` file with sample data that you can customize.

### Training a Model

#### Basic Training

Train a model with default settings:

```bash
python training/train_classifier.py
```

#### Custom Training

Train with custom parameters:

```bash
python training/train_classifier.py \
  --model-name bert-base-multilingual-cased \
  --epochs 5 \
  --batch-size 8 \
  --learning-rate 2e-5 \
  --output-dir models/email_classifier_custom
```

#### Training Parameters

- `--model-name`: Base model to fine-tune (default: `bert-base-multilingual-cased`)
- `--epochs`: Number of training epochs (default: `5`)
- `--batch-size`: Batch size for training (default: `8`)
- `--learning-rate`: Learning rate (default: `2e-5`)
- `--output-dir`: Directory to save the trained model (default: `models/email_classifier`)
- `--data-file`: Path to training data JSON file (default: `training_data.json`)
- `--no-gpu`: Disable GPU usage even if available

### Using a Trained Model

After training, update your `.env` file to use the new model:

```env
# For locally trained model
MODEL_PATH=models/email_classifier
DEFAULT_MODEL_NAME=models/email_classifier

# Or if uploaded to Hugging Face
MODEL_PATH=MiguelJeronimoOliveira/email-classifier
DEFAULT_MODEL_NAME=MiguelJeronimoOliveira/email-classifier
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_email.py
```

### Test Structure

- `tests/conftest.py` - Pytest configuration and fixtures
- `tests/test_api/` - API endpoint tests

## developed by 

Miguel Jeronimo Oliveira
