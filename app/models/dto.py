from pydantic import BaseModel
from typing import List, Optional, Union

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

class Question(BaseModel):
    question: str
    questionType: str
    options: List[str]
    isRequired: bool
    _id: str
    answers: Optional[List[List[str]]] = None

class FormData(BaseModel):
    _id: str
    title: str
    questions: List[Question]
    summary: Optional[str] = None
    user: str
    isPublished: bool
    isActive: bool
    isGenerated: bool
    isResultsShared: bool
    goal: Optional[str] = None
    hypothesis: Optional[str] = None
    targetGroup: Optional[str] = None
    timeTaken: Optional[Union[str, int]] = None