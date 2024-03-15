
from pydantic import BaseModel, Field
from enum import Enum

class QuestionType(str, Enum):
    numeric = "numeric"
    text = "text"
    date = "date"
    choice = "choice"


class ChatMessage(BaseModel):
    role: str
    content: str

class QuestionMessage(BaseModel):
    question: str = Field(..., description="the question to ask the user to clarify the context.")
    type: QuestionType = Field(..., alias="type", description="the type of question, it can be numeric, text, date, choice. If the type is choice, the choices field must be filled.")
    choices: list[str] = Field(default_factory=list, description="a list of choices for the question, only used when the type is choice.")
