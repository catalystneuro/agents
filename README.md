# LLM Agents for NWB conversion

LLM agents for NWB conversion is a project that utilizes large language models (LLMs) to assist in the conversion of neurophysiology data into the Neurodata Without Borders (NWB) format. The project is designed to be flexible and extensible, allowing users to adapt the agents to their specific needs.

The agents run in a Docker environment, guaranteeing reproducibility and ease of deployment.

- Agents are written in Python using the [smolagents](https://github.com/huggingface/smolagents)
- NWB conversion is done with [NeuroConv](https://github.com/catalystneuro/neuroconv) and [PyNWB](https://github.com/NeurodataWithoutBorders/pynwb)
- Results validation is done with [nwbinspector](https://github.com/NeurodataWithoutBorders/nwbinspector)

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
```

The environment variables necessary will depend on the models you are using in the `Select model` section in `scripts/run_agent_simple.py`.

## Running with Docker Compose

Build and start the container:
```bash
docker compose up --build
```

This will start the Gradio UI at http://localhost:7860.

To shut it down, use `CTRL+C` and then:
```bash
docker compose down
```

## Running with Docker

Build the image:
```
docker build -t catalystneuro_agent .
```

Run the container:
```bash
docker run \
  --name llm-agent \
  -e OPENROUTER_API_KEY=${OPENROUTER_API_KEY} \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  -e QDRANT_API_KEY=${QDRANT_API_KEY} \
  -e TELEMETRY_ENABLED=${TELEMETRY_ENABLED} \
  -v "$(pwd)/data:/home/data" \
  -v "$(pwd)/scripts:/home/scripts" \
  -v "$(pwd)/agent_workspace:/home/agent_workspace" \
  catalystneuro_agent
```

Stop the container:
```bash
docker stop llm-agent
```

## Directory Structure

- `/data`: You should put your source data here.
- `/agent_workspace`: This is where the code produced by the agents will be stored.
- `/scripts`: Contains the python scripts to run the agents service.

## Prompting the CatalystNeuro Agents

Some useful prompt templates can be found in the `scripts/prompts/` directory. Adapt these to your use case.

## Batch testing
You can run multiple parallel agents with the same configuration using the `run_batch.py` script.

1. export the necessary environment variables
2. build the docker image
3. organize the source data in the `data` directory
4. `python run_batch.py --n 10` (where `n` is the number of agents to run in parallel)

The source data should be organized in the `data` directory as follows:
```
data/
├── <protocol_name>/
│   ├── <session_name>/
│   │   ├── <data_file_1>
│   │   ├── <data_file_2>
│   │   └── ...
│   ├── <session_name_2>/
│   │   ├── <data_file_1>
│   │   ├── <data_file_2>
│   │   └── ...
│   └── ...
├── <protocol_name_2>/
│   ├── <session_name>/
│   │   ├── <data_file_1>
│   │   ├── <data_file_2>
│   │   └── ...
│   ├── ...
```

The `run_batch.py` script will create a new directory for each agent in the `agent_workspace` directory, and each agent will process the data in its own directory.
