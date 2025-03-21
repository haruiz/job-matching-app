import typing
import httpx
import tenacity
from google.genai.types import GenerateContentResponse
from rich.console import Console
from rich.spinner import Spinner

from base import VerbalAgent
from memory import Memory


class GeminiAgent(VerbalAgent):
    """
    GeminiAgent is a specialized implementation of VerbalAgent that interacts with the Google Gemini LLM.
    It supports iterative task execution, retries on transient API errors, and conditional termination.

    Attributes:
        name (str): Name of the agent.
        model (str): LLM model identifier to use.
        agent_scratchpad (str): Prompt or context hint to guide the model’s behavior.
        memory (Memory): Optional memory to persist and recall information.
        max_iterations (int): Maximum number of iterations for the reasoning loop.
        termination_condition (Callable): Optional function to determine when to stop iterating.
        api_client (Any): Client instance for making LLM API calls.
        task (Any): The task content or instructions the agent will execute.
        generate_conf (Dict): Optional configuration dict for content generation (e.g., tools, response schemas).
    """

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
        """
        Calls the Gemini LLM API to generate a response.

        Args:
            content (Any): The input message or task to send to the model.
            context (str): Optional contextual prefix to guide the model.

        Returns:
            GenerateContentResponse: The response from the LLM.

        Raises:
            Exception: Any API-related error not handled by retry logic.
        """
        try:
            # Add context to content if present
            if context:
                content = [str(context), content] if not isinstance(content, list) else [str(context)] + content

            # Generate content using the Gemini model
            response = self.api_client.models.generate_content(
                model=self.model,
                contents=content,
                config=self.generate_conf
            )
            return response

        except Exception as e:
            print(f"[{self.name}] API error: {str(e)}")
            raise

    def generate_response(self, content: typing.Any, context: str = None, *args, **kwargs):
        """
        Main agentic reasoning loop for executing tasks.

        Args:
            content (Any): Input content to guide the model.
            context (str): Optional context for the task.

        Returns:
            None
        """
        for i in range(self.max_iterations):
            try:
                llm_output = self.call_llm(content, context)

                # If function/tool calls are returned, process them
                if llm_output.function_calls:
                    for function_call in llm_output.function_calls:
                        self.use_tools(function_call.name, function_call.args)
                else:
                    # Use the model output directly
                    self.use_output(llm_output)

                # Stop if termination condition is satisfied
                if self.termination_condition and self.termination_condition(llm_output):
                    return

            except Exception as e:
                print(f"[{self.name}] Error: {str(e)}")
                break

    def start_task(self, context: str, *args, **kwargs) -> None:
        """
        Entry point to trigger the agent’s reasoning process.

        Args:
            context (str): Descriptive or instructional context for the task.

        Returns:
            None
        """
        spinner = Spinner("dots", text=f"agent {self.name} is working...")
        console = Console()

        with console.status(spinner):
            self.generate_response(self.task, context, *args, **kwargs)
