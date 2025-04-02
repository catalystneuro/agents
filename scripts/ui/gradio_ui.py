#!/usr/bin/env python
# coding=utf-8
# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import re
import shutil
from typing import Optional

from smolagents.agent_types import AgentAudio, AgentImage, AgentText
from smolagents.agents import MultiStepAgent, PlanningStep
from smolagents.memory import ActionStep, FinalAnswerStep, MemoryStep
from smolagents.utils import _is_package_available


def get_step_footnote_content(step_log: MemoryStep, step_name: str) -> str:
    """Get a footnote string for a step log with duration and token information"""
    step_footnote = f"**{step_name}**"
    if hasattr(step_log, "input_token_count") and hasattr(step_log, "output_token_count"):
        token_str = f" | Input tokens:{step_log.input_token_count:,} | Output tokens: {step_log.output_token_count:,}"
        step_footnote += token_str
    if hasattr(step_log, "duration"):
        step_duration = f" | Duration: {round(float(step_log.duration), 2)}" if step_log.duration else None
        step_footnote += step_duration
    step_footnote_content = f"""<span style="color: #bbbbc2; font-size: 12px;">{step_footnote}</span> """
    return step_footnote_content


def pull_messages_from_step(
    step_log: MemoryStep,
):
    """Extract ChatMessage objects from agent steps with proper nesting"""
    if not _is_package_available("gradio"):
        raise ModuleNotFoundError(
            "Please install 'gradio' extra to use the GradioUI: `pip install 'smolagents[gradio]'`"
        )
    import gradio as gr

    if isinstance(step_log, ActionStep):
        # Output the step number
        step_number = f"Step {step_log.step_number}" if step_log.step_number is not None else "Step"
        yield gr.ChatMessage(role="assistant", content=f"**{step_number}**")

        # First yield the thought/reasoning from the LLM
        if hasattr(step_log, "model_output") and step_log.model_output is not None:
            # Clean up the LLM output
            model_output = step_log.model_output.strip()
            # Remove any trailing <end_code> and extra backticks, handling multiple possible formats
            model_output = re.sub(r"```\s*<end_code>", "```", model_output)  # handles ```<end_code>
            model_output = re.sub(r"<end_code>\s*```", "```", model_output)  # handles <end_code>```
            model_output = re.sub(r"```\s*\n\s*<end_code>", "```", model_output)  # handles ```\n<end_code>
            model_output = model_output.strip()
            yield gr.ChatMessage(role="assistant", content=model_output)

        # For tool calls, create a parent message
        if hasattr(step_log, "tool_calls") and step_log.tool_calls is not None:
            first_tool_call = step_log.tool_calls[0]
            used_code = first_tool_call.name == "python_interpreter"
            parent_id = f"call_{len(step_log.tool_calls)}"

            # Tool call becomes the parent message with timing info
            # First we will handle arguments based on type
            args = first_tool_call.arguments
            if isinstance(args, dict):
                content = str(args.get("answer", str(args)))
            else:
                content = str(args).strip()

            if used_code:
                # Clean up the content by removing any end code tags
                content = re.sub(r"```.*?\n", "", content)  # Remove existing code blocks
                content = re.sub(r"\s*<end_code>\s*", "", content)  # Remove end_code tags
                content = content.strip()
                if not content.startswith("```python"):
                    content = f"```python\n{content}\n```"

            parent_message_tool = gr.ChatMessage(
                role="assistant",
                content=content,
                metadata={
                    "title": f"🛠️ Used tool {first_tool_call.name}",
                    "id": parent_id,
                    "status": "pending",
                },
            )
            yield parent_message_tool

            # Nesting execution logs under the tool call if they exist
            if hasattr(step_log, "observations") and (
                step_log.observations is not None and step_log.observations.strip()
            ):  # Only yield execution logs if there's actual content
                log_content = step_log.observations.strip()
                if log_content:
                    log_content = re.sub(r"^Execution logs:\s*", "", log_content)
                    yield gr.ChatMessage(
                        role="assistant",
                        content=f"```bash\n{log_content}\n",
                        metadata={"title": "📝 Execution Logs", "parent_id": parent_id, "status": "done"},
                    )

            # Nesting any errors under the tool call
            if hasattr(step_log, "error") and step_log.error is not None:
                yield gr.ChatMessage(
                    role="assistant",
                    content=str(step_log.error),
                    metadata={"title": "💥 Error", "parent_id": parent_id, "status": "done"},
                )

            # Update parent message metadata to done status without yielding a new message
            parent_message_tool.metadata["status"] = "done"

        # Handle standalone errors but not from tool calls
        elif hasattr(step_log, "error") and step_log.error is not None:
            yield gr.ChatMessage(role="assistant", content=str(step_log.error), metadata={"title": "💥 Error"})

        yield gr.ChatMessage(role="assistant", content=get_step_footnote_content(step_log, step_number))
        yield gr.ChatMessage(role="assistant", content="-----", metadata={"status": "done"})

    elif isinstance(step_log, PlanningStep):
        yield gr.ChatMessage(role="assistant", content="**Planning step**")
        yield gr.ChatMessage(role="assistant", content=step_log.plan)
        yield gr.ChatMessage(role="assistant", content=get_step_footnote_content(step_log, "Planning step"))
        yield gr.ChatMessage(role="assistant", content="-----", metadata={"status": "done"})

    elif isinstance(step_log, FinalAnswerStep):
        final_answer = step_log.final_answer
        if isinstance(final_answer, AgentText):
            yield gr.ChatMessage(
                role="assistant",
                content=f"**Final answer:**\n{final_answer.to_string()}\n",
            )
        elif isinstance(final_answer, AgentImage):
            yield gr.ChatMessage(
                role="assistant",
                content={"path": final_answer.to_string(), "mime_type": "image/png"},
            )
        elif isinstance(final_answer, AgentAudio):
            yield gr.ChatMessage(
                role="assistant",
                content={"path": final_answer.to_string(), "mime_type": "audio/wav"},
            )
        else:
            yield gr.ChatMessage(role="assistant", content=f"**Final answer:** {str(final_answer)}")

    else:
        raise ValueError(f"Unsupported step type: {type(step_log)}")


def stream_to_gradio(
    agent,
    task: str,
    reset_agent_memory: bool = False,
    additional_args: Optional[dict] = None,
):
    """Runs an agent with the given task and streams the messages from the agent as gradio ChatMessages."""
    total_input_tokens = 0
    total_output_tokens = 0

    for step_log in agent.run(task, stream=True, reset=reset_agent_memory, additional_args=additional_args):
        # Track tokens if model provides them
        if getattr(agent.model, "last_input_token_count", None) is not None:
            total_input_tokens += agent.model.last_input_token_count
            total_output_tokens += agent.model.last_output_token_count
            if isinstance(step_log, (ActionStep, PlanningStep)):
                step_log.input_token_count = agent.model.last_input_token_count
                step_log.output_token_count = agent.model.last_output_token_count

        for message in pull_messages_from_step(
            step_log,
        ):
            yield message


class GradioUI:
    """A one-line interface to launch your agent in Gradio"""

    def __init__(self, agent: MultiStepAgent, file_upload_folder: str | None = None):
        if not _is_package_available("gradio"):
            raise ModuleNotFoundError(
                "Please install 'gradio' extra to use the GradioUI: `pip install 'smolagents[gradio]'`"
            )
        self.agent = agent
        self.file_upload_folder = file_upload_folder
        self.name = getattr(agent, "name") or "Agent interface"
        self.description = getattr(agent, "description", None)
        if self.file_upload_folder is not None:
            if not os.path.exists(file_upload_folder):
                os.mkdir(file_upload_folder)

    def interact_with_agent(self, prompt, messages, session_state):
        import gradio as gr

        # Get the agent type from the template agent
        if "agent" not in session_state:
            session_state["agent"] = self.agent

        try:
            messages.append(gr.ChatMessage(role="user", content=prompt))
            yield messages

            for msg in stream_to_gradio(session_state["agent"], task=prompt, reset_agent_memory=False):
                messages.append(msg)
                yield messages

            yield messages
        except Exception as e:
            print(f"Error in interaction: {str(e)}")
            messages.append(gr.ChatMessage(role="assistant", content=f"Error: {str(e)}"))
            yield messages

    def upload_file(self, file, file_uploads_log, allowed_file_types=None):
        """
        Handle file uploads, default allowed types are .pdf, .docx, and .txt
        """
        import gradio as gr

        if file is None:
            return gr.Textbox(value="No file uploaded", visible=True), file_uploads_log

        if allowed_file_types is None:
            allowed_file_types = [".pdf", ".docx", ".txt"]

        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in allowed_file_types:
            return gr.Textbox("File type disallowed", visible=True), file_uploads_log

        # Sanitize file name
        original_name = os.path.basename(file.name)
        sanitized_name = re.sub(
            r"[^\w\-.]", "_", original_name
        )  # Replace any non-alphanumeric, non-dash, or non-dot characters with underscores

        # Save the uploaded file to the specified folder
        file_path = os.path.join(self.file_upload_folder, os.path.basename(sanitized_name))
        shutil.copy(file.name, file_path)

        return gr.Textbox(f"File uploaded: {file_path}", visible=True), file_uploads_log + [file_path]

    def log_user_message(self, text_input, file_uploads_log):
        import gradio as gr

        return (
            text_input
            + (
                f"\nYou have been provided with these files, which might be helpful or not: {file_uploads_log}"
                if len(file_uploads_log) > 0
                else ""
            ),
            "",
            gr.Button(interactive=False),
        )

    def read_memory_bank_files(self):
        """Read all memory bank files and return their contents"""
        file_paths = [
            "/home/agent_workspace/memory_bank/active_progress_tracking.md",
            "/home/agent_workspace/memory_bank/contextual_information.md",
            "/home/agent_workspace/memory_bank/historical_progress.md",
            "/home/agent_workspace/memory_bank/project_overview.md",
            "/home/agent_workspace/memory_bank/technical_specifications.md"
        ]

        contents = []
        for file_path in file_paths:
            try:
                with open(file_path) as f:
                    content = f.read()
            except (FileNotFoundError, IOError):
                content = ""  # Empty string if file doesn't exist
            contents.append(content)

        # Add an empty string for the last empty cell
        contents.append("")

        return contents

    def launch(self, share: bool = True, **kwargs):
        self.create_app().launch(debug=True, share=share, **kwargs)

    def create_app(self):
        import gradio as gr

        with gr.Blocks(theme="ocean", fill_height=True) as demo:
            # Add session state to store session-specific data
            session_state = gr.State({})
            stored_messages = gr.State([])
            file_uploads_log = gr.State([])

            with gr.Sidebar():
                gr.Markdown(
                    """
                    # NWB converter
                    Convert your data to NWB format.
                    """
                )

                gr.FileExplorer(
                    label="Source data:",
                    interactive=False,
                    visible=True,
                    root_dir="/home/data/",
                )

                # load the text from prompts/step_by_step.md
                with open("prompts/step_by_step.md", "r") as f:
                    text_value = f.read()

                with gr.Group():
                    gr.Markdown("**Your request**", container=True)
                    text_input = gr.Textbox(
                        lines=3,
                        label="Chat Message",
                        container=False,
                        # placeholder="Enter your prompt here and press Shift+Enter or press the button",
                        value=text_value,
                    )
                    submit_btn = gr.Button("Submit", variant="primary")

                # If an upload folder is provided, enable the upload feature
                if self.file_upload_folder is not None:
                    upload_file = gr.File(label="Upload a file")
                    upload_status = gr.Textbox(label="Upload Status", interactive=False, visible=False)
                    upload_file.change(
                        self.upload_file,
                        [upload_file, file_uploads_log],
                        [upload_status, file_uploads_log],
                    )

            # Add custom CSS and JavaScript to make tabs take full height with proper scrolling, style memory bank cards, and select Memory Bank tab by default
            gr.HTML("""
            <style>
            .full-height-tabs {
                display: flex;
                flex-direction: column;
                height: calc(100vh - 200px);
                min-height: 600px;
                overflow: hidden; /* Prevent overflow at container level */
            }
            .full-height-tabs > div:nth-child(2) {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden; /* Prevent overflow at tabs level */
            }
            /* Make tab content take full height */
            .full-height-tabs > div:nth-child(2) > div {
                height: 100%;
                display: flex;
                flex-direction: column;
            }
            /* Make tab panels take full height */
            .full-height-tabs > div:nth-child(2) > div > div {
                flex-grow: 1;
                height: 100%;
                overflow-y: auto; /* Enable scrolling for tab content */
            }
            /* Memory bank tab specific styles */
            #memory-bank-tab {
                height: 100%;
                overflow-y: auto !important; /* Enable vertical scrolling */
            }
            /* Memory bank tab row container */
            #memory-bank-tab > div {
                height: 100%;
                overflow-y: auto !important;
            }
            .full-height-tabs .chatbot {
                flex-grow: 1;
                height: 100% !important;
                min-height: 500px;
                max-height: calc(100vh - 250px); /* Ensure it doesn't grow beyond viewport */
                overflow-y: auto !important; /* Enable vertical scrolling */
            }
            /* Ensure the messages container inside chatbot also scrolls properly */
            .full-height-tabs .chatbot > div {
                max-height: 100%;
                overflow-y: auto !important;
            }
            /* Style for memory bank cards */
            .memory-bank-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                margin: 10px 0;
                background-color: #f9f9f9;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                height: calc(33vh - 80px); /* Dynamically size cards to fit in viewport */
                min-height: 200px; /* Minimum height for cards */
                overflow-y: auto; /* Enable card scrolling */
                display: flex;
                flex-direction: column;
            }
            /* Make the markdown content inside cards scrollable */
            .memory-bank-card > div {
                flex-grow: 1;
                overflow-y: auto;
                padding-right: 5px; /* Add some padding for the scrollbar */
            }
            .memory-bank-card h1 {
                font-size: 1.2rem;
                margin-top: 0;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 5px;
            }
            </style>
            """)

            # Main chat interface - using Row with scale=1 to take full height
            with gr.Row(scale=1, equal_height=True):
                with gr.Column(scale=1, elem_classes=["full-height-tabs"]):
                    with gr.Tabs():  # Set "Memory Bank" as the default selected tab
                        with gr.Tab("Chatbot"):
                            chatbot = gr.Chatbot(
                                label="Agent",
                                type="messages",
                                avatar_images=(
                                    None,
                                    "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/smolagents/mascot_smol.png",
                                ),
                                resizeable=True,
                                scale=1,
                                container=True,
                                elem_classes=["chatbot"],
                            )
                        with gr.Tab("Memory Bank", elem_id="memory-bank-tab"):
                            # Add refresh button at the top
                            with gr.Row():
                                refresh_btn = gr.Button("Refresh Memory Bank", size="sm")

                            # Get initial content for memory bank files
                            initial_contents = self.read_memory_bank_files()
                            active_progress = initial_contents[0]
                            contextual_info = initial_contents[1]
                            historical_progress = initial_contents[2]
                            project_overview = initial_contents[3]
                            tech_specs = initial_contents[4]
                            empty_content = initial_contents[5]

                            # Create a 2x3 grid layout for markdown files
                            with gr.Row():
                                with gr.Column(scale=1):
                                    # First column
                                    with gr.Row():
                                        # Display active_progress_tracking.md
                                        active_progress_md = gr.Markdown(value=active_progress, elem_classes=["memory-bank-card"])
                                    with gr.Row():
                                        # Display contextual_information.md
                                        contextual_info_md = gr.Markdown(value=contextual_info, elem_classes=["memory-bank-card"])
                                    with gr.Row():
                                        # Display historical_progress.md
                                        historical_progress_md = gr.Markdown(value=historical_progress, elem_classes=["memory-bank-card"])

                                with gr.Column(scale=1):
                                    # Second column
                                    with gr.Row():
                                        # Display project_overview.md
                                        project_overview_md = gr.Markdown(value=project_overview, elem_classes=["memory-bank-card"])
                                    with gr.Row():
                                        # Display technical_specifications.md
                                        tech_specs_md = gr.Markdown(value=tech_specs, elem_classes=["memory-bank-card"])
                                    with gr.Row():
                                        # Empty cell
                                        empty_md = gr.Markdown(value=empty_content, elem_classes=["memory-bank-card"])

                            # Connect refresh button to update all markdown components
                            refresh_btn.click(
                                fn=self.read_memory_bank_files,
                                outputs=[
                                    active_progress_md,
                                    contextual_info_md,
                                    historical_progress_md,
                                    project_overview_md,
                                    tech_specs_md,
                                    empty_md
                                ]
                            )

            # Set up event handlers
            text_input.submit(
                self.log_user_message,
                [text_input, file_uploads_log],
                [stored_messages, text_input, submit_btn],
            ).then(self.interact_with_agent, [stored_messages, chatbot, session_state], [chatbot]).then(
                lambda: (
                    gr.Textbox(
                        interactive=True, placeholder="Enter your prompt here and press Shift+Enter or the button"
                    ),
                    gr.Button(interactive=True),
                ),
                None,
                [text_input, submit_btn],
            )

            submit_btn.click(
                self.log_user_message,
                [text_input, file_uploads_log],
                [stored_messages, text_input, submit_btn],
            ).then(self.interact_with_agent, [stored_messages, chatbot, session_state], [chatbot]).then(
                lambda: (
                    gr.Textbox(
                        interactive=True, placeholder="Enter your prompt here and press Shift+Enter or the button"
                    ),
                    gr.Button(interactive=True),
                ),
                None,
                [text_input, submit_btn],
            )

        return demo


__all__ = ["stream_to_gradio", "GradioUI"]
