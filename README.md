# # Multi-Agent Job Search Framework

## Overview
This project is a **from-scratch implementation** of a **multi-agent system** for educational purposes. It demonstrates how multiple AI agents can collaborate to analyze resumes, categorize job opportunities, and search for relevant job listings on the internet using **Google's Gemini API**.

## Features
- **Modular Multi-Agent System**: Agents are designed to work sequentially, passing data through a shared memory.
- **Job Categorization**: Extracts relevant job categories based on user-provided resumes.
- **Automated Job Searching**: Searches online for job listings matching the identified categories.
- **API Integration**: Uses the Gemini LLM API to generate content dynamically.
- **Retry Mechanism**: Implements fault tolerance with `tenacity` for API calls.

## Agents
1. **JobCategorizerAgent** - Analyzes a user’s resume and identifies relevant job categories.
2. **JobSearchAgent** - Uses job categories from memory to search for relevant job listings.

## Technologies Used
- **Python** (core language)
- **Google Gemini API** (LLM-based job categorization and search)
- **Pydantic** (data validation)
- **Tenacity** (retry mechanism for API calls)
- **Httpx** (HTTP client)
- **Rich Logging** (enhanced terminal logging output)

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/multi-agent-job-search.git
   cd multi-agent-job-search
   ```
2. Install dependencies:
   ```sh
   uv sync
   ```
3. Add your **Gemini API Key** to a `.env` file:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage
Run the script to start the multi-agent execution:
```sh
python main.py
```

## Future Improvements
- Implement parallel execution of agents
- Expand tool integrations (LinkedIn, Glassdoor, Indeed APIs)
- Enhance response validation and feedback loops
- Add more multi-agents patterns (e.g. Supervisor, Hierarchical, Nested Agents)

## License
This project is provided **for educational purposes only**. Feel free to modify and extend the functionality!