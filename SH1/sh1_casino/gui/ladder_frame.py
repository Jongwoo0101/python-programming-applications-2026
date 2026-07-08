# -*- coding: utf-8 -*-
"""gui/ladder_frame.py - 사다리타기(경마 컨셉) 플레이 화면"""
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
        self.selected_lane = tk.IntVar(value=-1)
        self.racing = False

        top = tk.Frame(self, bg=styles.BG_TABLE)
        top.pack(fill="x", pady=(14, 0), padx=20)
        tk.Label(top, text="🏇 사다리타기 (경마)", font=styles.FONT_H1, bg=styles.BG_TABLE,
                  fg=styles.GOLD).pack(side="left")
        self.chip_label = tk.Label(top, text="", font=styles.FONT_BODY_BOLD,
                                    bg=styles.BG_TABLE, fg=styles.GOLD_LIGHT)
        self.chip_label.pack(side="right")

        tk.Label(self, text="레인을 선택하세요 (배당이 높을수록 확률은 낮아집니다)",
                  font=styles.FONT_SMALL, bg=styles.BG_TABLE, fg=styles.GRAY).pack(pady=(16, 10))

        self.lane_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.lane_frame.pack()
        self.lane_widgets = []
        for i, lane in enumerate(ladder.LANES):
            col = tk.Frame(self.lane_frame, bg=styles.BG_PANEL, padx=16, pady=14,
                            highlightthickness=2, highlightbackground=styles.BG_PANEL)
            col.grid(row=0, column=i, padx=8)

            horse = tk.Label(col, text="🐎", font=("Helvetica", 28), bg=styles.BG_PANEL,
                              fg=lane["color"])
            horse.pack()
            tk.Label(col, text=lane["name"], font=styles.FONT_BODY_BOLD, bg=styles.BG_PANEL,
                      fg=styles.WHITE).pack()
            tk.Label(col, text=f"x{lane['multiplier']}", font=styles.FONT_H2, bg=styles.BG_PANEL,
                      fg=styles.GOLD_LIGHT).pack(pady=(2, 8))
            rb = tk.Radiobutton(col, text="선택", variable=self.selected_lane, value=i,
                                 bg=styles.BG_PANEL, fg=styles.WHITE, selectcolor=styles.BG_DARK,
                                 activebackground=styles.BG_PANEL, font=styles.FONT_SMALL,
                                 command=self._reset_highlight)
            rb.pack()
            self.lane_widgets.append(col)

        self.result_label = tk.Label(self, text="", font=styles.FONT_H1, bg=styles.BG_TABLE,
                                      fg=styles.GOLD_LIGHT)
        self.result_label.pack(pady=(20, 6))

        self.bet_frame = tk.Frame(self, bg=styles.BG_TABLE)
        self.bet_frame.pack(pady=6)
        tk.Label(self.bet_frame, text="베팅액:", font=styles.FONT_BODY, bg=styles.BG_TABLE,
                  fg=styles.WHITE).grid(row=0, column=0, padx=(0, 6))
        self.bet_entry = tk.Entry(self.bet_frame, font=styles.FONT_BODY, width=10,
                                   bg=styles.ENTRY_BG, fg=styles.WHITE,
                                   insertbackground=styles.WHITE, relief="flat")
        self.bet_entry.insert(0, "100")
        self.bet_entry.grid(row=0, column=1, ipady=4)
        self.race_btn = tk.Button(self.bet_frame, text="베팅 후 경주 시작", command=self._start_race)
        styles.style_button(self.race_btn)
        self.race_btn.grid(row=0, column=2, padx=(10, 0))

        back_btn = tk.Button(self, text="← 게임 선택으로", width=18,
                              command=lambda: self.app.show_frame("GameSelectFrame"))
        styles.style_button(back_btn, bg=styles.BG_PANEL, fg=styles.GOLD_LIGHT,
                             hover=styles.BG_DARK)
        back_btn.pack(pady=(20, 20))

    def _reset_highlight(self):
        for i, col in enumerate(self.lane_widgets):
            is_sel = (self.selected_lane.get() == i)
            col.configure(highlightbackground=styles.GOLD if is_sel else styles.BG_PANEL)

    def _refresh_chip_label(self):
        user = self.app.current_user
        self.chip_label.configure(text=f"보유 칩: {user['chips']:,}")

    def on_show(self):
        self.app.refresh_user()
        self._refresh_chip_label()
        self.result_label.configure(text="")
        self.selected_lane.set(-1)
        self._reset_highlight()
        self.race_btn.configure(state="normal")
        self.racing = False

    def _start_race(self):
        if self.racing:
            return
        lane_idx = self.selected_lane.get()
        if lane_idx < 0:
            messagebox.showwarning("레인 선택 필요", "베팅할 레인을 먼저 선택하세요.")
            return
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

        self.racing = True
        self.race_btn.configure(state="disabled")
        self.result_label.configure(text="경주가 진행 중입니다...", fg=styles.WHITE)

        # 약간의 긴장감을 위한 카운트다운 연출 후 결과 표시
        self._countdown(3, lane_idx, bet)

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
        new_chips = db.update_chips(username, net)
        csv_logger.log_game(username, GAME_TYPE, bet, "win" if won else "lose", net, new_chips)

        if won:
            self.result_label.configure(
                text=f"🎉 {winner_lane['name']} 말 우승! (x{winner_lane['multiplier']})  +{net:,}칩",
                fg=styles.GREEN_OK)
        else:
            self.result_label.configure(
                text=f"{winner_lane['name']} 말 우승 (x{winner_lane['multiplier']}) - 베팅 실패  {net:,}칩",
                fg=styles.RED)

        self.app.refresh_user()
        self._refresh_chip_label()
        self.race_btn.configure(state="normal")
        self.racing = False
