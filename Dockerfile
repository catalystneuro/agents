FROM python:3.11

# Set working directory to home
WORKDIR /home

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    "smolagents[gradio,litellm,mcp,openai,telemetry]==1.8.1" \
    instructor \
    qdrant-client \
    "neuroconv==0.6.7" \
    nwbinspector \
    dandi \
    jupyterlab

# Copy scripts directory
COPY scripts /home/scripts

# Set default command
CMD ["/home/scripts/start.sh"]
