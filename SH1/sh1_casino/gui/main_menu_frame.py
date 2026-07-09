# -*- coding: utf-8 -*-
"""gui/main_menu_frame.py - 메인 화면 (토큰 조회, 메뉴 이동)"""
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
        tk.Label(header, text="💡 시흥랜드", font=styles.FONT_TITLE,
                 bg=styles.BG_DARK, fg=styles.GOLD).pack()

        self.welcome_label = tk.Label(self, text="", font=styles.FONT_H1,
                                       bg=styles.BG_DARK, fg=styles.WHITE)
        self.welcome_label.pack(pady=(10, 20))

        info_card = styles.make_card(self, padx=40, pady=24)
        info_card.pack(pady=10)

        self.token_label = tk.Label(info_card, text="", font=styles.FONT_TOKEN,
                                     bg=styles.BG_PANEL, fg=styles.GOLD_LIGHT)
        self.token_label.grid(row=0, column=0, columnspan=2, pady=(0, 6))

        self.limit_label = tk.Label(info_card, text="", font=styles.FONT_BODY,
                                     bg=styles.BG_PANEL, fg=styles.WHITE)
        self.limit_label.grid(row=1, column=0, columnspan=2, pady=(0, 4))

        limit_btn = styles.make_button(info_card, "일일 사용 한도 설정", self._set_limit,
                                        style="Ghost.TButton")
        limit_btn.grid(row=2, column=0, columnspan=2, pady=(12, 0))

        btn_frame = tk.Frame(self, bg=styles.BG_DARK)
        btn_frame.pack(pady=30)

        game_btn = styles.make_button(
            btn_frame, "🎮 미니게임 (토큰 획득)",
            lambda: self.app.show_frame("GameSelectFrame"), "Primary.TButton", 22)
        quiz_btn = styles.make_button(
            btn_frame, "📚 퀴즈 풀기 (리커버리)",
            lambda: self.app.show_frame("QuizFrame"), "Accent.TButton", 22)
        store_btn = styles.make_button(
            btn_frame, "🛒 교재 해금 (상점)",
            lambda: self.app.show_frame("StoreFrame"), "Purple.TButton", 22)
        history_btn = styles.make_button(
            btn_frame, "📊 통계 및 기록",
            lambda: self.app.show_frame("HistoryFrame"), "Success.TButton", 22)
        logout_btn = styles.make_button(
            btn_frame, "🚪 로그아웃", self.app.logout, "Danger.TButton", 48)

        game_btn.grid(row=0, column=0, padx=10, pady=6)
        quiz_btn.grid(row=0, column=1, padx=10, pady=6)
        store_btn.grid(row=1, column=0, padx=10, pady=6)
        history_btn.grid(row=1, column=1, padx=10, pady=6)
        logout_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=(14, 6))

    def on_show(self):
        user = self.app.refresh_user()
        if not user:
            return
        self.welcome_label.configure(text=f"{user['nickname']}님, 환영합니다!")
        self.token_label.configure(text=f"보유 토큰 : {user['tokens']:,} 🪙")
        self.limit_label.configure(text=f"일일 사용 한도 : {user['daily_limit']:,} 토큰")

    def _set_limit(self):
        user = self.app.current_user
        new_limit = simpledialog.askinteger(
            "한도 설정", f"새로운 일일 한도를 입력하세요.\n(현재: {user['daily_limit']:,})",
            minvalue=0, maxvalue=100_000_000, parent=self)
        if new_limit is not None:
            db.set_daily_limit(user["username"], new_limit)
            messagebox.showinfo("설정 완료", f"일일 한도가 {new_limit:,} 토큰으로 설정되었습니다.")
            self.on_show()
