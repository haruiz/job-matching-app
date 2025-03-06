import typing

import httpx
import tenacity
from google.genai.types import GenerateContentResponse
from rich.console import Console
from rich.spinner import Spinner

from base import VerbalAgent
from memory import Memory


# class OpenAIAgent(VerbalAgent):


class GeminiAgent(VerbalAgent):
    def __init__(
        self,
        name: str,
        model: str,
        agent_scratchpad: str,
        memory: Memory = None,
        max_iterations: int = 5,
        termination_condition: typing.Optional[typing.Callable] = None,
        api_client: typing.Optional[typing.Any] = None,
        task: typing.Any = None,
        generate_conf: typing.Optional[typing.Dict] = None,
    ):
        super().__init__(
            name=name,
            model=model,
            agent_scratchpad=agent_scratchpad,
            memory=memory,
            max_iterations=max_iterations,
            termination_condition=termination_condition,
            api_client=api_client,
            task=task,
        )
        self.generate_conf = generate_conf

    @tenacity.retry(
        wait=tenacity.wait_fixed(1),
        stop=tenacity.stop_after_attempt(5),
        retry=tenacity.retry_if_exception_type(httpx.HTTPStatusError)
    )
    def call_llm(self, content: typing.Any, context: str = None, *args, **kwargs) -> GenerateContentResponse:
        try:
            # add context to content
            if context:
                content = [str(context), content] if not isinstance(content, list) else [str(context)] + content
            # call LLM API
            response = self.api_client.models.generate_content(
                model=self.model, contents=content, config=self.generate_conf
            )
            return response
        except Exception as e:
            print(f"[{self.name}] API error: {str(e)}")
            raise

    # agentic loop
    def generate_response(self, content: typing.Any, context: str = None, *args, **kwargs):
        for i in range(self.max_iterations):
            try:
                llm_output = self.call_llm(content, context)
                if llm_output.function_calls:
                    for function_call in llm_output.function_calls:
                        # Use tools to process function calls
                        self.use_tools(function_call.name, function_call.args)
                else:
                    # Use output from LLM directly
                    self.use_output(llm_output)
                # Check termination condition
                if self.termination_condition and self.termination_condition(llm_output):
                    return
            except Exception as e:
                print(f"[{self.name}] Error: {str(e)}")
                break

    def start_task(self, context: str, *args, **kwargs) -> None:
        # Generate response from LLM
        spinner = Spinner("dots", text=f"agent {self.name} is working...")
        console = Console()
        with console.status(spinner):
            self.generate_response(self.task, context, *args, **kwargs)
