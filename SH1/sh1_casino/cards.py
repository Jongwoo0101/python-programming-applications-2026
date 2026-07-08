# -*- coding: utf-8 -*-
"""
cards.py
포커 / 블랙잭에서 공통으로 사용하는 카드, 덱 클래스
"""
import random

SUITS = ["♠", "♥", "♦", "♣"]
RANK_NAMES = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8",
              9: "9", 10: "10", 11: "J", 12: "Q", 13: "K", 14: "A"}


class Card:
    """rank: 2~14 (11=J, 12=Q, 13=K, 14=A), suit: ♠♥♦♣"""

    __slots__ = ("rank", "suit")

    def __init__(self, rank: int, suit: str):
        self.rank = rank
        self.suit = suit

    @property
    def name(self) -> str:
        return RANK_NAMES[self.rank]

    def __repr__(self) -> str:
        return f"{self.name}{self.suit}"

    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))


class Deck:
    """표준 52장 카드 덱"""

    def __init__(self):
        self._cards = [Card(r, s) for s in SUITS for r in range(2, 15)]
        random.shuffle(self._cards)

    def shuffle(self):
        random.shuffle(self._cards)

    def draw(self, n: int = 1):
        """n장을 뽑아 리스트로 반환 (n=1이면 리스트 길이 1)"""
        drawn = self._cards[:n]
        self._cards = self._cards[n:]
        return drawn

    def remaining(self) -> int:
        return len(self._cards)
