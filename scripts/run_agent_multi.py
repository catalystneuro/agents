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

# Tools
logger.info("Initializing tools...")
working_dir = "/home/agent_workspace"

neuroconv_tool = NeuroconvSpecialistTool(
    return_digest_summary=False,
    llm_model="openrouter/openai/o3-mini",
)
write_to_file_tool = WriteToFileTool(work_dir=working_dir)
read_file_tool = ReadFileTool(work_dir=working_dir)
replace_in_file_tool = ReplaceInFileTool(work_dir=working_dir)
search_files_tool = SearchFilesTool(work_dir=working_dir)
list_files_tool = ListFilesTool(work_dir=working_dir)
directory_tree_tool = DirectoryTreeTool(work_dir=working_dir)
execute_command_tool = ExecuteCommandInTerminalTool(allowed_dirs=[working_dir])
create_nwb_repo_tool = CreateNWBRepoTool()
nwb_inspector_tool = NWBInspectorTool()

# Agents
logger.info("Initializing agents...")

nwb_specialist_agent = ToolCallingAgent(
    name="nwb_conversion_specialist_agent",
    description="""This agent is a specialist in NWB conversion. It can write, organize and run NWB conversion projects.""",
    tools=[
        write_to_file_tool,
        read_file_tool,
        replace_in_file_tool,
        search_files_tool,
        list_files_tool,
        directory_tree_tool,
        execute_command_tool,
        neuroconv_tool,
        create_nwb_repo_tool,
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
    ],
    # model=LiteLLMModel("openrouter/anthropic/claude-3.7-sonnet"),
    model=LiteLLMModel("openrouter/google/gemini-2.5-pro-exp-03-25:free"),
    # planning_interval=3,
    max_steps=20,
    add_base_tools=False,
)

nwb_inspector_agent = ToolCallingAgent(
    name="nwb_inspector_agent",
    description="""This agent is a specialist in NWB inspection. It can analyze and validate NWB files.""",
    tools=[
        read_file_tool,
        search_files_tool,
        list_files_tool,
        directory_tree_tool,
        nwb_inspector_tool,
    ],
    # model=LiteLLMModel("openrouter/anthropic/claude-3.7-sonnet"),
    # model=LiteLLMModel("openrouter/openai/o3-mini-high"),
    model=LiteLLMModel("openrouter/google/gemini-2.5-pro-exp-03-25:free"),
    # planning_interval=3,
    max_steps=5,
    add_base_tools=False,
)

manager_agent = CodeAgent(
    name="manager_agent",
    tools=[
        PythonInterpreterTool(),
    ],
    # model=LiteLLMModel("openrouter/anthropic/claude-3.7-sonnet"),
    # model=LiteLLMModel("openrouter/openai/o3-mini-high"),
    model=LiteLLMModel("openrouter/google/gemini-2.5-pro-exp-03-25:free"),
    managed_agents=[
        nwb_specialist_agent,
        nwb_inspector_agent,
    ],
    # planning_interval=3,
    max_steps=40,
    add_base_tools=False,
)

demo = GradioUI(manager_agent).create_app()


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
        # manager_agent.run("hello, how are you?")
    except Exception as e:
        logger.error(f"Failed to start Gradio interface: {str(e)}")
        raise
