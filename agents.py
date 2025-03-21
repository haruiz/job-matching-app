from gemini_agent import GeminiAgent
from google.genai.types import GenerateContentResponse
import typing
from logger import logger

# Job Categorizer Agent
class JobCategorizerAgent(GeminiAgent):
    """
    Agent responsible for categorizing job titles based on a given user profile (e.g., a resume).
    Inherits behavior from GeminiAgent and implements custom tool usage and output handling.

    Responsibilities:
    - Use tools (if any) and log their usage.
    - Parse the model's structured output (job categories) and store them in shared memory.
    """

    def __init__(self, name: str, model: str, agent_scratchpad: str, *args, **kwargs):
        """
        Initializes the JobCategorizerAgent with model configuration and scratchpad instructions.

        Args:
            name (str): Agent name identifier.
            model (str): Gemini model to use.
            agent_scratchpad (str): Prompt-like instructions to guide LLM behavior.
            *args, **kwargs: Additional arguments passed to the base GeminiAgent.
        """
        super().__init__(name, model, agent_scratchpad, *args, **kwargs)

    def use_tools(self, tool_name: str, tool_args: typing.Any) -> typing.Any:
        """
        Logs the usage of a tool (if any tools are available).

        Args:
            tool_name (str): Name of the tool being called.
            tool_args (Any): Arguments to the tool.
        """
        logger.info(f"[{self.name}] Using tool: {tool_name} with args: {tool_args}")

    def use_output(self, model_out: GenerateContentResponse) -> None:
        """
        Handles the model's output by extracting job categories and saving them to memory.

        Args:
            model_out (GenerateContentResponse): The structured response from the LLM.
        """
        if self.crew and model_out.parsed:
            for job_category in model_out.parsed:
                self.crew.memory.add_entry("job-categories", job_category.title)


# Job Searcher Agent
class JobSearcherAgent(GeminiAgent):
    """
    Agent responsible for searching job listings based on categorized job titles.
    Inherits behavior from GeminiAgent and handles tool-based job search and memory persistence.

    Responsibilities:
    - Use external tools like Google Search to find jobs.
    - Store search results (textual) into shared memory for later use or display.
    """

    def __init__(self, name: str, model: str, agent_scratchpad: str, *args, **kwargs):
        """
        Initializes the JobSearcherAgent with model configuration and scratchpad instructions.

        Args:
            name (str): Agent name identifier.
            model (str): Gemini model to use.
            agent_scratchpad (str): Prompt-like instructions to guide LLM behavior.
            *args, **kwargs: Additional arguments passed to the base GeminiAgent.
        """
        super().__init__(name, model, agent_scratchpad, *args, **kwargs)

    def use_tools(self, tool_name: str, tool_args: typing.Any) -> typing.Any:
        """
        Logs the usage of a tool, such as a search function.

        Args:
            tool_name (str): Name of the tool being invoked.
            tool_args (Any): Arguments passed to the tool.
        """
        logger.info(f"[{self.name}] Using tool: {tool_name} with args: {tool_args}")

    def use_output(self, model_out: GenerateContentResponse) -> None:
        """
        Stores raw model output (job search results) in shared memory under 'jobs' key.

        Args:
            model_out (GenerateContentResponse): The textual response from the LLM.
        """
        if self.crew:
            self.crew.memory.add_entry("jobs", model_out.text)
