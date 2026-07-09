# -*- coding: utf-8 -*-
"""gui/quiz_frame.py - 학습 리커버리(퀴즈) 화면

[변경] 문제 목록을 DB 하드코딩 대신 data/quizzes.json 에서 읽어오는
       quiz_manager 를 사용하도록 변경했습니다. 문제를 추가하려면
       코드를 건드릴 필요 없이 그 JSON 파일만 편집하면 됩니다.
"""
import tkinter as tk
from tkinter import messagebox

from sh1_casino import database as db
from sh1_casino import quiz_manager
from sh1_casino.gui import styles


class QuizFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_DARK)
        self.app = app
        self.current_quiz = None

        tk.Label(self, text="📚 학습 리커버리 센터", font=styles.FONT_TITLE,
                 bg=styles.BG_DARK, fg=styles.GOLD).pack(pady=(40, 10))
        tk.Label(self, text="문제를 맞히고 게임 토큰을 획득하세요!", font=styles.FONT_SMALL,
                 bg=styles.BG_DARK, fg=styles.GRAY).pack(pady=(0, 20))

        self.card = styles.make_card(self, padx=40, pady=32)
        self.card.pack()

        self.category_label = tk.Label(self.card, text="", font=styles.FONT_SMALL,
                                        bg=styles.BG_PANEL, fg=styles.ACCENT_BLUE_LIGHT)
        self.category_label.pack()

        self.question_label = tk.Label(self.card, text="", font=styles.FONT_H2, bg=styles.BG_PANEL,
                                        fg=styles.WHITE, wraplength=420, justify="center")
        self.question_label.pack(pady=(6, 20))

        self.reward_label = tk.Label(self.card, text="", font=styles.FONT_BODY_BOLD,
                                      bg=styles.BG_PANEL, fg=styles.GREEN_OK)
        self.reward_label.pack(pady=(0, 20))

        self.answer_entry = styles.make_entry(self.card, width=28)
        self.answer_entry.pack(pady=(0, 14), ipady=4)
        self.answer_entry.bind("<Return>", lambda e: self._submit_answer())

        self.submit_btn = styles.make_button(self.card, "정답 제출", self._submit_answer,
                                              style="Primary.TButton", width=24)
        self.submit_btn.pack(pady=(6, 10))

        back_btn = styles.make_button(self, "← 메인으로",
                                       lambda: self.app.show_frame("MainMenuFrame"),
                                       style="Ghost.TButton", width=16)
        back_btn.pack(pady=40)

    def on_show(self):
        self.answer_entry.delete(0, tk.END)
        quiz_manager.reload()
        self._load_new_quiz()

    def _load_new_quiz(self):
        prev_id = self.current_quiz["id"] if self.current_quiz else None
        self.current_quiz = quiz_manager.get_random_quiz(exclude_id=prev_id)
        if self.current_quiz:
            self.category_label.configure(text=f"[{self.current_quiz.get('category', '일반')}]")
            self.question_label.configure(text=f"Q. {self.current_quiz['question']}")
            self.reward_label.configure(text=f"보상: {self.current_quiz['reward']} 토큰")
            self.submit_btn.configure(state="normal")
        else:
            self.category_label.configure(text="")
            self.question_label.configure(text="현재 등록된 퀴즈가 없습니다.\n(data/quizzes.json 확인)")
            self.reward_label.configure(text="")
            self.submit_btn.configure(state="disabled")

    def _submit_answer(self):
        if not self.current_quiz:
            return

        user_answer = self.answer_entry.get().strip()
        if quiz_manager.check_answer(self.current_quiz, user_answer):
            reward = self.current_quiz["reward"]
            db.update_tokens(self.app.current_user["username"], reward)
            messagebox.showinfo("정답!", f"정답입니다! {reward} 토큰이 지급되었습니다.")
            self.answer_entry.delete(0, tk.END)
            self._load_new_quiz()
            self.app.refresh_user()
        else:
            messagebox.showerror("오답", "틀렸습니다. 다시 도전해 보세요!")
            self.answer_entry.delete(0, tk.END)
