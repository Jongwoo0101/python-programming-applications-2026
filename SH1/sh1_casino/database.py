# -*- coding: utf-8 -*-
"""
database.py
SQLite3 기반 회원 정보 / 보유 칩 / 일일 베팅 한도 관리

테이블
  users        : id, username, password_hash, salt, nickname, chips, daily_limit, created_at
  daily_bets   : username, bet_date, total_bet   (일일 베팅 한도 체크용, 날짜별 누적 베팅액)
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

DEFAULT_CHIPS = 10000
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            nickname TEXT NOT NULL,
            chips INTEGER NOT NULL DEFAULT 10000,
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
            """INSERT INTO users (username, password_hash, salt, nickname, chips,
                                   daily_limit, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (username, pw_hash, salt, nickname, DEFAULT_CHIPS, DEFAULT_DAILY_LIMIT,
             datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
    finally:
        conn.close()


def authenticate(username: str, password: str):
    """성공 시 user dict 반환, 실패 시 AuthError 발생"""
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


# ---------------------------------------------------------------- 칩 / 한도 관리
def update_chips(username: str, delta: int) -> int:
    """chips += delta (음수 가능). 갱신된 chips 값을 반환"""
    conn = get_connection()
    try:
        row = conn.execute("SELECT chips FROM users WHERE username = ?", (username,)).fetchone()
        if row is None:
            raise AuthError("사용자를 찾을 수 없습니다.")
        new_chips = max(0, row["chips"] + delta)
        conn.execute("UPDATE users SET chips = ? WHERE username = ?", (new_chips, username))
        conn.commit()
        return new_chips
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
    """(허용여부: bool, 사유/메시지: str) 반환"""
    user = get_user(username)
    if user is None:
        return False, "사용자를 찾을 수 없습니다."
    if bet_amount <= 0:
        return False, "베팅 금액은 1 이상이어야 합니다."
    if bet_amount > user["chips"]:
        return False, "보유 칩이 부족합니다."
    today_total = get_today_bet_total(username)
    limit = user["daily_limit"]
    if today_total + bet_amount > limit:
        remaining = max(0, limit - today_total)
        return False, f"일일 베팅 한도를 초과합니다. (오늘 남은 한도: {remaining}칩)"
    return True, ""
