# -*- coding: utf-8 -*-
"""gui/blackjack_frame.py - 블랙잭 플레이 화면"""
import tkinter as tk
from tkinter import messagebox

from sh1_casino import database as db
from sh1_casino import csv_logger
from sh1_casino.games.blackjack import BlackjackGame
from sh1_casino.gui import styles

GAME_TYPE = "블랙잭"


class BlackjackFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_TABLE)
        self.app = app
        self.game = None

        top = tk.Frame(self, bg=styles.BG_TABLE)
        top.pack(fill="x", pady=(14, 0), padx=20)
        tk.Label(top, text="🂡 블랙잭", font=styles.FONT_H1, bg=styles.BG_TABLE,
                 fg=styles.GOLD).pack(side="left")
        self.token_label = tk.Label(top, text="", font=styles.FONT_BODY_BOLD,
                                     bg=styles.BG_TABLE, fg=styles.GOLD_LIGHT)
        self.token_label.pack(side="right")

        tk.Label(self, text="AI 상대", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE,
                 fg=styles.WHITE).pack(pady=(20, 2))
        self.dealer_cards_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.dealer_cards_frame.pack(pady=4)
        self.dealer_value_label = tk.Label(self, text="", font=styles.FONT_BODY,
                                            bg=styles.BG_TABLE, fg=styles.GRAY)
        self.dealer_value_label.pack()

        self.message_label = tk.Label(self, text="참여 토큰을 입력하고 게임을 시작하세요.",
                                       font=styles.FONT_H2, bg=styles.BG_TABLE, fg=styles.GOLD_LIGHT)
        self.message_label.pack(pady=16)

        self.player_cards_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.player_cards_frame.pack(pady=4)
        self.player_value_label = tk.Label(self, text="", font=styles.FONT_BODY,
                                            bg=styles.BG_TABLE, fg=styles.WHITE)
        self.player_value_label.pack()
        tk.Label(self, text="나 (학습자)", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE,
                 fg=styles.WHITE).pack(pady=(2, 10))

        self.bet_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.bet_frame.pack(pady=6)
        tk.Label(self.bet_frame, text="참여 토큰:", font=styles.FONT_BODY, bg=styles.BG_TABLE,
                 fg=styles.WHITE).grid(row=0, column=0, padx=(0, 6))
        self.bet_entry = styles.make_entry(self.bet_frame, width=10)
        self.bet_entry.insert(0, "100")
        self.bet_entry.grid(row=0, column=1, ipady=3)
        self.deal_btn = styles.make_button(self.bet_frame, "게임 시작", self._start_round,
                                            style="Primary.TButton")
        self.deal_btn.grid(row=0, column=2, padx=(10, 0))

        self.action_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.action_frame.pack(pady=10)
        self.hit_btn = styles.make_button(self.action_frame, "히트 (Hit)", self._hit,
                                           style="Accent.TButton", width=12)
        self.stand_btn = styles.make_button(self.action_frame, "스탠드 (Stand)", self._stand,
                                             style="Success.TButton", width=12)
        self.double_btn = styles.make_button(self.action_frame, "더블다운", self._double,
                                              style="Purple.TButton", width=12)
        for i, b in enumerate((self.hit_btn, self.stand_btn, self.double_btn)):
            b.grid(row=0, column=i, padx=6)

        back_btn = styles.make_button(self, "← 게임 선택으로",
                                       lambda: self.app.show_frame("GameSelectFrame"),
                                       style="Ghost.TButton", width=18)
        back_btn.pack(pady=(10, 20))

        self._set_action_state(False)

    def _render_card(self, parent, card, hidden=False):
        if hidden:
            tk.Label(parent, text="🂠", font=("Helvetica", 30), bg=styles.CARD_BACK,
                     fg=styles.GRAY, width=2, relief="flat", bd=0,
                     highlightbackground=styles.BORDER, highlightthickness=1
                     ).pack(side="left", padx=4)
            return
        color = styles.card_color(card)
        tk.Label(parent, text=f"{card.name}\n{card.suit}", font=styles.FONT_CARD,
                 bg=styles.CARD_FACE, fg=color, width=3, relief="flat", bd=0,
                 highlightbackground=styles.BORDER, highlightthickness=1,
                 justify="center").pack(side="left", padx=4)

    def _render_hands(self, reveal_dealer: bool):
        for w in self.dealer_cards_frame.winfo_children():
            w.destroy()
        for w in self.player_cards_frame.winfo_children():
            w.destroy()

        for i, card in enumerate(self.game.dealer):
            hidden = (i == 1 and not reveal_dealer)
            self._render_card(self.dealer_cards_frame, card, hidden)
        for card in self.game.player:
            self._render_card(self.player_cards_frame, card)

        dv, _ = self.game.dealer_value()
        pv, _ = self.game.player_value()
        self.dealer_value_label.configure(text="" if not reveal_dealer else f"합계: {dv}")
        self.player_value_label.configure(text=f"합계: {pv}")

    def _set_action_state(self, playing: bool):
        state = "normal" if playing else "disabled"
        self.hit_btn.configure(state=state)
        self.stand_btn.configure(state=state)
        self.double_btn.configure(state=state)
        self.bet_entry.configure(state="disabled" if playing else "normal")
        self.deal_btn.configure(state="disabled" if playing else "normal")

    def _refresh_token_label(self):
        user = self.app.current_user
        self.token_label.configure(text=f"보유 토큰: {user['tokens']:,}")

    def on_show(self):
        self.app.refresh_user()
        self._refresh_token_label()
        self.message_label.configure(text="참여 토큰을 입력하고 게임을 시작하세요.")
        for w in self.dealer_cards_frame.winfo_children():
            w.destroy()
        for w in self.player_cards_frame.winfo_children():
            w.destroy()
        self.dealer_value_label.configure(text="")
        self.player_value_label.configure(text="")
        self._set_action_state(False)
        self.game = None

    def _start_round(self):
        try:
            bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("오류", "토큰은 숫자로 입력해주세요.")
            return

        username = self.app.current_user["username"]
        allowed, reason = db.check_bet_allowed(username, bet)
        if not allowed:
            messagebox.showwarning("참여 불가", reason)
            return

        self.game = BlackjackGame(bet)
        self._set_action_state(True)
        self.double_btn.configure(
            state="normal" if bet <= self.app.current_user["tokens"] - bet else "disabled")

        if self.game.check_initial_blackjack():
            self._render_hands(reveal_dealer=True)
            self._finish_round()
        else:
            self._render_hands(reveal_dealer=False)
            self.message_label.configure(text="히트 또는 스탠드를 선택하세요.")

    def _hit(self):
        self.game.player_hit()
        self._render_hands(reveal_dealer=self.game.finished)
        self.double_btn.configure(state="disabled")
        if self.game.finished:
            self._finish_round()

    def _stand(self):
        self.game.player_stand()
        self._render_hands(reveal_dealer=True)
        self._finish_round()

    def _double(self):
        username = self.app.current_user["username"]
        allowed, reason = db.check_bet_allowed(username, self.game.bet)
        if not allowed:
            messagebox.showwarning("더블다운 불가", reason)
            return
        self.game.player_double()
        self._render_hands(reveal_dealer=self.game.finished)
        self._finish_round()

    def _finish_round(self):
        self._set_action_state(False)
        self.message_label.configure(text=self.game.result_label())

        payout = self.game.payout()
        username = self.app.current_user["username"]

        db.add_today_bet(username, self.game.bet)
        new_tokens = db.update_tokens(username, payout)

        csv_logger.log_game(username, GAME_TYPE, self.game.bet, self.game.csv_result(),
                             payout, new_tokens)

        self.app.refresh_user()
        self._refresh_token_label()
