from typing import Literal

from pydantic import BaseModel, Field

Language = Literal["mixed", "python", "javascript", "sql"]


class NewGame(BaseModel):
    language: Language = "mixed"
    rounds: int = Field(5, ge=3, le=10)


class AnswerIn(BaseModel):
    line: int | None = None  # None means "I ran out of time"


class SubmitIn(BaseModel):
    name: str
