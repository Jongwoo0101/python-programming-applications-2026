# -*- coding: utf-8 -*-
"""
csv_logger.py
게임 플레이 기록을 CSV 파일로 저장/조회하고, 승률/누적손익 등 통계를 계산한다.

CSV 컬럼 : timestamp, username, game_type, bet_amount, result, chip_change, chips_after
"""
import os
import csv
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, "game_logs.csv")

FIELDNAMES = ["timestamp", "username", "game_type", "bet_amount", "result",
              "chip_change", "chips_after"]

# result 값 표준화: "win" / "lose" / "push" (무승부/푸시)
WIN_RESULTS = {"win"}
LOSE_RESULTS = {"lose"}
PUSH_RESULTS = {"push"}


def _ensure_csv():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def log_game(username: str, game_type: str, bet_amount: int, result: str,
             chip_change: int, chips_after: int):
    """게임 한 판이 끝날 때마다 호출하여 로그를 남긴다."""
    _ensure_csv()
    with open(CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "game_type": game_type,
            "bet_amount": bet_amount,
            "result": result,
            "chip_change": chip_change,
            "chips_after": chips_after,
        })


def get_user_logs(username: str):
    """최신 순으로 정렬된 해당 사용자의 로그 리스트(dict)를 반환"""
    _ensure_csv()
    rows = []
    with open(CSV_PATH, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                rows.append(row)
    rows.reverse()
    return rows


def get_user_stats(username: str):
    """
    게임별 통계 + 전체 통계를 계산해서 반환.
    {
      "overall": {"plays": n, "wins": n, "losses": n, "pushes": n,
                   "win_rate": float, "total_bet": n, "net_profit": n},
      "by_game": {game_type: {...동일 구조...}, ...}
    }
    """
    logs = get_user_logs(username)

    def _new_stat():
        return {"plays": 0, "wins": 0, "losses": 0, "pushes": 0,
                "total_bet": 0, "net_profit": 0}

    overall = _new_stat()
    by_game = {}

    for row in logs:
        game_type = row["game_type"]
        bet = int(row["bet_amount"])
        chip_change = int(row["chip_change"])
        result = row["result"]

        stat = by_game.setdefault(game_type, _new_stat())
        for target in (overall, stat):
            target["plays"] += 1
            target["total_bet"] += bet
            target["net_profit"] += chip_change
            if result in WIN_RESULTS:
                target["wins"] += 1
            elif result in LOSE_RESULTS:
                target["losses"] += 1
            else:
                target["pushes"] += 1

    def _finalize(stat):
        stat["win_rate"] = round((stat["wins"] / stat["plays"]) * 100, 1) if stat["plays"] else 0.0
        return stat

    overall = _finalize(overall)
    by_game = {k: _finalize(v) for k, v in by_game.items()}

    return {"overall": overall, "by_game": by_game}
