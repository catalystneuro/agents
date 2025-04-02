FROM python:3.11

# Set working directory to home
WORKDIR /home

# Copy requirements file
COPY catalystneuro_agents/requirements.txt /home/requirements.txt

# Install Python dependencies from requirements file
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy smolagents package to the image (assuming it's in the build context)
# and install it in editable mode
COPY smolagents /home/smolagents
RUN cd /home/smolagents && pip install -e .

# Copy scripts directory
# COPY scripts /home/scripts
COPY catalystneuro_agents/scripts /home/scripts

# Set default command
CMD ["/home/scripts/start.sh"]
