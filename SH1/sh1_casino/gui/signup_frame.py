# -*- coding: utf-8 -*-
"""gui/signup_frame.py - 회원가입 화면"""
import tkinter as tk
from sh1_casino import database as db
from sh1_casino.gui import styles


class SignupFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_DARK)
        self.app = app

        wrapper = tk.Frame(self, bg=styles.BG_DARK)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrapper, text="회원가입", font=styles.FONT_TITLE,
                 bg=styles.BG_DARK, fg=styles.GOLD).pack(pady=(0, 20))

        card = styles.make_card(wrapper)
        card.pack()

        self.entries = {}
        fields = [
            ("username", "아이디", False),
            ("password", "비밀번호 (4자 이상)", True),
            ("password2", "비밀번호 확인", True),
            ("nickname", "닉네임", False),
        ]
        for i, (key, label, is_pw) in enumerate(fields):
            tk.Label(card, text=label, font=styles.FONT_BODY_BOLD, bg=styles.BG_PANEL,
                     fg=styles.WHITE, anchor="w").grid(row=i * 2, column=0, sticky="w", pady=(0, 4))
            entry = styles.make_entry(card, width=30, show="●" if is_pw else None)
            entry.grid(row=i * 2 + 1, column=0, pady=(0, 12), ipady=4)
            self.entries[key] = entry

        self.msg_label = tk.Label(card, text="", font=styles.FONT_BODY_BOLD, bg=styles.BG_PANEL,
                                   fg=styles.RED, wraplength=280, justify="left")
        self.msg_label.grid(row=len(fields) * 2, column=0, sticky="w", pady=(0, 8))

        signup_btn = styles.make_button(card, "가입하기", self._signup,
                                         style="Primary.TButton", width=26)
        signup_btn.grid(row=len(fields) * 2 + 1, column=0, pady=(6, 10))

        back_btn = styles.make_button(card, "로그인 화면으로", self._go_login,
                                       style="Ghost.TButton", width=26)
        back_btn.grid(row=len(fields) * 2 + 2, column=0)

        tk.Label(card, text="* 기본 지급 토큰 10,000 / 기본 일일 한도 100,000",
                 font=styles.FONT_SMALL, bg=styles.BG_PANEL, fg=styles.GRAY
                 ).grid(row=len(fields) * 2 + 3, column=0, pady=(10, 0))

    def on_show(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.msg_label.configure(text="", fg=styles.RED)

    def _signup(self):
        username = self.entries["username"].get()
        password = self.entries["password"].get()
        password2 = self.entries["password2"].get()
        nickname = self.entries["nickname"].get()

        if password != password2:
            self.msg_label.configure(text="비밀번호가 서로 일치하지 않습니다.", fg=styles.RED)
            return
        try:
            db.create_user(username, password, nickname)
            self.msg_label.configure(text="가입 완료! 로그인해주세요.", fg=styles.GREEN_OK)
            self.after(900, self._go_login)
        except db.AuthError as e:
            self.msg_label.configure(text=str(e), fg=styles.RED)

    def _go_login(self):
        self.app.show_frame("LoginFrame")
