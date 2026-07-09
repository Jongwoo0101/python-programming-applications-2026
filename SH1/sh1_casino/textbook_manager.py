# -*- coding: utf-8 -*-
"""
sh1_casino/textbook_manager.py
토큰으로 해금 가능한 온라인 교재 목록을 data/textbooks.json 에서 불러온다.

교재를 추가/수정하고 싶으면 data/textbooks.json 파일만 편집하면 된다. 형식:

[
  {
    "id": "book_python_1",
    "title": "파이썬 기초 완성",
    "cost": 15000,
    "desc": "파이썬 문법의 기초를 다집니다."
  },
  ...
]
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_PATH = os.path.join(BASE_DIR, "data", "textbooks.json")

_cache = None


def _load():
    global _cache
    try:
        with open(BOOKS_PATH, encoding="utf-8") as f:
            _cache = json.load(f)
    except FileNotFoundError:
        _cache = []
    return _cache


def reload():
    return _load()


def get_all_books():
    if _cache is None:
        _load()
    return _cache


def get_book(book_id):
    for b in get_all_books():
        if b["id"] == book_id:
            return b
    return None
