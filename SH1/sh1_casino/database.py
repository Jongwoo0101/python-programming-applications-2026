# -*- coding: utf-8 -*-
"""
database.py
SQLite3 기반 회원 정보 / 토큰 / 일일 베팅 한도 / 교재 해금 관리

[변경] 퀴즈 문제는 더 이상 이 파일(DB)에 하드코딩하지 않습니다.
       data/quizzes.json 에서 관리합니다 (sh1_casino/quiz_manager.py 참고).
       문제를 추가/수정하고 싶으면 그 JSON 파일만 편집하면 됩니다.
"""
import os
import sqlite3
import hashlib
import secrets
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "sh1.db")

DEFAULT_TOKENS = 10000
DEFAULT_DAILY_LIMIT = 100000


class AuthError(Exception):
    """회원가입/로그인 관련 오류"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()

    # 구버전 DB(chips 컬럼 존재) 마이그레이션 처리
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [row["name"] for row in cursor.fetchall()]
        if columns and "chips" in columns and "tokens" not in columns:
            conn.execute("ALTER TABLE users RENAME COLUMN chips TO tokens;")
            conn.commit()
    except Exception:
        pass

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            nickname TEXT NOT NULL,
            tokens INTEGER NOT NULL DEFAULT 10000,
            daily_limit INTEGER NOT NULL DEFAULT 100000,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_bets (
            username TEXT NOT NULL,
            bet_date TEXT NOT NULL,
            total_bet INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (username, bet_date)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS unlocked_books (
            username TEXT NOT NULL,
            book_id TEXT NOT NULL,
            unlocked_at TEXT NOT NULL,
            PRIMARY KEY (username, book_id)
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------- 비밀번호
def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- 회원가입 / 로그인
def create_user(username: str, password: str, nickname: str):
    username = username.strip()
    nickname = nickname.strip()
    if not username or not password or not nickname:
        raise AuthError("아이디, 비밀번호, 닉네임을 모두 입력해주세요.")
    if len(password) < 4:
        raise AuthError("비밀번호는 4자 이상이어야 합니다.")

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            raise AuthError("이미 존재하는 아이디입니다.")

        salt = secrets.token_hex(16)
        pw_hash = _hash_password(password, salt)
        conn.execute(
            """INSERT INTO users (username, password_hash, salt, nickname, tokens,
                                   daily_limit, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (username, pw_hash, salt, nickname, DEFAULT_TOKENS, DEFAULT_DAILY_LIMIT,
             datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
    finally:
        conn.close()


def authenticate(username: str, password: str):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()
        if row is None:
            raise AuthError("존재하지 않는 아이디입니다.")
        if _hash_password(password, row["salt"]) != row["password_hash"]:
            raise AuthError("비밀번호가 일치하지 않습니다.")
        return dict(row)
    finally:
        conn.close()


def get_user(username: str):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ---------------------------------------------------------------- 토큰 / 한도 관리
def update_tokens(username: str, delta: int) -> int:
    conn = get_connection()
    try:
        row = conn.execute("SELECT tokens FROM users WHERE username = ?", (username,)).fetchone()
        if row is None:
            raise AuthError("사용자를 찾을 수 없습니다.")
        new_tokens = max(0, row["tokens"] + delta)
        conn.execute("UPDATE users SET tokens = ? WHERE username = ?", (new_tokens, username))
        conn.commit()
        return new_tokens
    finally:
        conn.close()


def set_daily_limit(username: str, new_limit: int):
    if new_limit < 0:
        raise AuthError("한도는 0 이상이어야 합니다.")
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET daily_limit = ? WHERE username = ?", (new_limit, username))
        conn.commit()
    finally:
        conn.close()


def _today() -> str:
    return date.today().isoformat()


def get_today_bet_total(username: str) -> int:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT total_bet FROM daily_bets WHERE username = ? AND bet_date = ?",
            (username, _today()),
        ).fetchone()
        return row["total_bet"] if row else 0
    finally:
        conn.close()


def add_today_bet(username: str, amount: int):
    conn = get_connection()
    try:
        today = _today()
        row = conn.execute(
            "SELECT total_bet FROM daily_bets WHERE username = ? AND bet_date = ?",
            (username, today),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE daily_bets SET total_bet = total_bet + ? WHERE username = ? AND bet_date = ?",
                (amount, username, today),
            )
        else:
            conn.execute(
                "INSERT INTO daily_bets (username, bet_date, total_bet) VALUES (?, ?, ?)",
                (username, today, amount),
            )
        conn.commit()
    finally:
        conn.close()


def check_bet_allowed(username: str, bet_amount: int):
    user = get_user(username)
    if user is None:
        return False, "사용자를 찾을 수 없습니다."
    if bet_amount <= 0:
        return False, "참여 토큰은 1 이상이어야 합니다."
    if bet_amount > user["tokens"]:
        return False, "보유 토큰이 부족합니다."
    today_total = get_today_bet_total(username)
    limit = user["daily_limit"]
    if today_total + bet_amount > limit:
        remaining = max(0, limit - today_total)
        return False, f"일일 사용 한도를 초과합니다. (오늘 남은 한도: {remaining} 토큰)"
    return True, ""


# ---------------------------------------------------------------- 교재 해금 관리
def unlock_book(username: str, book_id: str, cost: int) -> bool:
    conn = get_connection()
    try:
        user = conn.execute("SELECT tokens FROM users WHERE username = ?", (username,)).fetchone()
        if user is None or user["tokens"] < cost:
            return False

        new_tokens = user["tokens"] - cost
        conn.execute("UPDATE users SET tokens = ? WHERE username = ?", (new_tokens, username))
        conn.execute(
            "INSERT INTO unlocked_books (username, book_id, unlocked_at) VALUES (?, ?, ?)",
            (username, book_id, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_unlocked_books(username: str):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT book_id FROM unlocked_books WHERE username = ?", (username,)
        ).fetchall()
        return [row["book_id"] for row in rows]
    finally:
        conn.close()
