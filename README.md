# Bericht Generator (Backend)

Bericht Generator Backend is a high-performance FastAPI-based API service that powers the comprehensive report generation system. Built with modern Python 3.12+ and utilizing advanced AI technologies, it provides speech-to-text transcription, intelligent title generation, email services, and comprehensive logging capabilities. This repository contains only the backend API; the frontend is available separately.

[![Build status](https://img.shields.io/github/actions/workflow/status/DCC-BS/bericht-backend/main.yml?branch=main)](https://github.com/DCC-BS/bericht-backend/actions/workflows/main.yml?query=branch%3Amain)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Features

- **Speech-to-Text**: High-quality audio transcription using Whisper API integration
- **AI-Powered Title Generation**: Intelligent title generation using LLM (Qwen3) models
- **Email Services**: Automated email sending with document attachments
- **Comprehensive Logging**: Structured logging with in-memory storage and REST API access
- **RESTful API**: Well-documented FastAPI endpoints with automatic OpenAPI documentation
- **Production Ready**: Docker support with multi-stage builds and SSL/TLS security
- **Type Safety**: Full type annotations compatible with Python 3.12+
- **Async Architecture**: Non-blocking asynchronous operations for optimal performance

## Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) with async/await support
- **AI/ML**: [LLM Facade](https://pypi.org/project/llm-facade/) with Qwen3 integration
- **Speech Processing**: OpenAI Whisper API for audio transcription
- **HTTP Client**: aiohttp for efficient async HTTP operations
- **Logging**: Structlog for structured logging with JSON output
- **Package Manager**: [uv](https://docs.astral.sh/uv/) for fast dependency management
- **Code Quality**: Ruff for linting and formatting, Pre-commit hooks
- **Testing**: pytest with coverage reporting
- **Documentation**: MkDocs with Material theme

## API Endpoints

### Core Services

- `POST /stt` - Speech-to-text transcription from audio files
- `POST /title` - Generate intelligent titles from text content
- `POST /send` - Send emails with document attachments

### Documentation

- `/docs` - Interactive API documentation (Swagger UI)
- `/redoc` - Alternative API documentation (ReDoc)

## Setup

### Environment Configuration

Create a `.env` file in the project root with the required environment variables:

```bash
# Whisper API Configuration
WHISPER_API=http://localhost:3000

# LLM Configuration
LLM_API=http://localhost:50002/v1
LLM_MODEL="Qwen/Qwen3-32B-AWQ"
LLM_API_KEY=your_api_key_here
```

### Pre-requisites

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.12 or higher

### Installation

1. **Create venv with uv and install dependencies:**
```bash
uv sync
```

1. **Start the development server:**
```
./run.sh
```
or directly with uv:
```bash
uv run fastapi dev src/bericht_backend/app.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Development

### Running the Application

For development with auto-reload:

```bash
uv run fastapi dev src/bericht_backend/app.py
```

For production:

```bash
uv run fastapi run src/bericht_backend/app.py
```

### Frontend Integration

This backend is designed to work with the [Bericht Frontend](https://github.com/DCC-BS/bericht-frontend) application.
Ensure both services are running and properly configured to communicate with each other.

The frontend should be configured to point to this backend's URL in its environment configuration.

## Code Quality

### Code Formatting and Linting

Format and lint code with Ruff:

```bash
# Check code quality
uv run ruff check

# Fix auto-fixable issues
uv run ruff check --fix

# Format code
uv run ruff format
```

### Type Checking

Run type checking with basedpyright:

```bash
uv run basedpyright
```

## Docker Deployment

### Production Deployment

The application includes a multi-stage Dockerfile:

```bash
# Build the Docker image
docker build -t bericht-backend .

# Run the container
docker run -p 8000:8000 \
  -e WHISPER_API=http://your-whisper-service:3000 \
  -e QWEN_BASE_URL=http://your-llm-service:11434 \
  bericht-backend
```

### Docker Compose

For local development with dependencies:

```bash
docker-compose up -d
```

This will start any required services defined in `docker-compose.yml`.

## Project Architecture

```
src/bericht_backend/
├── app.py                 # FastAPI application and route definitions
├── config.py              # Configuration management and environment variables
├── models/                # Pydantic models for request/response schemas
│   ├── generate_title_input.py
│   ├── generate_title_response.py
│   ├── log_response.py
│   ├── response_format.py
│   └── transcription_response.py
├── services/              # Business logic and external service integrations
│   ├── mail_services.py
│   ├── title_generation_service.py
│   └── whisper_services.py
├── utils/                 # Utility functions and helpers
│   └── logger.py
└── stubs/                 # Type stubs for external libraries
```

## API Usage Examples

### Speech-to-Text Transcription

```bash
curl -X POST "http://localhost:8000/stt" \
  -F "audio_file=@recording.wav"
```

### Generate Title

```bash
curl -X POST "http://localhost:8000/title" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a complaint about noise pollution in the neighborhood..."}'
```

### Send Email

```bash
curl -X POST "http://localhost:8000/send" \
  -F "to_email=recipient@example.com" \
  -F "subject=Report Document" \
  -F "email_body=Please find the attached report." \
  -F "file=@report.docx"
```

## License

[MIT](LICENSE) © Data Competence Center Basel-Stadt

---

<a href="https://www.bs.ch/schwerpunkte/daten/databs/schwerpunkte/datenwissenschaften-und-ki"><img src="https://github.com/DCC-BS/.github/blob/main/_imgs/databs_log.png?raw=true" alt="DCC Logo" width="200" /></a>

**Datenwissenschaften und KI**  
Developed with ❤️ by DCC - Data Competence Center
