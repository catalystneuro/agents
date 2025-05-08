import os
import yaml
import json
import argparse
from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
)

from utils.logger import set_logger
from tools.neuroconv_specialist_tool import NeuroconvSpecialistTool
from tools.git_repo_tools import CreateNWBRepoTool
from tools.nwbinspector_tool import NWBInspectorTool
from tools.file_system_tools import (
    WriteToFileTool,
    ReadFileTool,
    ReplaceInFileTool,
    SearchFilesTool,
    ListFilesTool,
    DirectoryTreeTool,
)
from tools.cli_tools import ExecuteCommandInTerminalTool
from tools.memory_bank_tool import MemoryBankTool
from ui.gradio_ui import GradioUI
from utils.litellm_router import LiteLLMRouter


######################################################
# Basic setup
######################################################
# Telemetry
if os.getenv("TELEMETRY_ENABLED", "false").lower() == "true":
    from utils.telemetry import set_telemetry
    set_telemetry()

# Configure logging
logger = set_logger(name=__name__)

# Check environment variables
if not os.getenv("OPENROUTER_API_KEY", None):
    logger.error("OPENROUTER_API_KEY environment variable is not set")
    raise ValueError("Please set the OPENROUTER_API_KEY environment variable.")

######################################################
# Tools
######################################################
logger.info("Initializing tools...")
working_dir = "/home/agent_workspace"

write_to_file_tool = WriteToFileTool(work_dir=working_dir)
read_file_tool = ReadFileTool(work_dir=working_dir)
replace_in_file_tool = ReplaceInFileTool(work_dir=working_dir)
search_files_tool = SearchFilesTool(work_dir=working_dir)
list_files_tool = ListFilesTool(work_dir=working_dir)
directory_tree_tool = DirectoryTreeTool(work_dir=working_dir)
execute_command_tool = ExecuteCommandInTerminalTool(allowed_dirs=[working_dir])

create_nwb_repo_tool = CreateNWBRepoTool()
nwb_inspector_tool = NWBInspectorTool()
neuroconv_specialist_tool = NeuroconvSpecialistTool(
    return_digest_summary=False,
    llm_model="openrouter/openai/o3-mini",
)

memory_bank_tool = MemoryBankTool(
    memory_bank_dir_path=f"{working_dir}/memory_bank",
)

######################################################
# Prompt templates
######################################################
this_dir = os.path.dirname(os.path.abspath(__file__))
prompt_file = os.path.join(this_dir, "prompts", "code_agent.yaml")
with open(prompt_file, 'r') as f:
    prompt_templates = yaml.safe_load(f)

######################################################
# Select model
######################################################
model_list = [
    # {
    #     "model_name": "o4-mini-high",
    #     "litellm_params": {
    #         "model": "openrouter/openai/o4-mini-high",
    #         "api_key": os.getenv("OPENROUTER_API_KEY"),
    #         "weight": 1,
    #     }
    # },
    # {
    #     "model_name": "o4-mini",
    #     "litellm_params": {
    #         "model": "openrouter/openai/o4-mini",
    #         "api_key": os.getenv("OPENROUTER_API_KEY"),
    #         "weight": 1,
    #     }
    # },
    # {
    #     "model_name": "gpt-41",
    #     "litellm_params": {
    #         "model": "openrouter/openai/gpt-4.1",
    #         "api_key": os.getenv("OPENROUTER_API_KEY"),
    #         "weight": 1,
    #     }
    # },
    {
        "model_name": "claude-37",
        "litellm_params": {
            "model": "openrouter/anthropic/claude-3.7-sonnet",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "weight": 1,
        }
    },
    # {
    #     "model_name": "qwen",
    #     "litellm_params": {
    #         "model": "openrouter/qwen/qwen3-235b-a22b",
    #         "api_key": os.getenv("OPENROUTER_API_KEY"),
    #         "weight": 1,
    #     }
    # },
    # {
    #     "model_name": "gemini",
    #     "litellm_params": {
    #         "model": "openrouter/google/gemini-2.5-pro-preview",
    #         "api_key": os.getenv("OPENROUTER_API_KEY"),
    #         "weight": 1,
    #     }
    # },
]

router_config = {
    # "routing_strategy": "simple-shuffle",
    "num_retries": 3,
    "retry_after": 30,
    # "fallbacks": [
    #     {"o4-mini-high": ["04-mini"]},
    #     {"o4-mini": ["qwen"]},
    #     {"qwen": ["o4-mini-high"]},
    # ],
}

model = LiteLLMRouter(
    model_id=model_list[0]["model_name"],
    model_list=model_list,
    router_config=router_config,
)

######################################################
# Agents
######################################################
logger.info("Initializing agent...")
agent = CodeAgent(
    tools=[
        write_to_file_tool,
        read_file_tool,
        replace_in_file_tool,
        search_files_tool,
        list_files_tool,
        directory_tree_tool,
        execute_command_tool,
        create_nwb_repo_tool,
        nwb_inspector_tool,
        neuroconv_specialist_tool,
        memory_bank_tool,
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
    ],
    model=model,
    max_steps=70,
    planning_interval=2,
    add_base_tools=True,
    prompt_templates=prompt_templates,
)


######################################################
# Main function - script entry point
######################################################
if __name__ == "__main__":
    def parse_arguments():
        parser = argparse.ArgumentParser(description='Run the agent in different modes')
        parser.add_argument('--run-mode', type=str, help='Mode to run the agent (e.g., "script")')
        return parser.parse_args()

    try:
        args = parse_arguments()
        if args.run_mode == "script":
            logger.info("Running in script mode...")

            # request = "Hi, how are you? Tell me a random fact about the universe."
            step_by_step_file = os.path.join(this_dir, "prompts", "step_by_step.md")
            with open(step_by_step_file, 'r') as f:
                request = f.read()
            response = agent.run(request)
            with open(f"{working_dir}/response.log", "w") as f:
                f.write(str(response))

            with open(f"{working_dir}/usage.json", "w") as f:
                json.dump(model.usage_tracking, f, indent=4)
        else:
            logger.info("Starting Gradio interface...")
            demo = GradioUI(agent).create_app()
            demo.launch(
                server_name="0.0.0.0",
                server_port=7860,
                debug=True,
                share=False,
            )

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
