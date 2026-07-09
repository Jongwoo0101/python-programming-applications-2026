# -*- coding: utf-8 -*-
"""
sh1_casino/quiz_manager.py
학습 리커버리용 퀴즈 문제를 data/quizzes.json 에서 불러온다.

문제를 추가/수정/삭제하고 싶으면 코드를 건드릴 필요 없이
data/quizzes.json 파일만 편집하면 된다. 형식:

[
  {
    "id": 1,
    "category": "프로그래밍",
    "question": "파이썬에서 리스트의 길이를 구하는 내장 함수는?",
    "answer": "len",
    "reward": 500
  },
  ...
]

answer 비교는 대소문자/앞뒤 공백을 무시하고 비교한다.
"""
import os
import json
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUIZ_PATH = os.path.join(BASE_DIR, "data", "quizzes.json")

_cache = None


def _load():
    global _cache
    try:
        with open(QUIZ_PATH, encoding="utf-8") as f:
            _cache = json.load(f)
    except FileNotFoundError:
        _cache = []
    return _cache


def reload():
    """JSON 파일을 다시 읽어 최신 문제 목록을 반영한다."""
    return _load()


def get_all_quizzes():
    if _cache is None:
        _load()
    return _cache


def get_random_quiz(exclude_id=None):
    quizzes = get_all_quizzes()
    if not quizzes:
        return None
    candidates = [q for q in quizzes if q.get("id") != exclude_id] or quizzes
    return random.choice(candidates)


def check_answer(quiz: dict, user_answer: str) -> bool:
    correct_answers = quiz.get("answer")
    given = str(user_answer).strip().lower()

    if not correct_answers or not given:
        return False

    # 1. 정답이 리스트(배열) 형태로 여러 개 등록된 경우
    if isinstance(correct_answers, list):
        # 리스트 안의 모든 정답을 소문자/공백제거 상태로 변환하여 비교
        valid_answers = [str(ans).strip().lower() for ans in correct_answers]
        return given in valid_answers
    
    # 2. 정답이 기존처럼 단일 문자열로 등록된 경우
    else:
        correct = str(correct_answers).strip().lower()
        return correct == given
