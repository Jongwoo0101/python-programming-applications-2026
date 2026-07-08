# -*- coding: utf-8 -*-
"""gui/login_frame.py - 로그인 화면"""
import tkinter as tk
from tkinter import messagebox

from sh1_casino import database as db
from sh1_casino.gui import styles


class LoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_DARK)
        self.app = app

        wrapper = tk.Frame(self, bg=styles.BG_DARK)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="♠ SH1 시흥랜드 ♠", font=styles.FONT_TITLE,
                  bg=styles.BG_DARK, fg=styles.GOLD).pack(pady=(0, 6))
        tk.Label(wrapper, text="교육용 카지노 시뮬레이션", font=styles.FONT_SMALL,
                  bg=styles.BG_DARK, fg=styles.GRAY).pack(pady=(0, 24))

        card = tk.Frame(wrapper, bg=styles.BG_PANEL, padx=40, pady=32)
        card.pack()

        tk.Label(card, text="아이디", font=styles.FONT_BODY, bg=styles.BG_PANEL,
                  fg=styles.WHITE, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.username_entry = tk.Entry(card, font=styles.FONT_BODY, width=28,
                                        bg=styles.ENTRY_BG, fg=styles.WHITE,
                                        insertbackground=styles.WHITE, relief="flat")
        self.username_entry.grid(row=1, column=0, pady=(0, 14), ipady=6)

        tk.Label(card, text="비밀번호", font=styles.FONT_BODY, bg=styles.BG_PANEL,
                  fg=styles.WHITE, anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.password_entry = tk.Entry(card, font=styles.FONT_BODY, width=28, show="●",
                                        bg=styles.ENTRY_BG, fg=styles.WHITE,
                                        insertbackground=styles.WHITE, relief="flat")
        self.password_entry.grid(row=3, column=0, pady=(0, 8), ipady=6)
        self.password_entry.bind("<Return>", lambda e: self._login())

        self.error_label = tk.Label(card, text="", font=styles.FONT_SMALL,
                                     bg=styles.BG_PANEL, fg=styles.RED)
        self.error_label.grid(row=4, column=0, sticky="w", pady=(0, 8))

        login_btn = tk.Button(card, text="로그인", command=self._login, width=24)
        styles.style_button(login_btn)
        login_btn.grid(row=5, column=0, pady=(6, 10))

        signup_btn = tk.Button(card, text="회원가입", command=self._go_signup, width=24,
                                bg=styles.BG_PANEL, fg=styles.GOLD_LIGHT, relief="flat",
                                bd=0, font=styles.FONT_SMALL, cursor="hand2",
                                activebackground=styles.BG_PANEL, activeforeground=styles.GOLD)
        signup_btn.grid(row=6, column=0)

    def on_show(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.error_label.configure(text="")
        self.username_entry.focus_set()

    def _login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            user = db.authenticate(username, password)
            self.app.set_user(user)
            self.app.show_frame("MainMenuFrame")
        except db.AuthError as e:
            self.error_label.configure(text=str(e))

    def _go_signup(self):
        self.app.show_frame("SignupFrame")
