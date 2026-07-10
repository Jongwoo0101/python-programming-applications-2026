# -*- coding: utf-8 -*-
"""gui/game_select_frame.py - 미니게임 선택 화면"""
import tkinter as tk
from sh1_casino.gui import styles


class GameSelectFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_DARK)
        self.app = app

        tk.Label(self, text="미니게임 (토큰 획득)", font=styles.FONT_TITLE,
                 bg=styles.BG_DARK, fg=styles.GOLD).pack(pady=(40, 30))

        cards_frame = tk.Frame(self, bg=styles.BG_DARK)
        cards_frame.pack(pady=10)

        games = [
            ("🂡", "블랙잭", "AI와의 1:1 대결\n21에 가장 가깝게!", "BlackjackFrame"),
            ("♣", "포커 (홀덤)", "규칙 기반 AI와의 포커\n최고의 5장 조합으로 승부", "PokerFrame"),
            ("🂤", "바카라", "플레이어 vs 뱅커\n어느 쪽이 9에 가까울까?", "BaccaratFrame"),
            ("🏇", "사다리타기", "경마 컨셉의 확률 게임\n레인을 골라 배당을 노려라", "LadderFrame"),
        ]

        for i, (icon, title, desc, frame_name) in enumerate(games):
            card = styles.make_card(cards_frame, padx=26, pady=22)
            card.grid(row=i // 2, column=i % 2, padx=14, pady=10)

            tk.Label(card, text=icon, font=("Helvetica", 34), bg=styles.BG_PANEL,
                     fg=styles.GOLD_LIGHT).pack(pady=(0, 6))
            tk.Label(card, text=title, font=styles.FONT_H2, bg=styles.BG_PANEL,
                     fg=styles.WHITE).pack(pady=(0, 6))
            tk.Label(card, text=desc, font=styles.FONT_SMALL, bg=styles.BG_PANEL,
                     fg=styles.GRAY, justify="center").pack(pady=(0, 14))

            btn = styles.make_button(card, "플레이",
                                      lambda f=frame_name: self.app.show_frame(f),
                                      style="Primary.TButton", width=14)
            btn.pack()

        back_btn = styles.make_button(self, "← 메인으로",
                                       lambda: self.app.show_frame("MainMenuFrame"),
                                       style="Ghost.TButton", width=16)
        back_btn.pack(pady=40)

    def on_show(self):
        pass
