# -*- coding: utf-8 -*-
"""gui/history_frame.py - 결과 및 기록 조회 화면 (승률, 누적손익, 게임별 통계, 전체 로그)"""
import tkinter as tk
from tkinter import ttk

from sh1_casino import csv_logger
from sh1_casino.gui import styles


class HistoryFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_DARK)
        self.app = app

        tk.Label(self, text="📊 게임 이용 기록", font=styles.FONT_TITLE,
                  bg=styles.BG_DARK, fg=styles.GOLD).pack(pady=(24, 10))

        self.summary_frame = tk.Frame(self, bg=styles.BG_PANEL, padx=24, pady=16)
        self.summary_frame.pack(fill="x", padx=40, pady=(0, 12))

        self.stat_labels = {}
        stat_defs = [
            ("plays", "총 게임 수"), ("win_rate", "승률"),
            ("net_profit", "누적 손익"), ("total_bet", "총 베팅액"),
        ]
        for i, (key, label) in enumerate(stat_defs):
            box = tk.Frame(self.summary_frame, bg=styles.BG_PANEL)
            box.grid(row=0, column=i, padx=20)
            tk.Label(box, text=label, font=styles.FONT_SMALL, bg=styles.BG_PANEL,
                      fg=styles.GRAY).pack()
            val = tk.Label(box, text="-", font=styles.FONT_H2, bg=styles.BG_PANEL,
                            fg=styles.GOLD_LIGHT)
            val.pack()
            self.stat_labels[key] = val

        tk.Label(self, text="게임별 통계", font=styles.FONT_H2, bg=styles.BG_DARK,
                  fg=styles.WHITE).pack(anchor="w", padx=44, pady=(6, 4))

        self.by_game_frame = tk.Frame(self, bg=styles.BG_DARK)
        self.by_game_frame.pack(fill="x", padx=40)

        tk.Label(self, text="최근 게임 기록", font=styles.FONT_H2, bg=styles.BG_DARK,
                  fg=styles.WHITE).pack(anchor="w", padx=44, pady=(16, 4))

        table_wrap = tk.Frame(self, bg=styles.BG_DARK)
        table_wrap.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Casino.Treeview", background=styles.BG_PANEL, fieldbackground=styles.BG_PANEL,
                         foreground=styles.WHITE, rowheight=26, font=styles.FONT_SMALL)
        style.configure("Casino.Treeview.Heading", background=styles.BG_TABLE,
                         foreground=styles.GOLD_LIGHT, font=styles.FONT_BODY_BOLD)
        style.map("Casino.Treeview", background=[("selected", styles.BUTTON_HOVER)])

        columns = ("timestamp", "game_type", "bet_amount", "result", "chip_change", "chips_after")
        headers = {"timestamp": "일시", "game_type": "게임", "bet_amount": "베팅액",
                   "result": "결과", "chip_change": "칩 변동", "chips_after": "잔여 칩"}

        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings",
                                  style="Casino.Treeview", height=10)
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, anchor="center", width=140 if col == "timestamp" else 110)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        back_btn = tk.Button(self, text="← 메인으로", width=16,
                              command=lambda: self.app.show_frame("MainMenuFrame"))
        styles.style_button(back_btn, bg=styles.BG_PANEL, fg=styles.GOLD_LIGHT,
                             hover=styles.BG_TABLE)
        back_btn.pack(pady=16)

    def on_show(self):
        self.app.refresh_user()
        username = self.app.current_user["username"]
        stats = csv_logger.get_user_stats(username)
        overall = stats["overall"]

        self.stat_labels["plays"].configure(text=f"{overall['plays']:,}")
        self.stat_labels["win_rate"].configure(text=f"{overall['win_rate']}%")
        profit = overall["net_profit"]
        self.stat_labels["net_profit"].configure(
            text=f"{'+' if profit >= 0 else ''}{profit:,}",
            fg=styles.GREEN_OK if profit >= 0 else styles.RED)
        self.stat_labels["total_bet"].configure(text=f"{overall['total_bet']:,}")

        for w in self.by_game_frame.winfo_children():
            w.destroy()
        by_game = stats["by_game"]
        if not by_game:
            tk.Label(self.by_game_frame, text="아직 플레이한 게임이 없습니다.",
                      font=styles.FONT_SMALL, bg=styles.BG_DARK, fg=styles.GRAY).pack(anchor="w")
        else:
            for game_type, s in by_game.items():
                row = tk.Frame(self.by_game_frame, bg=styles.BG_PANEL, padx=14, pady=8)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=game_type, font=styles.FONT_BODY_BOLD, bg=styles.BG_PANEL,
                          fg=styles.GOLD_LIGHT, width=10, anchor="w").pack(side="left")
                tk.Label(row, text=f"{s['plays']}판", font=styles.FONT_BODY, bg=styles.BG_PANEL,
                          fg=styles.WHITE, width=8).pack(side="left")
                tk.Label(row, text=f"승률 {s['win_rate']}%", font=styles.FONT_BODY, bg=styles.BG_PANEL,
                          fg=styles.WHITE, width=12).pack(side="left")
                profit_g = s["net_profit"]
                tk.Label(row, text=f"손익 {'+' if profit_g >= 0 else ''}{profit_g:,}",
                          font=styles.FONT_BODY, bg=styles.BG_PANEL,
                          fg=styles.GREEN_OK if profit_g >= 0 else styles.RED, width=16
                          ).pack(side="left")

        for item in self.tree.get_children():
            self.tree.delete(item)
        result_kr = {"win": "승", "lose": "패", "push": "무승부"}
        for log in csv_logger.get_user_logs(username):
            change = int(log["chip_change"])
            self.tree.insert("", "end", values=(
                log["timestamp"], log["game_type"], f"{int(log['bet_amount']):,}",
                result_kr.get(log["result"], log["result"]),
                f"{'+' if change >= 0 else ''}{change:,}",
                f"{int(log['chips_after']):,}",
            ))
