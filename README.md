# LLM Agent Development Environment

This repository contains a Docker-based development environment for LLM agents using smolagents.

## Setup

Make the startup script executable:
```bash
chmod +x scripts/start.sh
```

Set the necessary environment variables:
```bash
export OPENROUTER_API_KEY=your_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
export QDRANT_API_KEY=your_qdrant_api_key_here
export TELEMETRY_ENABLED=true
```

## Running with Docker Compose

Build and start the container:
```bash
docker compose up --build
```

This will:
- Start the Phoenix telemetry server on http://localhost:6006
- Start the Gradio UI on http://localhost:7860

To shut it down, use `CTRL+C` and then:
```bash
docker compose down
```

## Directory Structure

- `/data`: You should put your source data here.
- `/agent_workspace`: This is where the code produced by the agents will be stored.
- `/scripts`: Contains the python scripts to run the agents service.