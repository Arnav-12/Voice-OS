# VoiceAgentOS - Multi-Agent Voice Intelligence Platform

A production-ready, LangGraph and Langchain-powered voice automation system that processes audio through intelligent agent workflows.

##  Quick Start (30-minute deployment)

### 1. Clone and Setup
```bash
git clone https://github.com/Arnav-12/Voice-OS.git
cd voiceagent-os
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 2. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build -d

# Check logs
docker-compose logs -f voiceagent-api
```

### 4. Cloud Deployment (Railway/Render)

#### Railway:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### Render:
1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `GROQ_API_KEY`

##  Testing the API

### Upload and Process Audio
```bash
curl -X POST "http://localhost:8000/process-audio" \
  -F "file=@your-audio-file.mp3" \
  -F "task_type=summary"
```

### Check Job Status
```bash
curl "http://localhost:8000/job-status/{job_id}"
```

### Download Generated Audio
```bash
curl "http://localhost:8000/download-audio/{job_id}" -o response.mp3
```

##  Architecture

The system uses LangGraph to orchestrate multiple AI agents:

1. **Transcribe Agent** - Converts audio to text (Whisper)
2. **Language Detector** - Identifies language
3. **Task Router** - Routes to appropriate processor
4. **Processing Agents** - Summary/Q&A/Action Items
5. **TTS Agent** - Converts response to speech

## Configuration

### Environment Variables
- `GROQ_API_KEY` - Your GROQ API key
- `REDIS_URL` - Redis connection string
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)

### Task Types
- `summary` - Generate content summary
- `qa` - Answer questions about content
- `action_items` - Extract actionable tasks

##  Monitoring

- Health check: `GET /health`
- API docs: `http://localhost:8000/docs`
- Logs: `docker-compose logs -f voiceagent-api`

##  Production Considerations

1. **Scaling**: Use Redis for job queuing
2. **Storage**: Replace temp files with cloud storage
3. **Security**: Add authentication middleware
4. **Monitoring**: Add Prometheus metrics
5. **Rate Limiting**: Add request throttling

##  Extending the System

### Add New Agent
```python
async def my_custom_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    # Your logic here
    return state

# Add to graph in app/agents/graph.py
workflow.add_node("my_agent", my_custom_agent)
```

### Custom Task Types
Add new enum values to `TaskType` in `schemas.py` and corresponding logic in `task_router_agent`.

##  Troubleshooting

### Common Issues
1. **Missing OpenAI Key**: Ensure `GROQ_API_KEY` is set
2. **Audio Format**: Only MP3, WAV, M4A, FLAC, OGG supported
3. **Memory Issues**: Large audio files may need more RAM
4. **Network Timeouts**: Increase proxy timeout for long audio

### Debug Mode
```bash
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

This system is production-ready and can handle real-world voice processing workloads!
```

##  30-Minute Deployment Guide

### Option 1: Local Development (5 minutes)
```bash
# 1. Save all files to voiceagent-os/ directory
# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variable
export GROQ_API_KEY="your-key-here"

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker Deployment (10 minutes)
```bash
# 1. Create .env file with your OpenAI key
echo "GROQ_API_KEY=your-key-here" > .env

# 2. Build and run
docker-compose up --build -d

# 3. Test
curl http://localhost/health
```

### Option 3: Railway Cloud Deploy (15 minutes)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Initialize and deploy
railway login
railway init
railway add # Add PostgreSQL if needed
railway up

# 3. Set environment variables in Railway dashboard
# GROQ_API_KEY=your-key-here
```

##  Test the System

Upload an audio file and get intelligent responses:

```bash
# Test summary generation
curl -X POST "http://localhost:8000/process-audio" \
  -F "file=@test-audio.mp3" \
  -F "task_type=summary"

# Test Q&A mode
curl -X POST "http://localhost:8000/process-audio" \
  -F "file=@test-audio.mp3" \
  -F "task_type=qa"
```

The system will return transcription, intelligent processing, and a downloadable audio response!
