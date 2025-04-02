#!/usr/bin/env python
# coding=utf-8
import os
import re
import shutil
from typing import Optional

import gradio as gr


class SimpleGradioUI:
    """A simplified Gradio UI without smolagents dependencies"""

    def __init__(self, name: str = "Simple Chat Interface", description: Optional[str] = None, file_upload_folder: Optional[str] = None):
        self.name = name
        self.description = description
        self.file_upload_folder = file_upload_folder

        # Create upload folder if specified and doesn't exist
        if self.file_upload_folder is not None:
            if not os.path.exists(self.file_upload_folder):
                os.mkdir(self.file_upload_folder)

    def chat_response(self, prompt, messages, session_state):
        """Simple chat response function"""
        try:
            # Add user message
            messages.append(gr.ChatMessage(role="user", content=prompt))
            yield messages

            # Add assistant response
            response = f"You said: {prompt}\n\nThis is a simple response from the assistant."
            messages.append(gr.ChatMessage(role="assistant", content=response))
            yield messages

        except Exception as e:
            print(f"Error in interaction: {str(e)}")
            messages.append(gr.ChatMessage(role="assistant", content=f"Error: {str(e)}"))
            yield messages

    def upload_file(self, file, file_uploads_log, allowed_file_types=None):
        """
        Handle file uploads, default allowed types are .pdf, .docx, and .txt
        """
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
        if self.file_upload_folder is not None:
            file_path = os.path.join(self.file_upload_folder, os.path.basename(sanitized_name))
            shutil.copy(file.name, file_path)
        else:
            file_path = "File uploaded but no storage location specified"

        return gr.Textbox(f"File uploaded: {file_path}", visible=True), file_uploads_log + [file_path]

    def log_user_message(self, text_input, file_uploads_log):
        """Process user message and handle file uploads"""
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

    def launch(
        self,
        debug: bool = False,
        share: bool = True,
        **kwargs,
    ):
        """Launch the Gradio app"""
        self.create_app().launch(debug=debug, share=share, **kwargs)

    def create_app(self):
        """Create the Gradio app interface"""
        with gr.Blocks(theme="ocean", fill_height=True) as demo:
            # Add session state to store session-specific data
            session_state = gr.State({})
            stored_messages = gr.State([])
            file_uploads_log = gr.State([])

            with gr.Sidebar():
                gr.Markdown(
                    f"# {self.name.replace('_', ' ').capitalize()}"
                    "\n> This web UI provides a simple chat interface."
                )

                with gr.Group():
                    gr.Markdown("**Your request**", container=True)
                    text_input = gr.Textbox(
                        lines=3,
                        label="Chat Message",
                        container=False,
                        placeholder="Enter your message here and press Shift+Enter or press the button",
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

                gr.HTML("<br><br><h4><center>Simple Gradio Chat</center></h4>")

            with gr.Tab("Lion"):
                gr.Button("New Lion")
            with gr.Tab("Chatbot"):
                # Main chat interface
                chatbot = gr.Chatbot(
                    label="Chat",
                    type="messages",
                    avatar_images=(None, None),
                    resizeable=True,
                    scale=1,
                )

            # Set up event handlers
            text_input.submit(
                self.log_user_message,
                [text_input, file_uploads_log],
                [stored_messages, text_input, submit_btn],
            ).then(self.chat_response, [stored_messages, chatbot, session_state], [chatbot]).then(
                lambda: (
                    gr.Textbox(
                        interactive=True, placeholder="Enter your message here and press Shift+Enter or the button"
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
            ).then(self.chat_response, [stored_messages, chatbot, session_state], [chatbot]).then(
                lambda: (
                    gr.Textbox(
                        interactive=True, placeholder="Enter your message here and press Shift+Enter or the button"
                    ),
                    gr.Button(interactive=True),
                ),
                None,
                [text_input, submit_btn],
            )

        return demo


if __name__ == "__main__":
    # Create a simple UI with file upload capability
    upload_folder = os.path.join(os.getcwd(), "uploads")
    # Ensure the upload folder exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    demo = SimpleGradioUI(
        name="Simple Gradio Chat",
        description="A standalone Gradio chat interface without smolagents dependencies.",
        file_upload_folder=upload_folder
    )
    # Launch the app
    demo.launch(
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7860,       # Match the exposed port
        debug=True,
        share=False,
    )
