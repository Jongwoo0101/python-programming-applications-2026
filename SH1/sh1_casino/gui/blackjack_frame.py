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
        self.chip_label = tk.Label(top, text="", font=styles.FONT_BODY_BOLD,
                                    bg=styles.BG_TABLE, fg=styles.GOLD_LIGHT)
        self.chip_label.pack(side="right")

        # 딜러 영역
        tk.Label(self, text="딜러", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE,
                  fg=styles.WHITE).pack(pady=(20, 2))
        self.dealer_cards_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.dealer_cards_frame.pack(pady=4)
        self.dealer_value_label = tk.Label(self, text="", font=styles.FONT_BODY,
                                            bg=styles.BG_TABLE, fg=styles.GRAY)
        self.dealer_value_label.pack()

        # 결과 메시지
        self.message_label = tk.Label(self, text="베팅액을 입력하고 게임을 시작하세요.",
                                       font=styles.FONT_H2, bg=styles.BG_TABLE, fg=styles.GOLD_LIGHT)
        self.message_label.pack(pady=16)

        # 플레이어 영역
        self.player_cards_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.player_cards_frame.pack(pady=4)
        self.player_value_label = tk.Label(self, text="", font=styles.FONT_BODY,
                                            bg=styles.BG_TABLE, fg=styles.WHITE)
        self.player_value_label.pack()
        tk.Label(self, text="플레이어 (나)", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE,
                  fg=styles.WHITE).pack(pady=(2, 10))

        # 베팅 영역
        self.bet_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.bet_frame.pack(pady=6)
        tk.Label(self.bet_frame, text="베팅액:", font=styles.FONT_BODY, bg=styles.BG_TABLE,
                  fg=styles.WHITE).grid(row=0, column=0, padx=(0, 6))
        self.bet_entry = tk.Entry(self.bet_frame, font=styles.FONT_BODY, width=10,
                                   bg=styles.ENTRY_BG, fg=styles.WHITE,
                                   insertbackground=styles.WHITE, relief="flat")
        self.bet_entry.insert(0, "100")
        self.bet_entry.grid(row=0, column=1, ipady=4)
        self.deal_btn = tk.Button(self.bet_frame, text="게임 시작", command=self._start_round)
        styles.style_button(self.deal_btn)
        self.deal_btn.grid(row=0, column=2, padx=(10, 0))

        # 액션 버튼 (히트/스탠드/더블/새게임)
        self.action_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.action_frame.pack(pady=10)
        self.hit_btn = tk.Button(self.action_frame, text="히트 (Hit)", command=self._hit, width=12)
        self.stand_btn = tk.Button(self.action_frame, text="스탠드 (Stand)", command=self._stand, width=12)
        self.double_btn = tk.Button(self.action_frame, text="더블다운", command=self._double, width=12)
        for i, b in enumerate((self.hit_btn, self.stand_btn, self.double_btn)):
            styles.style_button(b)
            b.grid(row=0, column=i, padx=6)

        back_btn = tk.Button(self, text="← 게임 선택으로", width=18,
                              command=lambda: self.app.show_frame("GameSelectFrame"))
        styles.style_button(back_btn, bg=styles.BG_PANEL, fg=styles.GOLD_LIGHT,
                             hover=styles.BG_DARK)
        back_btn.pack(pady=(10, 20))

        self._set_action_state(False)

    # ---------------------------------------------------------- 표시 헬퍼
    def _render_card(self, parent, card, hidden=False):
        if hidden:
            tk.Label(parent, text="🂠", font=("Helvetica", 30), bg=styles.CARD_BG,
                      fg=styles.GRAY, width=2, relief="raised", bd=2).pack(side="left", padx=4)
            return
        color = styles.card_color(card)
        tk.Label(parent, text=f"{card.name}\n{card.suit}", font=styles.FONT_CARD,
                  bg=styles.CARD_BG, fg=color, width=3, relief="raised", bd=2,
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

    def _refresh_chip_label(self):
        user = self.app.current_user
        self.chip_label.configure(text=f"보유 칩: {user['chips']:,}")

    def on_show(self):
        self.app.refresh_user()
        self._refresh_chip_label()
        self.message_label.configure(text="베팅액을 입력하고 게임을 시작하세요.")
        for w in self.dealer_cards_frame.winfo_children():
            w.destroy()
        for w in self.player_cards_frame.winfo_children():
            w.destroy()
        self.dealer_value_label.configure(text="")
        self.player_value_label.configure(text="")
        self._set_action_state(False)
        self.game = None

    # ---------------------------------------------------------- 게임 진행
    def _start_round(self):
        try:
            bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("오류", "베팅액은 숫자로 입력해주세요.")
            return

        username = self.app.current_user["username"]
        allowed, reason = db.check_bet_allowed(username, bet)
        if not allowed:
            messagebox.showwarning("베팅 불가", reason)
            return

        self.game = BlackjackGame(bet)
        self._set_action_state(True)
        self.double_btn.configure(state="normal" if bet <= self.app.current_user["chips"] - bet else "disabled")

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

        # 이번 라운드에 실제로 베팅한 총액(더블다운 반영)을 일일 한도에 반영
        db.add_today_bet(username, self.game.bet)

        new_chips = db.update_chips(username, payout)
        csv_logger.log_game(username, GAME_TYPE, self.game.bet, self.game.csv_result(),
                             payout, new_chips)

        self.app.refresh_user()
        self._refresh_chip_label()
