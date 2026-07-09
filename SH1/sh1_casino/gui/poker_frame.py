# -*- coding: utf-8 -*-
"""gui/poker_frame.py - 포커 플레이 화면"""
import tkinter as tk
from tkinter import messagebox

from sh1_casino import database as db
from sh1_casino import csv_logger
from sh1_casino.games.poker import HeadsUpPoker
from sh1_casino.gui import styles

GAME_TYPE = "포커"

STREET_LABELS = {
    "preflop": "프리플랍", "flop": "플랍", "turn": "턴",
    "river": "리버", "showdown": "쇼다운",
}


class PokerFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_TABLE)
        self.app = app
        self.game = None

        top = tk.Frame(self, bg=styles.BG_TABLE)
        top.pack(fill="x", pady=(14, 0), padx=20)
        tk.Label(top, text="♣ 포커 (헤즈업 홀덤)", font=styles.FONT_H1, bg=styles.BG_TABLE,
                 fg=styles.GOLD).pack(side="left")
        self.token_label = tk.Label(top, text="", font=styles.FONT_BODY_BOLD,
                                     bg=styles.BG_TABLE, fg=styles.GOLD_LIGHT)
        self.token_label.pack(side="right")

        self.street_label = tk.Label(self, text="", font=styles.FONT_BODY_BOLD,
                                      bg=styles.BG_TABLE, fg=styles.WHITE)
        self.street_label.pack(pady=(16, 2))

        tk.Label(self, text="AI", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE,
                 fg=styles.WHITE).pack()
        self.ai_cards_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.ai_cards_frame.pack(pady=4)

        tk.Label(self, text="커뮤니티 카드", font=styles.FONT_SMALL, bg=styles.BG_TABLE,
                 fg=styles.GRAY).pack(pady=(14, 2))
        self.board_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.board_frame.pack(pady=4)

        self.pot_label = tk.Label(self, text="", font=styles.FONT_H2, bg=styles.BG_TABLE,
                                   fg=styles.GOLD_LIGHT)
        self.pot_label.pack(pady=(10, 6))

        self.message_label = tk.Label(self, text="참여 토큰 단위를 입력하고 게임을 시작하세요.",
                                       font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE, fg=styles.WHITE)
        self.message_label.pack(pady=6)

        self.player_cards_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.player_cards_frame.pack(pady=4)
        tk.Label(self, text="나 (학습자)", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE,
                 fg=styles.WHITE).pack(pady=(2, 10))

        self.bet_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.bet_frame.pack(pady=4)
        tk.Label(self.bet_frame, text="토큰 단위:", font=styles.FONT_BODY, bg=styles.BG_TABLE,
                 fg=styles.WHITE).grid(row=0, column=0, padx=(0, 6))
        self.bet_entry = styles.make_entry(self.bet_frame, width=10)
        self.bet_entry.insert(0, "50")
        self.bet_entry.grid(row=0, column=1, ipady=3)
        self.start_btn = styles.make_button(self.bet_frame, "핸드 시작", self._start_hand,
                                             style="Primary.TButton")
        self.start_btn.grid(row=0, column=2, padx=(10, 0))

        self.action_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.action_frame.pack(pady=10)
        self.check_btn = styles.make_button(self.action_frame, "체크", self._check,
                                             style="Accent.TButton", width=10)
        self.bet_btn = styles.make_button(self.action_frame, "베팅", self._bet,
                                           style="Success.TButton", width=10)
        self.call_btn = styles.make_button(self.action_frame, "콜", self._call,
                                            style="Success.TButton", width=10)
        self.fold_btn = styles.make_button(self.action_frame, "폴드", self._fold,
                                            style="Danger.TButton", width=10)

        back_btn = styles.make_button(self, "← 게임 선택으로",
                                       lambda: self.app.show_frame("GameSelectFrame"),
                                       style="Ghost.TButton", width=18)
        back_btn.pack(pady=(10, 20))

        self._set_action_buttons(mode="none")

    def _render_card(self, parent, card, hidden=False):
        if hidden:
            tk.Label(parent, text="🂠", font=("Helvetica", 26), bg=styles.CARD_BACK,
                     fg=styles.GRAY, width=2, relief="flat", bd=0,
                     highlightbackground=styles.BORDER, highlightthickness=1
                     ).pack(side="left", padx=4)
            return
        color = styles.card_color(card)
        tk.Label(parent, text=f"{card.name}\n{card.suit}", font=styles.FONT_CARD,
                 bg=styles.CARD_FACE, fg=color, width=3, relief="flat", bd=0,
                 highlightbackground=styles.BORDER, highlightthickness=1,
                 justify="center").pack(side="left", padx=4)

    def _clear_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _render_table(self):
        g = self.game
        reveal_ai = g.finished
        self._clear_frame(self.ai_cards_frame)
        self._clear_frame(self.board_frame)
        self._clear_frame(self.player_cards_frame)

        for card in g.hole_ai:
            self._render_card(self.ai_cards_frame, card, hidden=not reveal_ai)
        for card in g.board:
            self._render_card(self.board_frame, card)
        for _ in range(5 - len(g.board)):
            tk.Label(self.board_frame, text="", font=styles.FONT_CARD, bg=styles.BG_TABLE,
                     width=3).pack(side="left", padx=4)
        for card in g.hole_player:
            self._render_card(self.player_cards_frame, card)

        self.street_label.configure(text=STREET_LABELS.get(g.street, ""))
        self.pot_label.configure(text=f"팟: {g.pot:,} 토큰")
        self.message_label.configure(text=g.message)

    def _set_action_buttons(self, mode: str):
        for b in (self.check_btn, self.bet_btn, self.call_btn, self.fold_btn):
            b.grid_forget()
        if mode == "act":
            self.check_btn.grid(row=0, column=0, padx=6)
            self.bet_btn.grid(row=0, column=1, padx=6)
            self.fold_btn.grid(row=0, column=2, padx=6)
        elif mode == "facing":
            self.call_btn.grid(row=0, column=0, padx=6)
            self.fold_btn.grid(row=0, column=1, padx=6)
        self.bet_entry.configure(state="disabled" if mode != "none" else "normal")
        self.start_btn.configure(state="disabled" if mode != "none" else "normal")

    def _refresh_token_label(self):
        user = self.app.current_user
        self.token_label.configure(text=f"보유 토큰: {user['tokens']:,}")

    def on_show(self):
        self.app.refresh_user()
        self._refresh_token_label()
        self.message_label.configure(text="참여 토큰 단위를 입력하고 게임을 시작하세요.")
        self.street_label.configure(text="")
        self.pot_label.configure(text="")
        self._clear_frame(self.ai_cards_frame)
        self._clear_frame(self.board_frame)
        self._clear_frame(self.player_cards_frame)
        self._set_action_buttons("none")
        self.game = None

    def _start_hand(self):
        try:
            bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("오류", "참여 단위는 숫자로 입력해주세요.")
            return

        username = self.app.current_user["username"]
        allowed, reason = db.check_bet_allowed(username, bet)
        if not allowed:
            messagebox.showwarning("참여 불가", reason)
            return

        self.game = HeadsUpPoker(bet)
        self._render_table()
        self._set_action_buttons("act")

    def _after_action(self):
        self._render_table()
        if self.game.finished:
            self._finish_hand()
        elif self.game.facing_bet:
            self._set_action_buttons("facing")
        else:
            self._set_action_buttons("act")

    def _has_enough_for(self, extra_amount: int) -> bool:
        """[버그 수정] 매 스트리트 베팅/콜 전에 실제 잔여 토큰을 재검증한다.
        기존 버전은 핸드 시작 시점의 ante 금액만 확인하고 이후 라운드는
        검증 없이 계속 베팅이 가능해, 이론상 보유 토큰보다 더 많이 걸 수 있었다."""
        user = self.app.current_user
        remaining = user["tokens"] - self.game.player_total
        return remaining >= extra_amount

    def _check(self):
        self.game.player_check()
        self._after_action()

    def _bet(self):
        if not self._has_enough_for(self.game.bet_unit):
            messagebox.showwarning("토큰 부족", "남은 토큰이 부족하여 베팅할 수 없습니다. 폴드 처리됩니다.")
            self._fold()
            return
        self.game.player_bet()
        self._after_action()

    def _call(self):
        if not self._has_enough_for(self.game.bet_unit):
            messagebox.showwarning("토큰 부족", "남은 토큰이 부족하여 콜할 수 없습니다. 폴드 처리됩니다.")
            self._fold()
            return
        self.game.player_call()
        self._after_action()

    def _fold(self):
        self.game.player_fold()
        self._after_action()

    def _finish_hand(self):
        self._set_action_buttons("none")
        payout = self.game.payout()
        username = self.app.current_user["username"]

        db.add_today_bet(username, self.game.player_total)
        new_tokens = db.update_tokens(username, payout)
        csv_logger.log_game(username, GAME_TYPE, self.game.player_total,
                             self.game.csv_result(), payout, new_tokens)

        self.app.refresh_user()
        self._refresh_token_label()
        sign = "+" if payout >= 0 else ""
        self.message_label.configure(text=f"{self.game.message}  ({sign}{payout:,} 토큰)")
