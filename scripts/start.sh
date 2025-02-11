#!/bin/bash

echo "Starting Phoenix telemetry server..."
python -m phoenix.server.main serve &

# Wait a moment to ensure Phoenix server is up
sleep 5
echo "Phoenix server is running at http://localhost:6006"

echo "Starting LLM agent with Gradio UI..."
python scripts/run_agent_simple.py
