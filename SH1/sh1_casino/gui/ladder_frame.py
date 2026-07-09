# -*- coding: utf-8 -*-
"""gui/ladder_frame.py - 사다리타기 플레이 화면

[변경] 기존 tk.Radiobutton은 macOS(Aqua)에서 선택색(selectcolor)이 무시되어
       거의 안 보였습니다. 라디오버튼 대신 카드 전체를 클릭하면 선택되는
       방식으로 바꾸고, 선택된 카드는 금색 테두리로 강조합니다.
"""
import tkinter as tk
from tkinter import messagebox

from sh1_casino import database as db
from sh1_casino import csv_logger
from sh1_casino.games import ladder
from sh1_casino.gui import styles

GAME_TYPE = "사다리타기"


class LadderFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_TABLE)
        self.app = app
        self.selected_lane = -1
        self.racing = False

        top = tk.Frame(self, bg=styles.BG_TABLE)
        top.pack(fill="x", pady=(14, 0), padx=20)
        tk.Label(top, text="🏇 사다리타기", font=styles.FONT_H1, bg=styles.BG_TABLE,
                 fg=styles.GOLD).pack(side="left")
        self.token_label = tk.Label(top, text="", font=styles.FONT_BODY_BOLD,
                                     bg=styles.BG_TABLE, fg=styles.GOLD_LIGHT)
        self.token_label.pack(side="right")

        tk.Label(self, text="레인을 클릭해서 선택하세요 (배당이 높을수록 확률은 낮아집니다)",
                 font=styles.FONT_SMALL, bg=styles.BG_TABLE, fg=styles.GRAY).pack(pady=(16, 10))

        self.lane_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.lane_frame.pack()
        self.lane_widgets = []
        for i, lane in enumerate(ladder.LANES):
            col = tk.Frame(self.lane_frame, bg=styles.BG_PANEL, padx=16, pady=14,
                            highlightthickness=2, highlightbackground=styles.BORDER,
                            cursor="hand2")
            col.grid(row=0, column=i, padx=8)

            horse = tk.Label(col, text="🐎", font=("Helvetica", 28), bg=styles.BG_PANEL,
                              fg=lane["color"], cursor="hand2")
            horse.pack()
            name_lbl = tk.Label(col, text=lane["name"], font=styles.FONT_BODY_BOLD,
                                 bg=styles.BG_PANEL, fg=styles.WHITE, cursor="hand2")
            name_lbl.pack()
            mult_lbl = tk.Label(col, text=f"x{lane['multiplier']}", font=styles.FONT_H2,
                                 bg=styles.BG_PANEL, fg=styles.GOLD_LIGHT, cursor="hand2")
            mult_lbl.pack(pady=(2, 8))
            check_lbl = tk.Label(col, text="선택되지 않음", font=styles.FONT_SMALL,
                                  bg=styles.BG_PANEL, fg=styles.GRAY, cursor="hand2")
            check_lbl.pack()

            for widget in (col, horse, name_lbl, mult_lbl, check_lbl):
                widget.bind("<Button-1>", lambda e, idx=i: self._select_lane(idx))

            self.lane_widgets.append({"frame": col, "check_label": check_lbl})

        self.result_label = tk.Label(self, text="", font=styles.FONT_H1, bg=styles.BG_TABLE,
                                      fg=styles.GOLD_LIGHT)
        self.result_label.pack(pady=(20, 6))

        self.bet_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.bet_frame.pack(pady=6)
        tk.Label(self.bet_frame, text="참여 토큰:", font=styles.FONT_BODY, bg=styles.BG_TABLE,
                 fg=styles.WHITE).grid(row=0, column=0, padx=(0, 6))
        self.bet_entry = styles.make_entry(self.bet_frame, width=10)
        self.bet_entry.insert(0, "100")
        self.bet_entry.grid(row=0, column=1, ipady=3)
        self.race_btn = styles.make_button(self.bet_frame, "참여 후 시작", self._start_race,
                                            style="Primary.TButton")
        self.race_btn.grid(row=0, column=2, padx=(10, 0))

        back_btn = styles.make_button(self, "← 게임 선택으로",
                                       lambda: self.app.show_frame("GameSelectFrame"),
                                       style="Ghost.TButton", width=18)
        back_btn.pack(pady=(20, 20))

    def _select_lane(self, idx):
        if self.racing:
            return
        self.selected_lane = idx
        self._refresh_lane_highlight()

    def _refresh_lane_highlight(self):
        for i, widgets in enumerate(self.lane_widgets):
            is_sel = (self.selected_lane == i)
            widgets["frame"].configure(
                highlightbackground=styles.GOLD if is_sel else styles.BORDER)
            widgets["check_label"].configure(
                text="✅ 선택됨" if is_sel else "선택되지 않음",
                fg=styles.GOLD_LIGHT if is_sel else styles.GRAY)

    def _refresh_token_label(self):
        user = self.app.current_user
        self.token_label.configure(text=f"보유 토큰: {user['tokens']:,}")

    def on_show(self):
        self.app.refresh_user()
        self._refresh_token_label()
        self.result_label.configure(text="")
        self.selected_lane = -1
        self._refresh_lane_highlight()
        self.race_btn.configure(state="normal")
        self.racing = False

    def _start_race(self):
        if self.racing:
            return
        if self.selected_lane < 0:
            messagebox.showwarning("레인 선택 필요", "참여할 레인을 먼저 클릭해서 선택하세요.")
            return
        try:
            bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("오류", "토큰액은 숫자로 입력해주세요.")
            return

        username = self.app.current_user["username"]
        allowed, reason = db.check_bet_allowed(username, bet)
        if not allowed:
            messagebox.showwarning("참여 불가", reason)
            return

        self.racing = True
        self.race_btn.configure(state="disabled")
        self.result_label.configure(text="경주가 진행 중입니다...", fg=styles.WHITE)

        self._countdown(3, self.selected_lane, bet)

    def _countdown(self, n, lane_idx, bet):
        if n > 0:
            self.result_label.configure(text=f"경주 시작까지... {n}")
            self.after(400, lambda: self._countdown(n - 1, lane_idx, bet))
        else:
            self._resolve_race(lane_idx, bet)

    def _resolve_race(self, lane_idx, bet):
        won, winner_idx, net = ladder.play(lane_idx, bet)
        winner_lane = ladder.LANES[winner_idx]
        username = self.app.current_user["username"]

        db.add_today_bet(username, bet)
        new_tokens = db.update_tokens(username, net)
        csv_logger.log_game(username, GAME_TYPE, bet, "win" if won else "lose", net, new_tokens)

        if won:
            self.result_label.configure(
                text=f"🎉 {winner_lane['name']} 우승! (x{winner_lane['multiplier']})  +{net:,} 토큰",
                fg=styles.GREEN_OK)
        else:
            self.result_label.configure(
                text=f"{winner_lane['name']} 우승 (x{winner_lane['multiplier']}) - 베팅 실패  {net:,} 토큰",
                fg=styles.RED)

        self.app.refresh_user()
        self._refresh_token_label()
        self.race_btn.configure(state="normal")
        self.racing = False
