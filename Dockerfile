FROM python:3.11

# Set working directory to home
WORKDIR /home

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    "neuroconv[deeplabcut,spikeglx]==0.6.7" \
    "smolagents[gradio,litellm,mcp,openai,telemetry]==1.9.0" \
    instructor \
    qdrant-client \
    nwbinspector \
    dandi \
    "directory-tree==1.0.0" \
    "cookiecutter==2.6.0" \
    jupyterlab

# RUN pip install

# Copy scripts directory
COPY scripts /home/scripts

# Set default command
CMD ["/home/scripts/start.sh"]
