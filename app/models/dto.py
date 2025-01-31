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


class SurveyResponse(BaseModel):
    """
    Represents a single survey response from a user.
    """
    user: str
    responses: List[dict]  # List of responses containing question-answer pairs

class SurveyData(BaseModel):
    """
    Represents the structure of survey data including goal, hypothesis, target group, etc.
    """
    goal: str
    hypothesis: str
    target_group: str
    time_taken: int
    survey_responses: List[SurveyResponse]  # List of survey responses
