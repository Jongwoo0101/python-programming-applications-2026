# -*- coding: utf-8 -*-
"""
games/blackjack.py
규칙 기반 딜러(AI) 와의 1:1 블랙잭

- 딜러는 16 이하면 반드시 히트, 17 이상이면 반드시 스탠드 (소프트 17 스탠드)
- 블랙잭(카드 2장으로 21) 은 1.5배 지급
- 더블다운 지원
"""
from sh1_casino.cards import Deck


def hand_value(cards):
    """(합계, 소프트여부) 반환. 소프트 = 에이스를 11로 계산 중인 상태"""
    total = 0
    aces = 0
    for c in cards:
        if c.rank == 14:
            total += 11
            aces += 1
        elif c.rank >= 10:
            total += 10
        else:
            total += c.rank
    soft = False
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    if aces > 0 and total <= 21:
        soft = True
    return total, soft


RESULT_LABELS = {
    "player_blackjack": "블랙잭! 승리 (1.5배 지급)",
    "player_win": "승리",
    "dealer_bust": "딜러 버스트! 승리",
    "push": "무승부 (베팅액 반환)",
    "dealer_win": "패배",
    "player_bust": "버스트! 패배",
}


class BlackjackGame:
    def __init__(self, bet: int):
        self.bet = bet
        self.deck = Deck()
        self.player = self.deck.draw(2)
        self.dealer = self.deck.draw(2)
        self.finished = False
        self.doubled = False
        self.result = None  # RESULT_LABELS의 key 중 하나

    # ---------------------------------------------------------- 조회
    def player_value(self):
        return hand_value(self.player)

    def dealer_value(self):
        return hand_value(self.dealer)

    def dealer_hidden_card(self):
        """딜러의 두번째 카드를 라운드가 끝나기 전까지 숨김 처리할 때 사용"""
        return self.dealer[1] if len(self.dealer) > 1 else None

    # ---------------------------------------------------------- 진행
    def check_initial_blackjack(self) -> bool:
        """딜러/플레이어 중 누구든 초기 2장으로 21이면 즉시 정산하고 True 반환"""
        pv, _ = self.player_value()
        dv, _ = self.dealer_value()
        if pv == 21 or dv == 21:
            self._settle()
            return True
        return False

    def player_hit(self):
        self.player += self.deck.draw(1)
        pv, _ = self.player_value()
        if pv > 21:
            self.finished = True
            self.result = "player_bust"
        return pv

    def player_double(self):
        """더블다운: 베팅액 2배, 카드 1장만 받고 강제 스탠드"""
        self.doubled = True
        self.bet *= 2
        pv = self.player_hit()
        if not self.finished:
            self.player_stand()
        return pv

    def player_stand(self):
        while True:
            dv, soft = self.dealer_value()
            if dv < 17:
                self.dealer += self.deck.draw(1)
            else:
                break
        self._settle()
        return self.result

    def _settle(self):
        self.finished = True
        pv, _ = self.player_value()
        dv, _ = self.dealer_value()
        player_bj = len(self.player) == 2 and pv == 21
        dealer_bj = len(self.dealer) == 2 and dv == 21

        if player_bj and dealer_bj:
            self.result = "push"
        elif player_bj:
            self.result = "player_blackjack"
        elif dealer_bj:
            self.result = "dealer_win"
        elif pv > 21:
            self.result = "player_bust"
        elif dv > 21:
            self.result = "dealer_bust"
        elif pv > dv:
            self.result = "player_win"
        elif pv < dv:
            self.result = "dealer_win"
        else:
            self.result = "push"

    def payout(self):
        """원래 베팅액(더블 전) 대비 순손익(토큰 증감량)을 반환"""
        base_bet = self.bet // 2 if self.doubled else self.bet
        if self.result == "player_blackjack":
            return int(base_bet * 1.5)
        if self.result in ("player_win", "dealer_bust"):
            return self.bet
        if self.result == "push":
            return 0
        return -self.bet

    def result_label(self) -> str:
        return RESULT_LABELS.get(self.result, "")

    def csv_result(self) -> str:
        """csv_logger 저장용 표준 result 값"""
        if self.result in ("player_blackjack", "player_win", "dealer_bust"):
            return "win"
        if self.result == "push":
            return "push"
        return "lose"
