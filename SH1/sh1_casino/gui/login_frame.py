# -*- coding: utf-8 -*-
"""gui/login_frame.py - 로그인 화면"""
import tkinter as tk
from sh1_casino import database as db
from sh1_casino.gui import styles


class LoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_DARK)
        self.app = app

        wrapper = tk.Frame(self, bg=styles.BG_DARK)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="💡 시흥랜드에 오신걸 환영합니다 💡", font=styles.FONT_TITLE,
                 bg=styles.BG_DARK, fg=styles.GOLD).pack(pady=(0, 6))
        tk.Label(wrapper, text="게이미피케이션 기반 학습 플랫폼", font=styles.FONT_BODY,
                 bg=styles.BG_DARK, fg=styles.GRAY).pack(pady=(0, 24))

        card = styles.make_card(wrapper)
        card.pack()

        tk.Label(card, text="아이디", font=styles.FONT_BODY_BOLD, bg=styles.BG_PANEL,
                 fg=styles.WHITE, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.username_entry = styles.make_entry(card, width=28)
        self.username_entry.grid(row=1, column=0, pady=(0, 14), ipady=4)

        tk.Label(card, text="비밀번호", font=styles.FONT_BODY_BOLD, bg=styles.BG_PANEL,
                 fg=styles.WHITE, anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.password_entry = styles.make_entry(card, width=28, show="●")
        self.password_entry.grid(row=3, column=0, pady=(0, 8), ipady=4)
        self.password_entry.bind("<Return>", lambda e: self._login())

        self.error_label = tk.Label(card, text="", font=styles.FONT_BODY_BOLD,
                                     bg=styles.BG_PANEL, fg=styles.RED)
        self.error_label.grid(row=4, column=0, sticky="w", pady=(0, 8))

        login_btn = styles.make_button(card, "로그인", self._login,
                                        style="Primary.TButton", width=24)
        login_btn.grid(row=5, column=0, pady=(6, 10))

        signup_btn = styles.make_button(card, "회원가입", self._go_signup,
                                         style="Ghost.TButton", width=24)
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
