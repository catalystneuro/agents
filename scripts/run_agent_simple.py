import os
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    LiteLLMModel,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    PythonInterpreterTool,
    GradioUI,
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

logger.info("Initializing models and tools...")

# Models
# code_model = LiteLLMModel("openrouter/anthropic/claude-3.5-sonnet")
code_model = LiteLLMModel("openrouter/google/gemini-2.0-flash-001")
# code_model = LiteLLMModel("openrouter/google/gemini-2.0-pro-exp-02-05:free")

# Tools
neuroconv_tool = NeuroconvSpecialistTool(
    return_digest_summary=False,
    llm_model="openrouter/openai/o3-mini",
)
write_to_file_tool = WriteToFileTool()
read_file_tool = ReadFileTool()
replace_in_file_tool = ReplaceInFileTool()
search_files_tool = SearchFilesTool()
list_files_tool = ListFilesTool()
directory_tree_tool = DirectoryTreeTool()
execute_command_tool = ExecuteCommandInTerminalTool()
create_nwb_repo_tool = CreateNWBRepoTool()
nwb_inspector_tool = NWBInspectorTool()

# More tools
extra_tools = [
    write_to_file_tool,
    read_file_tool,
    replace_in_file_tool,
    search_files_tool,
    list_files_tool,
    directory_tree_tool,
    execute_command_tool,
    create_nwb_repo_tool,
    nwb_inspector_tool,
]

# Agents
agent = CodeAgent(
    tools=[
        neuroconv_tool,
        *extra_tools,
    ],
    model=code_model,
    max_steps=40,
    planning_interval=2,
    add_base_tools=True,
)

demo = GradioUI(agent).create_app()


if __name__ == "__main__":
    try:
        logger.info("Starting Gradio interface...")
        # Configure Gradio to be accessible from outside the container
        demo.launch(
            server_name="0.0.0.0",  # Listen on all interfaces
            server_port=7860,       # Match the exposed port
            debug=True,
            share=False,
        )
    except Exception as e:
        logger.error(f"Failed to start Gradio interface: {str(e)}")
        raise