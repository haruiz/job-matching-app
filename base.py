
from memory import Memory
from abc import ABC, abstractmethod
import typing
from logger import logger

class VerbalAgent(ABC):
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
        self.name = name
        self.agent_scratchpad = agent_scratchpad
        self.model = model
        self.memory = memory or Memory()
        self.max_iterations = max_iterations
        self.termination_condition = termination_condition
        self.api_client = api_client
        self.task = task
        self.crew = None

    def __rshift__(self, other: "VerbalAgent") -> "SequentialCrew":
        return SequentialCrew(self, other)

    def use_tools(self, tool_name: str, args: typing.Dict[str, typing.Any]) -> None:
        ...

    def use_output(self, llm_output: typing.Any) -> None:
        ...

    @abstractmethod
    def call_llm(self, content: typing.Any, context: str, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def generate_response(self, content: typing.Any, *args, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def start_task(self, context: str, *args, **kwargs) -> None:
        raise NotImplementedError


class SequentialCrew:
    def __init__(self, *agents: VerbalAgent):
        self.memory = Memory()
        self.agents = list(agents)
        for agent in self.agents:
            agent.crew = self
            agent.memory = self.memory

    def kickoff(self):
        logger.info(f"Starting crew with agents: {[agent.name for agent in self.agents]}")
        for agent in self.agents:
            agent.start_task(context=str(self.memory))