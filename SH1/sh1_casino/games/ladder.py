# -*- coding: utf-8 -*-
"""
games/ladder.py
사다리타기 (경마 컨셉) - 5개의 레인 중 하나를 선택해 베팅한다.
배당률이 높을수록 당첨 확률이 낮아지도록 설계 (레인별 기대값이 균일하도록 정규화).
"""
import random

# (배당 배수, 이름)
LANES = [
    {"multiplier": 2, "name": "빨강", "color": "#c0392b"},
    {"multiplier": 3, "name": "파랑", "color": "#2980b9"},
    {"multiplier": 5, "name": "노랑", "color": "#f1c40f"},
    {"multiplier": 10, "name": "초록", "color": "#27ae60"},
    {"multiplier": 100, "name": "보라", "color": "#8e44ad"},
]

# 레인별 확률 = C / 배수  (C는 확률의 합이 1이 되도록 정규화된 상수)
_inv_sum = sum(1.0 / lane["multiplier"] for lane in LANES)
_C = 1.0 / _inv_sum
WEIGHTS = [_C / lane["multiplier"] for lane in LANES]


def run_race():
    """당첨 레인의 인덱스(0~4)를 반환"""
    return random.choices(range(len(LANES)), weights=WEIGHTS, k=1)[0]


def play(lane_index: int, bet: int):
    """
    베팅한 레인과 베팅액을 받아 결과를 계산한다.
    반환: (승리여부: bool, 당첨레인 인덱스: int, 순손익(칩 증감): int)
    """
    winner_idx = run_race()
    if winner_idx == lane_index:
        multiplier = LANES[lane_index]["multiplier"]
        net = bet * (multiplier - 1)  # 베팅액은 이미 낸 상태이므로 순이익만 계산
        return True, winner_idx, net
    return False, winner_idx, -bet
