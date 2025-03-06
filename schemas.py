from pydantic import BaseModel


class Job(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary: str


class JobCategory(BaseModel):
    title: str
    description: str