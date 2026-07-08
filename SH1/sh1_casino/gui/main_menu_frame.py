# -*- coding: utf-8 -*-
"""gui/main_menu_frame.py - 메인 화면 (칩/한도 조회, 메뉴 이동)"""
import tkinter as tk
from tkinter import simpledialog, messagebox

from sh1_casino import database as db
from sh1_casino.gui import styles


class MainMenuFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_DARK)
        self.app = app

        header = tk.Frame(self, bg=styles.BG_DARK)
        header.pack(fill="x", pady=(30, 10))
        tk.Label(header, text="♣ SH1 시흥랜드 ♣", font=styles.FONT_TITLE,
                  bg=styles.BG_DARK, fg=styles.GOLD).pack()

        self.welcome_label = tk.Label(self, text="", font=styles.FONT_H1,
                                       bg=styles.BG_DARK, fg=styles.WHITE)
        self.welcome_label.pack(pady=(10, 20))

        info_card = tk.Frame(self, bg=styles.BG_PANEL, padx=40, pady=24)
        info_card.pack(pady=10)

        self.chip_label = tk.Label(info_card, text="", font=styles.FONT_CHIP,
                                    bg=styles.BG_PANEL, fg=styles.GOLD_LIGHT)
        self.chip_label.grid(row=0, column=0, columnspan=2, pady=(0, 6))

        self.limit_label = tk.Label(info_card, text="", font=styles.FONT_BODY,
                                     bg=styles.BG_PANEL, fg=styles.WHITE)
        self.limit_label.grid(row=1, column=0, columnspan=2, pady=(0, 4))

        self.today_label = tk.Label(info_card, text="", font=styles.FONT_BODY,
                                     bg=styles.BG_PANEL, fg=styles.GRAY)
        self.today_label.grid(row=2, column=0, columnspan=2, pady=(0, 4))

        limit_btn = tk.Button(info_card, text="일일 베팅 한도 설정", command=self._set_limit)
        styles.style_button(limit_btn, bg=styles.BG_PANEL, fg=styles.GOLD_LIGHT,
                             hover=styles.BG_TABLE)
        limit_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        btn_frame = tk.Frame(self, bg=styles.BG_DARK)
        btn_frame.pack(pady=30)

        game_btn = tk.Button(btn_frame, text="🎰  게임하기", width=22,
                              command=lambda: self.app.show_frame("GameSelectFrame"))
        styles.style_button(game_btn)
        game_btn.grid(row=0, column=0, padx=10, pady=6)

        history_btn = tk.Button(btn_frame, text="📊  기록 조회", width=22,
                                 command=lambda: self.app.show_frame("HistoryFrame"))
        styles.style_button(history_btn)
        history_btn.grid(row=1, column=0, padx=10, pady=6)

        logout_btn = tk.Button(btn_frame, text="🚪  로그아웃", width=22,
                                command=self.app.logout)
        styles.style_button(logout_btn, bg="#7a2020", hover="#9c2b2b")
        logout_btn.grid(row=2, column=0, padx=10, pady=6)

        tk.Label(self, text="※ 본 프로그램은 교육 목적의 시뮬레이션이며 실제 현금 거래를 포함하지 않습니다.",
                  font=styles.FONT_SMALL, bg=styles.BG_DARK, fg=styles.GRAY).pack(side="bottom", pady=14)

    def on_show(self):
        user = self.app.refresh_user()
        if not user:
            return
        self.welcome_label.configure(text=f"{user['nickname']}님, 환영합니다!")
        self.chip_label.configure(text=f"보유 칩 : {user['chips']:,} 칩")
        self.limit_label.configure(text=f"일일 베팅 한도 : {user['daily_limit']:,} 칩")
        today_total = db.get_today_bet_total(user["username"])
        remaining = max(0, user["daily_limit"] - today_total)
        self.today_label.configure(
            text=f"오늘 사용한 베팅액 : {today_total:,} 칩  (남은 한도 : {remaining:,} 칩)")

    def _set_limit(self):
        user = self.app.current_user
        new_limit = simpledialog.askinteger(
            "일일 베팅 한도 설정",
            f"새로운 일일 베팅 한도를 입력하세요.\n(현재: {user['daily_limit']:,} 칩)",
            minvalue=0, maxvalue=100_000_000, parent=self,
        )
        if new_limit is not None:
            db.set_daily_limit(user["username"], new_limit)
            messagebox.showinfo("설정 완료", f"일일 베팅 한도가 {new_limit:,} 칩으로 설정되었습니다.")
            self.on_show()
