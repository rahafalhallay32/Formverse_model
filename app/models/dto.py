from pydantic import BaseModel
from typing import List

class ResearcherInput(BaseModel):
    """
    Represents the input data from the researcher when creating a research form.
    """
    goal: str
    hypothesis: str
    target_group: str
    time_taken: int

class SummarizeInput(BaseModel):
    """
    Represents the input data needed for summarizing survey responses.
    """
    goal: str
    hypothesis: str
    target_group: str
    time_taken: int
    user_responses: List[str]  # A list of user responses to summarize

class SurveyResponse(BaseModel):
    """
    Represents a single survey response from a user.
    """
    response: str
