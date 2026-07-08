# -*- coding: utf-8 -*-
"""gui/poker_frame.py - 포커(헤즈업 홀덤) 플레이 화면"""
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
        self.chip_label = tk.Label(top, text="", font=styles.FONT_BODY_BOLD,
                                    bg=styles.BG_TABLE, fg=styles.GOLD_LIGHT)
        self.chip_label.pack(side="right")

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

        self.message_label = tk.Label(self, text="베팅액을 입력하고 게임을 시작하세요.",
                                       font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE, fg=styles.WHITE)
        self.message_label.pack(pady=6)

        self.player_cards_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.player_cards_frame.pack(pady=4)
        tk.Label(self, text="플레이어 (나)", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE,
                  fg=styles.WHITE).pack(pady=(2, 10))

        self.bet_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.bet_frame.pack(pady=4)
        tk.Label(self.bet_frame, text="베팅 단위:", font=styles.FONT_BODY, bg=styles.BG_TABLE,
                  fg=styles.WHITE).grid(row=0, column=0, padx=(0, 6))
        self.bet_entry = tk.Entry(self.bet_frame, font=styles.FONT_BODY, width=10,
                                   bg=styles.ENTRY_BG, fg=styles.WHITE,
                                   insertbackground=styles.WHITE, relief="flat")
        self.bet_entry.insert(0, "50")
        self.bet_entry.grid(row=0, column=1, ipady=4)
        self.start_btn = tk.Button(self.bet_frame, text="핸드 시작", command=self._start_hand)
        styles.style_button(self.start_btn)
        self.start_btn.grid(row=0, column=2, padx=(10, 0))

        self.action_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.action_frame.pack(pady=10)
        self.check_btn = tk.Button(self.action_frame, text="체크", command=self._check, width=10)
        self.bet_btn = tk.Button(self.action_frame, text="베팅", command=self._bet, width=10)
        self.call_btn = tk.Button(self.action_frame, text="콜", command=self._call, width=10)
        self.fold_btn = tk.Button(self.action_frame, text="폴드", command=self._fold, width=10)
        for b in (self.check_btn, self.bet_btn, self.call_btn, self.fold_btn):
            styles.style_button(b)

        back_btn = tk.Button(self, text="← 게임 선택으로", width=18,
                              command=lambda: self.app.show_frame("GameSelectFrame"))
        styles.style_button(back_btn, bg=styles.BG_PANEL, fg=styles.GOLD_LIGHT,
                             hover=styles.BG_DARK)
        back_btn.pack(pady=(10, 20))

        self._set_action_buttons(mode="none")

    # ---------------------------------------------------------- 표시 헬퍼
    def _render_card(self, parent, card, hidden=False):
        if hidden:
            tk.Label(parent, text="🂠", font=("Helvetica", 26), bg=styles.CARD_BG,
                      fg=styles.GRAY, width=2, relief="raised", bd=2).pack(side="left", padx=4)
            return
        color = styles.card_color(card)
        tk.Label(parent, text=f"{card.name}\n{card.suit}", font=styles.FONT_CARD,
                  bg=styles.CARD_BG, fg=color, width=3, relief="raised", bd=2,
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
        self.pot_label.configure(text=f"팟: {g.pot:,} 칩")
        self.message_label.configure(text=g.message)

    def _set_action_buttons(self, mode: str):
        """mode: 'none' | 'act' (체크/베팅/폴드) | 'facing' (콜/폴드)"""
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

    def _refresh_chip_label(self):
        user = self.app.current_user
        self.chip_label.configure(text=f"보유 칩: {user['chips']:,}")

    def on_show(self):
        self.app.refresh_user()
        self._refresh_chip_label()
        self.message_label.configure(text="베팅액을 입력하고 게임을 시작하세요.")
        self.street_label.configure(text="")
        self.pot_label.configure(text="")
        self._clear_frame(self.ai_cards_frame)
        self._clear_frame(self.board_frame)
        self._clear_frame(self.player_cards_frame)
        self._set_action_buttons("none")
        self.game = None

    # ---------------------------------------------------------- 게임 진행
    def _start_hand(self):
        try:
            bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("오류", "베팅 단위는 숫자로 입력해주세요.")
            return

        username = self.app.current_user["username"]
        # 최대 위험 금액(모든 스트리트에서 베팅될 경우) = bet_unit * 5 정도로 넉넉히 체크
        allowed, reason = db.check_bet_allowed(username, bet)
        if not allowed:
            messagebox.showwarning("베팅 불가", reason)
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

    def _check(self):
        self.game.player_check()
        self._after_action()

    def _bet(self):
        self.game.player_bet()
        self._after_action()

    def _call(self):
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
        new_chips = db.update_chips(username, payout)
        csv_logger.log_game(username, GAME_TYPE, self.game.player_total,
                             self.game.csv_result(), payout, new_chips)

        self.app.refresh_user()
        self._refresh_chip_label()
        sign = "+" if payout >= 0 else ""
        self.message_label.configure(text=f"{self.game.message}  ({sign}{payout:,}칩)")
