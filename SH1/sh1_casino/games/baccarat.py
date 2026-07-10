# -*- coding: utf-8 -*-
"""
games/baccarat.py
규칙 기반 바카라 로직 (표준 서드 카드 룰 적용)

- 뱅커 승리 시 5% 커미션 차감 (0.95배 지급)
- 플레이어 승리 시 1:1 지급
- 타이 승리 시 8:1 지급
- 타이가 나왔을 때 뱅커/플레이어 베팅은 '푸시(반환)' 처리
"""
from sh1_casino.cards import Deck

def baccarat_value(card) -> int:
    """바카라 카드 점수 계산 (A=1, 2~9=액면가, 10/J/Q/K=0)"""
    if card.rank == 14: # Ace
        return 1
    elif card.rank >= 10: # 10, J, Q, K
        return 0
    return card.rank

def hand_score(cards: list) -> int:
    """바카라 핸드 점수 (합의 일의 자리)"""
    return sum(baccarat_value(c) for c in cards) % 10

class BaccaratGame:
    def __init__(self, bet_amount: int, bet_target: str):
        self.bet_amount = bet_amount
        self.bet_target = bet_target # "player", "banker", "tie"
        self.deck = Deck()
        
        # 덱 셔플 및 기본 카드 2장씩 드로우
        self.player_cards = self.deck.draw(2)
        self.banker_cards = self.deck.draw(2)
        
        self.winner = None
        self.payout_amount = 0
        self.result = "" # "win", "lose", "push"

    def determine_third_cards(self):
        """서드 카드 룰에 따라 추가 카드를 뽑아야 하는지 결정하고 뽑은 카드를 반환"""
        p_score = hand_score(self.player_cards)
        b_score = hand_score(self.banker_cards)
        
        p_third = None
        b_third = None

        # 1. 내추럴 (Natural 8 or 9) -> 양쪽 모두 스탠드
        if p_score >= 8 or b_score >= 8:
            return p_third, b_third

        # 2. 플레이어의 서드 카드 룰
        if p_score <= 5:
            p_third = self.deck.draw(1)[0]
            self.player_cards.append(p_third)
            p_third_val = baccarat_value(p_third)
        else:
            p_third_val = None # 플레이어 스탠드

        # 3. 뱅커의 서드 카드 룰
        b_draws = False
        if p_third_val is None:
            # 플레이어가 스탠드한 경우: 뱅커는 5 이하일 때 뽑음
            if b_score <= 5:
                b_draws = True
        else:
            # 플레이어가 서드 카드를 뽑은 경우: 복잡한 뱅커 룰 적용
            if b_score <= 2:
                b_draws = True
            elif b_score == 3 and p_third_val != 8:
                b_draws = True
            elif b_score == 4 and p_third_val in (2, 3, 4, 5, 6, 7):
                b_draws = True
            elif b_score == 5 and p_third_val in (4, 5, 6, 7):
                b_draws = True
            elif b_score == 6 and p_third_val in (6, 7):
                b_draws = True
            # b_score == 7 이면 스탠드

        if b_draws:
            b_third = self.deck.draw(1)[0]
            self.banker_cards.append(b_third)

        return p_third, b_third

    def settle(self):
        """최종 승자를 가리고 배당금을 계산"""
        p_score = hand_score(self.player_cards)
        b_score = hand_score(self.banker_cards)

        if p_score > b_score:
            self.winner = "player"
        elif b_score > p_score:
            self.winner = "banker"
        else:
            self.winner = "tie"

        # 수익(순손익) 계산
        if self.winner == self.bet_target:
            self.result = "win"
            if self.bet_target == "player":
                self.payout_amount = self.bet_amount
            elif self.bet_target == "banker":
                self.payout_amount = int(self.bet_amount * 0.95) # 5% 커미션
            elif self.bet_target == "tie":
                self.payout_amount = self.bet_amount * 8 # 타이 8배당
        elif self.winner == "tie" and self.bet_target in ("player", "banker"):
            # 플레이어나 뱅커에 걸었는데 타이가 나오면 '푸시(베팅금 반환)'
            self.result = "push"
            self.payout_amount = 0
        else:
            self.result = "lose"
            self.payout_amount = -self.bet_amount
            
        return self.result, self.payout_amount

    def get_scores(self):
        return hand_score(self.player_cards), hand_score(self.banker_cards)