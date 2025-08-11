import pytest
from src.travelplay.schema import Worksheet, QuizItem


def test_quiz_index_validation():
    ws = Worksheet(
        title="Test",
        age=8,
        destination="Tokyo",
        fun_facts=["Fact 1"],
        quiz=[QuizItem(q="Q1", a=["A", "B", "C"], correct=1)],
    )
    assert ws.quiz[0].correct == 1


def test_quiz_index_out_of_range():
    with pytest.raises(Exception):
        Worksheet(
            title="Bad", age=8, destination="Rome", quiz=[QuizItem(q="Q1", a=["A", "B"], correct=5)]
        )
