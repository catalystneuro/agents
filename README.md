# LLM Agent Development Environment

This repository contains a Docker-based development environment for LLM agents using smolagents.

## Prerequisites

- Docker installed on your system
- OpenRouter API key (set as environment variable)

## Setup

Make the startup script executable:
```bash
chmod +x scripts/start.sh
```

## Environment Variables

Before running the container, make sure to set your OpenRouter API key:

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

## Running with Docker Compose (Recommended)

1. Build and start the container:
```bash
docker compose up --build
```

This will:
- Start the Phoenix telemetry server on http://localhost:6006
- Start the Gradio UI on http://localhost:7860

2. For subsequent runs (without rebuilding):
```bash
docker compose up
```

The startup script will automatically:
1. Launch the Phoenix server in the background
2. Wait for it to initialize
3. Start the LLM agent with Gradio UI

## Running with Docker directly

1. Build the image:
```bash
docker build -t llm-agent .
```

2. Run the container:
```bash
docker run -p 7860:7860 -p 6006:6006 \
  -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
  -v ./data:/home/data \
  -v ./scripts:/home/scripts \
  llm-agent
```

## Accessing the Services

- Gradio UI: http://localhost:7860
- Telemetry/Phoenix: http://localhost:6006

## Directory Structure

- `./data`: Mounted as `/home/data` in the container
- `./scripts`: Mounted as `/home/scripts` in the container
  - `run_agent.py`: Main agent script that runs on container start
