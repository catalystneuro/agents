FROM python:3.11

# Set working directory to home
WORKDIR /home

# Copy requirements file
COPY requirements.txt /home/requirements.txt

# Install Python dependencies from requirements file
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# temporary pip install from source
# RUN pip install git+https://github.com/huggingface/smolagents.git

# Copy scripts directory
COPY scripts /home/scripts

# Set default command
CMD ["/home/scripts/start.sh"]
