# -*- coding: utf-8 -*-
"""
gui/app.py
SH1(시흥랜드) 메인 애플리케이션 - 프레임 전환을 관리하는 컨트롤러
"""
import tkinter as tk

from sh1_casino import database as db
from sh1_casino.gui import styles


class SH1App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SH1 - 시흥랜드")
        self.geometry("1040x720")
        self.minsize(960, 660)
        self.configure(bg=styles.BG_DARK)

        db.init_db()
        self.current_user = None  # 로그인한 사용자 정보 dict (username, nickname, chips, daily_limit ...)

        # 컨테이너: 모든 화면(Frame)을 겹쳐 놓고 필요한 것만 raise
        self.container = tk.Frame(self, bg=styles.BG_DARK)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self._register_frames()
        self.show_frame("LoginFrame")

    def _register_frames(self):
        # 순환 import 방지를 위해 함수 내부에서 import
        from sh1_casino.gui.login_frame import LoginFrame
        from sh1_casino.gui.signup_frame import SignupFrame
        from sh1_casino.gui.main_menu_frame import MainMenuFrame
        from sh1_casino.gui.game_select_frame import GameSelectFrame
        from sh1_casino.gui.blackjack_frame import BlackjackFrame
        from sh1_casino.gui.poker_frame import PokerFrame
        from sh1_casino.gui.ladder_frame import LadderFrame
        from sh1_casino.gui.history_frame import HistoryFrame

        for F in (LoginFrame, SignupFrame, MainMenuFrame, GameSelectFrame,
                  BlackjackFrame, PokerFrame, LadderFrame, HistoryFrame):
            frame = F(parent=self.container, app=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, name: str):
        frame = self.frames[name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    # ---------------------------------------------------------- 세션 관리
    def set_user(self, user_dict):
        self.current_user = user_dict

    def refresh_user(self):
        """DB에서 최신 칩/한도 정보를 다시 읽어온다."""
        if self.current_user:
            fresh = db.get_user(self.current_user["username"])
            if fresh:
                self.current_user = fresh
        return self.current_user

    def logout(self):
        self.current_user = None
        self.show_frame("LoginFrame")
