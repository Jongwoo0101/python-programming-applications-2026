# -*- coding: utf-8 -*-
"""
games/ladder.py
사다리타기 - 5개의 레인 중 하나를 선택해 참여 토큰을 투자한다.
배당이 높은(당첨확률 낮은) 레인일수록 낮은 확률로 가중치를 부여해
어떤 레인을 골라도 기댓값이 동일하도록 설계되어 있다 (공정한 확률).
"""
import random

LANES = [
    {"multiplier": 2, "name": "빨강", "color": "#e63946"},
    {"multiplier": 3, "name": "파랑", "color": "#4fb3ff"},
    {"multiplier": 5, "name": "노랑", "color": "#f2b705"},
    {"multiplier": 10, "name": "초록", "color": "#33d17a"},
    {"multiplier": 100, "name": "보라", "color": "#b98cff"},
]

_inv_sum = sum(1.0 / lane["multiplier"] for lane in LANES)
_C = 1.0 / _inv_sum
WEIGHTS = [_C / lane["multiplier"] for lane in LANES]


def run_race():
    return random.choices(range(len(LANES)), weights=WEIGHTS, k=1)[0]


def play(lane_index: int, bet: int):
    """
    반환: (승리여부: bool, 당첨레인 인덱스: int, 순손익(토큰 증감): int)
    """
    winner_idx = run_race()
    if winner_idx == lane_index:
        multiplier = LANES[lane_index]["multiplier"]
        net = bet * (multiplier - 1)
        return True, winner_idx, net
    return False, winner_idx, -bet
