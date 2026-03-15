from pydantic import BaseModel
from typing import Dict


class StackStatsResponse(BaseModel):
    total_accepted_answers: int
    accepted_answers_average_score: float
    average_answers_per_question: float
    top_ten_answers_comment_count: Dict[str, int]
