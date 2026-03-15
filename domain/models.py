from dataclasses import dataclass

@dataclass(slots=True)
class Answer:
    """Represents a StackOverflow answer."""
    answer_id: int
    question_id: int
    score: int
    is_accepted: bool


@dataclass(slots=True)
class Comment:
    """Represents a comment on a StackOverflow answer."""
    comment_id: int
    answer_id: int
