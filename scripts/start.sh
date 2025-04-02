#!/bin/bash

# if [ "$TELEMETRY_ENABLED" = "true" ]; then
#     echo "Starting Phoenix telemetry server..."
#     python -m phoenix.server.main serve &

#     # Wait a moment to ensure Phoenix server is up
#     sleep 5
# fi

# Start Jupyter lab server
echo "Starting Jupyter lab server..."

cd /home/agent_workspace
jupyter lab --no-browser --allow-root --port=8889 --ip=0.0.0.0 \
    --NotebookApp.token='' \
    --NotebookApp.disable_check_xsrf=True \
    --NotebookApp.tornado_settings="{'headers': {'Content-Security-Policy': 'frame-ancestors *'}}" \
    --NotebookApp.allow_origin='*' &

echo "Jupyter lab server is running at http://localhost:8889"

# Start Gradio server
echo "Starting LLM agent with Gradio UI..."
cd /home/scripts
gradio run_agent_simple.py
# gradio run_agent_multi.py
# python test_telemetry.py
# python run_agent_example.py


# python scripts/run_agent_simple.py
# cd scripts
# gradio run_agent_simple.py

# # Wait a moment to ensure LLM agent is up
# sleep 3
# echo "Phoenix server is running at http://localhost:6006"
# echo "Gradio server is running at http://localhost:7860"