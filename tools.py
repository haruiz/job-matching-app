from google.genai.types import (
    FunctionDeclaration, Tool, Schema, GoogleSearch,
)

get_jobs_from_linkedIn_api = Tool(function_declarations=[
    FunctionDeclaration(
        name="get_jobs_posts_from_linkedIn",
        description="Return job posts from LinkedIn.",
        parameters= Schema(
            type='OBJECT',
            properties={
                'job_title': Schema(type='STRING'),
            }
        ),
    )
])
get_jobs_from_glassdoor_api = Tool(function_declarations=[
    FunctionDeclaration(
        name="get_jobs_posts_from_glassdoor",
        description="Return job posts from Glassdoor.",
        parameters=Schema(
            type='OBJECT',
            properties={
                'job_title': Schema(type='STRING'),
            }
        ),
    )
])

google_search = Tool(google_search=GoogleSearch())
