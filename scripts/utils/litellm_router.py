from typing import Any, Dict, List, Optional
from smolagents import Tool
from smolagents.models import ApiModel, ChatMessage


class LiteLLMRouter(ApiModel):
    """Model to use [LiteLLM Python SDK](https://docs.litellm.ai/docs/#litellm-python-sdk) to access hundreds of LLMs.

    Parameters:
        model_id (`str`):
            The model group identifier to use from the model list(e.g. "model-group-1").
        model_list (`List[Dict[Any, Any]]`)
            The models in the pool available. Refer to this document [LiteLLM Routing](https://docs.litellm.ai/docs/routing#quick-start)
        api_base (`str`, *optional*):
            The base URL of the provider API to call the model.
        api_key (`str`, *optional*):
            The API key to use for authentication.
        custom_role_conversions (`dict[str, str]`, *optional*):
            Custom role conversion mapping to convert message roles in others.
            Useful for specific models that do not support specific message roles like "system".
        flatten_messages_as_text (`bool`, *optional*): Whether to flatten messages as text.
            Defaults to `True` for models that start with "ollama", "groq", "cerebras".
        **kwargs:
            Additional keyword arguments to pass to the OpenAI API.
    """

    def __init__(
        self,
        model_id: str,
        model_list: List[Dict[Any, Any]],
        api_base=None,
        api_key=None,
        custom_role_conversions: Optional[Dict[str, str]] = None,
        flatten_messages_as_text: bool | None = None,
        **kwargs,
    ):
        try:
            from litellm import Router
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Please install 'litellm' extra to use LiteLLMModel: `pip install 'smolagents[litellm]'`"
            )
        self.model_id = model_id
        self._model_list = model_list
        self.api_base = api_base
        self.api_key = api_key
        self.custom_role_conversions = custom_role_conversions
        flatten_messages_as_text = (
            flatten_messages_as_text
            if flatten_messages_as_text is not None
            else False  # self.model_id.startswith(("ollama", "groq", "cerebras"))
        )
        super().__init__(
            model_id=model_id,
            flatten_messages_as_text=flatten_messages_as_text,
            **kwargs,
        )

    def create_client(self):
        """Create a client for the model."""
        try:
            from litellm import Router
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Please install 'litellm' extra to use LiteLLMModel: `pip install 'smolagents[litellm]'`"
            )
        self.router = Router(
            model_list=self._model_list,
            routing_strategy="simple-shuffle",
            num_retries=3,
            retry_after=5,
        )

    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        tools_to_call_from: Optional[List[Tool]] = None,
        **kwargs,
    ) -> ChatMessage:
        completion_kwargs = self._prepare_completion_kwargs(
            model=self.model_id,
            messages=messages,
            stop_sequences=stop_sequences,
            grammar=grammar,
            tools_to_call_from=tools_to_call_from,
            api_base=self.api_base,
            api_key=self.api_key,
            convert_images_to_image_urls=True,
            custom_role_conversions=self.custom_role_conversions,
            **kwargs,
        )

        response = self.router.completion(**completion_kwargs)

        self.last_input_token_count = response.usage.prompt_tokens
        self.last_output_token_count = response.usage.completion_tokens
        first_message = ChatMessage.from_dict(
            response.choices[0].message.model_dump(include={"role", "content", "tool_calls"}),
            raw=response,
        )
        return self.postprocess_message(first_message, tools_to_call_from)
