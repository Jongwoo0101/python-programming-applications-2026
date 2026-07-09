# -*- coding: utf-8 -*-
"""gui/store_frame.py - 온라인 교재 해금 화면

[변경] 교재 목록을 코드에 하드코딩하지 않고 data/textbooks.json 에서
       읽어오는 textbook_manager 를 사용하도록 변경했습니다.
"""
import tkinter as tk
from tkinter import messagebox

from sh1_casino import database as db
from sh1_casino import textbook_manager
from sh1_casino.gui import styles


class StoreFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_DARK)
        self.app = app

        top = tk.Frame(self, bg=styles.BG_DARK)
        top.pack(fill="x", pady=(40, 20), padx=40)
        tk.Label(top, text="🛒 교재 해금 상점", font=styles.FONT_TITLE,
                 bg=styles.BG_DARK, fg=styles.GOLD).pack(side="left")
        self.token_label = tk.Label(top, text="", font=styles.FONT_BODY_BOLD,
                                     bg=styles.BG_DARK, fg=styles.GOLD_LIGHT)
        self.token_label.pack(side="right")

        self.books_frame = tk.Frame(self, bg=styles.BG_DARK)
        self.books_frame.pack(pady=10)

        back_btn = styles.make_button(self, "← 메인으로",
                                       lambda: self.app.show_frame("MainMenuFrame"),
                                       style="Ghost.TButton", width=16)
        back_btn.pack(pady=30)

    def on_show(self):
        self.app.refresh_user()
        user = self.app.current_user
        self.token_label.configure(text=f"보유 토큰: {user['tokens']:,}")
        textbook_manager.reload()
        self._render_books()

    def _render_books(self):
        for w in self.books_frame.winfo_children():
            w.destroy()

        username = self.app.current_user["username"]
        unlocked = db.get_unlocked_books(username)
        books = textbook_manager.get_all_books()

        if not books:
            tk.Label(self.books_frame, text="등록된 교재가 없습니다. (data/textbooks.json 확인)",
                     font=styles.FONT_SMALL, bg=styles.BG_DARK, fg=styles.GRAY).pack()
            return

        for i, book in enumerate(books):
            is_unlocked = book["id"] in unlocked

            card = styles.make_card(self.books_frame, padx=20, pady=20,
                                     border=styles.GOLD if is_unlocked else styles.BORDER)
            card.grid(row=i // 4, column=i % 4, padx=14, pady=10)

            tk.Label(card, text="📖" if is_unlocked else "🔒", font=("Helvetica", 34),
                     bg=styles.BG_PANEL,
                     fg=styles.GOLD_LIGHT if is_unlocked else styles.GRAY).pack(pady=(0, 6))
            tk.Label(card, text=book["title"], font=styles.FONT_H2, bg=styles.BG_PANEL,
                     fg=styles.WHITE).pack(pady=(0, 6))
            tk.Label(card, text=book["desc"], font=styles.FONT_SMALL, bg=styles.BG_PANEL,
                     fg=styles.GRAY, justify="center", wraplength=150).pack(pady=(0, 14))

            if is_unlocked:
                tk.Label(card, text="해금 완료", font=styles.FONT_BODY_BOLD, bg=styles.BG_PANEL,
                         fg=styles.GREEN_OK).pack()
            else:
                btn = styles.make_button(
                    card, f"{book['cost']:,} 토큰에 해금",
                    lambda b=book: self._unlock(b), style="Primary.TButton", width=18)
                btn.pack()

    def _unlock(self, book):
        username = self.app.current_user["username"]
        success = db.unlock_book(username, book["id"], book["cost"])
        if success:
            messagebox.showinfo("해금 성공", f"'{book['title']}' 교재가 해금되었습니다!")
            self.on_show()
        else:
            messagebox.showwarning("토큰 부족", "토큰이 부족합니다. 게임을 하거나 퀴즈를 풀어 토큰을 모으세요.")
