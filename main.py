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

# Load environment variables from a .env file (e.g., API keys)
dotenv.load_dotenv(dotenv.find_dotenv())

def gemini_termination_condition(llm_output: GenerateContentResponse) -> bool:
    """
    Custom termination condition for agent execution.

    Returns True when the LLM's response has reached a 'STOP' condition.
    """
    return llm_output.candidates.pop().finish_reason == FinishReason.STOP


if __name__ == '__main__':
    # Initialize Google Generative AI client with appropriate API version
    api_client = genai.Client(http_options=HttpOptions(api_version="v1"))

    # Read the user's CV from PDF file
    cv = Part.from_bytes(
        data=Path("CV.pdf").read_bytes(),
        mime_type="application/pdf"
    )

    # === Agent 1: Job Categorizer ===
    categorizer_agent = JobCategorizerAgent(
        name="JobCategorizerAgent",
        model="gemini-2.0-flash-001",
        max_iterations=5,
        termination_condition=gemini_termination_condition,
        agent_scratchpad=(
            "You are a job categorization assistant helping the user identify suitable job roles based on their CV. "
            "Analyze the PDF CV and provide a structured list of relevant job titles or categories that match the user's qualifications, "
            "experience, and skills. Return the response in valid JSON format using the JobCategory schema."
        ),
        api_client=api_client,
        task=[
            cv,
            "Review my CV and provide the list of job titles that match my profile."
        ],
        generate_conf=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[JobCategory]
        )
    )

    # === Tool for web search ===
    google_search = Tool(google_search=GoogleSearch())

    # === Agent 2: Job Searcher ===
    job_search_agent = JobSearcherAgent(
        name="JobSearchAgent",
        model="gemini-2.0-flash-001",
        api_client=api_client,
        max_iterations=5,
        termination_condition=gemini_termination_condition,
        agent_scratchpad=(
            "You are an intelligent job search assistant. Given a list of job titles from memory, "
            "use the Google Search tool to find real job openings. For each relevant job, extract and return the following details:\n"
            "- Job Title\n"
            "- Company Name\n"
            "- Location\n"
            "- Job Description (brief summary)\n"
            "- Estimated Salary (if available)\n"
            "- Application Link (URL)\n"
            "Provide clean and complete results in an easily readable format for human users."
        ),
        task=[
            "Extract job titles from memory and search online for job openings. "
            "For each job, provide title, company, location, description, salary, and application link."
        ],
        generate_conf=GenerateContentConfig(
            response_modalities=["TEXT"],
            tools=[google_search],
            # automatic_function_calling=AutomaticFunctionCallingConfig(disable=True),
        )
    )

    # === Compose Agents into a Sequential Crew ===
    # JobCategorizerAgent -> JobSearcherAgent
    crew = categorizer_agent >> job_search_agent

    # === Execute the Crew ===
    crew.kickoff()

    # === Display Final Memory ===
    console = Console()
    console.print(Markdown(str(crew.memory)))
