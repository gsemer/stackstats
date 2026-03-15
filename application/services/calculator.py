import logging
from collections import defaultdict
from typing import List, Dict, Any

from domain.models import Answer, Comment
from domain.interfaces import CalculatorInterface


logger = logging.getLogger("stackexchange_api")


class Calculator(CalculatorInterface):
    """
    Computes statistics from answers and comments.
    """

    async def compute_statistics(self, answers: List[Answer], comments: List[Comment]) -> Dict[str, Any]:
        """
        Compute statistics from lists of answers and comments.

        Args:
            answers: List of Answer objects retrieved from the StackExchange API.
            comments: List of Comment objects associated with the answers.

        Returns:
            dict containing:
                - total_accepted_answers
                - accepted_answers_average_score
                - average_answers_per_question
                - top_ten_answers_comment_count
        """

        logger.info("Starting computation of statistics...")

        # Total accepted answers
        total_accepted = sum(1 for answer in answers if answer.is_accepted)

        # Average score of accepted answers
        accepted_scores = [answer.score for answer in answers if answer.is_accepted]
        avg_score = round(sum(accepted_scores) / len(accepted_scores), 1) if accepted_scores else 0

        # Average answers per question
        question_map = defaultdict(int)
        for answer in answers:
            question_map[answer.question_id] += 1
        avg_answers_per_question = round(sum(question_map.values()) / len(question_map), 1) if question_map else 0

        # Top 10 answers by score
        top_answers = sorted(answers, key=lambda answer: answer.score, reverse=True)[:10]
        # Map comments count to top answers
        comment_map = defaultdict(int)
        for comment in comments:
            comment_map[comment.answer_id] += 1

        top_comments = {
            str(answer.answer_id): comment_map.get(answer.answer_id, 0) 
            for answer in top_answers
        }

        logger.info("Finished computation of statistics.")

        return {
            "total_accepted_answers": total_accepted,
            "accepted_answers_average_score": avg_score,
            "average_answers_per_question": avg_answers_per_question,
            "top_ten_answers_comment_count": top_comments
        }
