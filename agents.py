from gemini_agent import GeminiAgent
from google.genai.types import GenerateContentResponse
import typing
from logger import logger

# Job Categorizer Agent
class JobCategorizerAgent(GeminiAgent):
    def __init__(self, name: str, model: str, agent_scratchpad: str, *args, **kwargs):
        super().__init__(name, model, agent_scratchpad, *args, **kwargs)

    def use_tools(self, tool_name: str, tool_args: typing.Any) -> typing.Any:
        logger.info(f"[{self.name}] Using tool: {tool_name} with args: {tool_args}")

    def use_output(self, model_out: GenerateContentResponse) -> None:
        # if the agent has a crew
        if self.crew and model_out.parsed:
            for job_category in model_out.parsed:
                self.crew.memory.add_entry("job-categories", job_category.title)

# Job Searcher Agent
class JobSearcherAgent(GeminiAgent):
    def __init__(self, name: str, model: str, agent_scratchpad: str, *args, **kwargs):
        super().__init__(name, model, agent_scratchpad, *args, **kwargs)

    def use_tools(self, tool_name: str, tool_args: typing.Any) -> typing.Any:
        logger.info(f"[{self.name}] Using tool: {tool_name} with args: {tool_args}")
        # jobs_list = []
        # for tool_arg in tool_args:
        #     if tool_name == "get_jobs_posts_from_linkedIn":
        #         # add some dummy jobs
        #         jobs_list.append(Job(title="Software Engineer", company="Google", location="Mountain View, CA", description="Job description", salary="$150,000"))
        #     elif tool_name == "get_jobs_posts_from_glassdoor":
        #         # add some dummy jobs
        #         jobs_list.append(Job(title="Software Engineer", company="Microsoft", location="Redmond, WA", description="Job description", salary="$140,000"))
        # # update memory
        # logger.info(f"[{self.name}] Adding jobs to memory: {jobs_list}")
        # for job in jobs_list:
        #     self.crew.memory.add_entry("jobs", job.title)


    def use_output(self, model_out: GenerateContentResponse) -> None:
        # if the agent has a crew
        if self.crew:
            self.crew.memory.add_entry("jobs", model_out.text)