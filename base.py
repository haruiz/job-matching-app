from __future__ import annotations
import typing
from abc import ABC, abstractmethod
from memory import Memory
from logger import logger


class VerbalAgent(ABC):
    """
    Abstract base class representing a verbal (LLM-powered) agent.

    A VerbalAgent performs tasks by communicating with a language model,
    optionally using tools and interacting with shared memory. It supports
    termination conditions and can be composed into sequential multi-agent crews.
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
    ):
        """
        Initializes the VerbalAgent.

        Args:
            name (str): The agent's name identifier.
            model (str): The model name to be used (e.g., Gemini).
            agent_scratchpad (str): Prompt/context that defines agent behavior.
            memory (Memory, optional): A shared memory store; new one created if not provided.
            max_iterations (int): Max iterations for response generation.
            termination_condition (Callable, optional): Function to check if agent should stop.
            api_client (Any, optional): Client for calling the LLM API.
            task (Any, optional): The input task or instruction to complete.
        """
        self.name = name
        self.agent_scratchpad = agent_scratchpad
        self.model = model
        self.memory = memory or Memory()
        self.max_iterations = max_iterations
        self.termination_condition = termination_condition
        self.api_client = api_client
        self.task = task
        self.crew: SequentialVerbalAgentCrew | None = None

    def __rshift__(self, other: VerbalAgent) -> SequentialVerbalAgentCrew:
        """
        Enables chaining of agents using the '>>' operator to form a sequential crew.

        Args:
            other (VerbalAgent): The next agent to execute after this one.

        Returns:
            SequentialVerbalAgentCrew: A composite crew of the two agents.
        """
        return SequentialVerbalAgentCrew(self, other)

    def use_tools(self, tool_name: str, args: typing.Dict[str, typing.Any]) -> None:
        """
        Placeholder for subclasses to implement logic for using tools.

        Args:
            tool_name (str): The name of the tool to be used.
            args (dict): Arguments required to use the tool.
        """
        ...

    def use_output(self, llm_output: typing.Any) -> None:
        """
        Placeholder for subclasses to implement output handling logic.

        Args:
            llm_output (Any): The output received from the language model.
        """
        ...

    @abstractmethod
    def call_llm(self, content: typing.Any, context: str, *args, **kwargs):
        """
        Abstract method to call the LLM with input content and context.

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_response(self, content: typing.Any, *args, **kwargs) -> str:
        """
        Abstract method representing the agent's core logic loop.

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def start_task(self, context: str, *args, **kwargs) -> None:
        """
        Abstract method to initiate the task execution process.

        Must be implemented by subclasses.
        """
        raise NotImplementedError


class SequentialVerbalAgentCrew:
    """
    A controller class for chaining VerbalAgents into a sequential pipeline.

    Agents share a single memory object and are executed in the order they are added.
    """

    def __init__(self, *agents: VerbalAgent):
        """
        Initializes the SequentialVerbalAgentCrew and assigns shared memory to all agents.

        Args:
            *agents (VerbalAgent): One or more agents to be executed in sequence.
        """
        self.memory = Memory()
        self.agents = list(agents)
        for agent in self.agents:
            agent.crew = self  # Attach the shared crew reference

    def kickoff(self):
        """
        Executes all agents in sequence using shared memory as context.
        """
        logger.info(f"Starting crew with agents: {[agent.name for agent in self.agents]}")
        for agent in self.agents:
            agent.start_task(context=str(self.memory))
