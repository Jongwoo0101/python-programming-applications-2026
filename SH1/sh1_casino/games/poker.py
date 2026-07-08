# -*- coding: utf-8 -*-
"""
games/poker.py
규칙 기반 AI(Rule-Based AI) 와의 1:1(헤즈업) 텍사스 홀덤 포커 (고정 베팅 방식)

- 매 핸드 시작 시 플레이어와 AI가 각각 bet_unit 만큼 앤티(ante)를 낸다.
- 각 스트리트(프리플랍/플랍/턴/리버)마다 플레이어가 먼저 행동한다.
    * 체크 -> AI가 체크/베팅 결정
    * 베팅 -> AI가 콜/폴드 결정
    * (AI가 베팅한 경우) 플레이어는 콜 또는 폴드로 대응
- 리버 이후 쇼다운으로 7장(홀 2 + 보드 5) 중 최고의 5장 조합으로 승자를 가린다.
- AI는 핸드 강도(hand_strength)를 0~1 사이 점수로 계산하는 규칙 기반으로 행동한다.
"""
from itertools import combinations
from collections import Counter

from sh1_casino.cards import Deck


# ================================================================ 핸드 평가
def evaluate_5(cards):
    """5장의 카드를 받아 비교 가능한 튜플(카테고리, 타이브레이커...)을 반환.
    카테고리 : 8=스트레이트플러시 7=포카드 6=풀하우스 5=플러시 4=스트레이트
               3=트리플 2=투페어 1=원페어 0=하이카드
    """
    ranks = sorted([c.rank for c in cards], reverse=True)
    suits = [c.suit for c in cards]
    is_flush = len(set(suits)) == 1

    unique_ranks = sorted(set(ranks), reverse=True)
    straight_high = None
    if len(unique_ranks) == 5:
        if unique_ranks[0] - unique_ranks[4] == 4:
            straight_high = unique_ranks[0]
        elif unique_ranks == [14, 5, 4, 3, 2]:  # A-2-3-4-5 (휠)
            straight_high = 5

    counts = Counter(ranks)
    count_groups = sorted(counts.items(), key=lambda x: (-x[1], -x[0]))
    pattern = [c for _, c in count_groups]
    rank_order = [r for r, _ in count_groups]

    if straight_high and is_flush:
        return (8, straight_high)
    if pattern[0] == 4:
        return (7, rank_order[0], rank_order[1])
    if pattern[0] == 3 and pattern[1] == 2:
        return (6, rank_order[0], rank_order[1])
    if is_flush:
        return (5, tuple(ranks))
    if straight_high:
        return (4, straight_high)
    if pattern[0] == 3:
        return (3, rank_order[0], tuple(rank_order[1:3]))
    if pattern[0] == 2 and pattern[1] == 2:
        hi, lo = sorted([rank_order[0], rank_order[1]], reverse=True)
        return (2, hi, lo, rank_order[2])
    if pattern[0] == 2:
        return (1, rank_order[0], tuple(rank_order[1:4]))
    return (0, tuple(ranks))


def best_of_7(cards7):
    """7장(또는 그 이상) 중 최고의 5장 조합 평가값을 반환"""
    return max(evaluate_5(list(combo)) for combo in combinations(cards7, 5))


HAND_NAMES = {
    8: "스트레이트 플러시", 7: "포카드", 6: "풀하우스", 5: "플러시",
    4: "스트레이트", 3: "트리플", 2: "투페어", 1: "원페어", 0: "하이카드",
}


def hand_name(rank_tuple) -> str:
    return HAND_NAMES.get(rank_tuple[0], "")


# ================================================================ AI 로직
def hand_strength(hole, board):
    """0~1 사이의 핸드 강도 점수 (규칙 기반 휴리스틱)"""
    if not board:
        r1, r2 = sorted([hole[0].rank, hole[1].rank], reverse=True)
        suited = hole[0].suit == hole[1].suit
        pair = r1 == r2
        score = (r1 + r2) / 28.0
        if pair:
            score += 0.30
        if suited:
            score += 0.05
        if not pair and abs(r1 - r2) == 1:
            score += 0.05
        return min(score, 1.0)
    else:
        category = best_of_7(hole + board)[0]
        return min(category / 8.0 + 0.05, 1.0)


def ai_decide(facing_bet: bool, hole, board) -> str:
    """facing_bet=False -> 'check' 또는 'bet' 반환
       facing_bet=True  -> 'call' 또는 'fold' 반환"""
    strength = hand_strength(hole, board)
    if not facing_bet:
        return "bet" if strength >= 0.60 else "check"
    return "call" if strength >= 0.35 else "fold"


# ================================================================ 게임 진행
class HeadsUpPoker:
    STREET_ORDER = ["preflop", "flop", "turn", "river", "showdown"]

    def __init__(self, bet_unit: int):
        self.bet_unit = bet_unit
        self.deck = Deck()
        self.hole_player = self.deck.draw(2)
        self.hole_ai = self.deck.draw(2)
        self.board = []
        self.street = "preflop"
        self.pot = bet_unit * 2  # 양쪽 앤티
        self.player_total = bet_unit  # 이번 핸드에서 플레이어가 낸 총 칩
        self.ai_total = bet_unit
        self.facing_bet = False  # True면 플레이어가 AI의 베팅에 콜/폴드 해야 함
        self.finished = False
        self.folded_by = None     # 'player' / 'ai' / None
        self.winner = None        # 'player' / 'ai' / 'split'
        self.message = "당신의 차례입니다. 체크 또는 베팅하세요."

    # ---------------------------------------------------------- 플레이어 행동
    def player_check(self):
        if self.facing_bet or self.finished:
            return
        action = ai_decide(False, self.hole_ai, self.board)
        if action == "check":
            self.message = "AI가 체크했습니다."
            self._advance_street()
        else:
            self.pot += self.bet_unit
            self.ai_total += self.bet_unit
            self.facing_bet = True
            self.message = f"AI가 {self.bet_unit}칩을 베팅했습니다. 콜 또는 폴드하세요."

    def player_bet(self):
        if self.facing_bet or self.finished:
            return
        self.pot += self.bet_unit
        self.player_total += self.bet_unit
        action = ai_decide(True, self.hole_ai, self.board)
        if action == "call":
            self.pot += self.bet_unit
            self.ai_total += self.bet_unit
            self.message = "AI가 콜했습니다."
            self._advance_street()
        else:
            self.folded_by = "ai"
            self.message = "AI가 폴드했습니다! 팟을 획득합니다."
            self._settle()

    def player_call(self):
        if not self.facing_bet or self.finished:
            return
        self.pot += self.bet_unit
        self.player_total += self.bet_unit
        self.facing_bet = False
        self.message = "콜 했습니다."
        self._advance_street()

    def player_fold(self):
        if self.finished:
            return
        self.folded_by = "player"
        self.message = "폴드했습니다. AI가 팟을 획득합니다."
        self._settle()

    # ---------------------------------------------------------- 진행/정산
    def _advance_street(self):
        self.facing_bet = False
        idx = self.STREET_ORDER.index(self.street)
        if self.street == "preflop":
            self.board += self.deck.draw(3)
        elif self.street in ("flop", "turn"):
            self.board += self.deck.draw(1)
        elif self.street == "river":
            self.street = "showdown"
            self._settle()
            return
        self.street = self.STREET_ORDER[idx + 1]
        if self.street != "showdown":
            self.message = "당신의 차례입니다. 체크 또는 베팅하세요."

    def _settle(self):
        self.finished = True
        if self.folded_by == "player":
            self.winner = "ai"
        elif self.folded_by == "ai":
            self.winner = "player"
        else:
            self.street = "showdown"
            p_rank = best_of_7(self.hole_player + self.board)
            a_rank = best_of_7(self.hole_ai + self.board)
            if p_rank > a_rank:
                self.winner = "player"
                self.message = f"당신의 승리! ({hand_name(p_rank)})"
            elif a_rank > p_rank:
                self.winner = "ai"
                self.message = f"AI의 승리... ({hand_name(a_rank)})"
            else:
                self.winner = "split"
                self.message = f"무승부! ({hand_name(p_rank)})"

    def payout(self) -> int:
        """플레이어 기준 순 칩 증감량 (베팅한 총액 대비 손익)"""
        if self.winner == "player":
            return self.pot - self.player_total
        if self.winner == "ai":
            return -self.player_total
        # split
        return (self.pot // 2) - self.player_total

    def csv_result(self) -> str:
        if self.winner == "player":
            return "win"
        if self.winner == "split":
            return "push"
        return "lose"
