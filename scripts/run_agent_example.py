from smolagents import (
    CodeAgent,
    LiteLLMModel,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    MemoryBankTool,
)


working_dir = "/home/agent_workspace"

memory_bank_tool = MemoryBankTool(
    memory_bank_dir_path=f"{working_dir}/memory_bank",
)

# Agents
agent = CodeAgent(
    tools=[
        memory_bank_tool,
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
    ],
    model=LiteLLMModel("openrouter/anthropic/claude-3.7-sonnet"),
    max_steps=50,
    planning_interval=3,
    add_base_tools=True,
    use_memory_bank=True,
)

request = """
Do a deep research about vaccines:
- find the 5 most common vaccines used throughout the world nowadays
- find source material about the safety profile of each one of these vaccines
- find recommendations of application of these vaccines for public authorities, including schedules, target groups and other
similar relevant information
- add some historical context about each vaccine, including the year of introduction and the disease it is meant to prevent
- produce a final report with the relevant content summarized in a single markdown document, with references cited where needed
"""

response = agent.run(request)
print(response)

# save the final report
with open(f"{working_dir}/vaccine_report.md", "w") as f:
    f.write(response)
