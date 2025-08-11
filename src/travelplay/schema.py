from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List

class QuizItem(BaseModel):
    q: str = Field(..., min_length=3)
    a: List[str] = Field(..., min_items=2)
    correct: int = Field(..., ge=0)

    @field_validator("correct")
    def correct_index_in_range(cls, v, info):
        a = info.data.get("a", [])
        if not (0 <= v < len(a)):
            raise ValueError("correct index must be within range of answers")
        return v

class Worksheet(BaseModel):
    title: str = Field(..., min_length=3)
    age: int = Field(..., ge=3, le=12)
    destination: str = Field(..., min_length=2)
    fun_facts: List[str] = Field(default_factory=list, max_items=5)
    quiz: List[QuizItem] = Field(default_factory=list)
