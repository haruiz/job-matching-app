from pathlib import Path

import dotenv
import google.genai as genai
from google.genai.types import (
    GenerateContentConfig,
    Part,
    HttpOptions,
    FinishReason,
    GenerateContentResponse,
    Tool, GoogleSearch,
)
from schemas import JobCategory
from agents import JobCategorizerAgent, JobSearcherAgent
from rich.console import Console
from rich.markdown import Markdown

# Load environment variables
dotenv.load_dotenv(dotenv.find_dotenv())


if __name__ == '__main__':
    api_client = genai.Client(http_options=HttpOptions(api_version="v1"))
    def gemini_termination_condition(llm_output: GenerateContentResponse) -> bool:
        return llm_output.candidates.pop().finish_reason == FinishReason.STOP

    cv = Part.from_bytes(data=Path("CV.pdf").read_bytes(), mime_type="application/pdf")
    categorizer_agent = JobCategorizerAgent(
        name="JobCategorizerAgent",
        model="gemini-2.0-flash-001",
        max_iterations=5,
        termination_condition=gemini_termination_condition,
        agent_scratchpad="You are a job search assistant categorizing jobs.",
        api_client=api_client,
        task=[cv, "Review my CV and provide the list of jobs that match my profile"],
        generate_conf=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[JobCategory]
        )
    )
    google_search = Tool(google_search=GoogleSearch())
    job_search_agent = JobSearcherAgent(
        name="JobSearchAgent",
        model="gemini-2.0-flash-001",
        api_client=api_client,
        max_iterations=5,
        termination_condition=gemini_termination_condition,
        agent_scratchpad="Find job listings matching user profile.",
        task=["Extract job categories from memory and search online for job openings. "
              "For each job, provide title, company, location, description, salary, and application link."],
        generate_conf=GenerateContentConfig(
            response_modalities=["TEXT"],
            tools=[google_search],
            # automatic_function_calling=AutomaticFunctionCallingConfig(disable=True),
        )
    )

    crew = categorizer_agent >> job_search_agent
    crew.kickoff()
    console = Console()
    console.print(Markdown(str(crew.memory)))