#!/bin/bash

if [ "$TELEMETRY_ENABLED" = "true" ]; then
    echo "Starting Phoenix telemetry server..."
    python -m phoenix.server.main serve &

    # Wait a moment to ensure Phoenix server is up
    sleep 5
fi

echo "Starting LLM agent with Gradio UI..."
python scripts/run_agent_simple.py
# cd scripts
# gradio run_agent_simple.py

# # Wait a moment to ensure LLM agent is up
# sleep 3
# echo "Phoenix server is running at http://localhost:6006"
# echo "Gradio server is running at http://localhost:7860"