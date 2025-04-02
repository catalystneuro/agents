import os
from smolagents import (
    CodeAgent,
    LiteLLMModel,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    MemoryBankTool,
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

# Tools
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

# Agents
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
    model=LiteLLMModel("openrouter/anthropic/claude-3.7-sonnet"),
    # model=LiteLLMModel("openrouter/google/gemini-2.5-pro-exp-03-25:free"),
    max_steps=50,
    planning_interval=2,
    add_base_tools=True,
    use_memory_bank=True,
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
        raise e
