# -*- coding: utf-8 -*-
"""gui/baccarat_frame.py - 바카라 플레이 화면"""
import tkinter as tk
from tkinter import messagebox

from sh1_casino import database as db
from sh1_casino import csv_logger
from sh1_casino.games.baccarat import BaccaratGame
from sh1_casino.gui import styles

GAME_TYPE = "바카라"

class BaccaratFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=styles.BG_TABLE)
        self.app = app
        self.game = None
        self.is_dealing = False
        
        # 게임 승패 기록(Bead Plate)을 저장할 리스트
        self.history = []

        # --- 상단 헤더 ---
        top = tk.Frame(self, bg=styles.BG_TABLE)
        top.pack(fill="x", pady=(14, 0), padx=20)
        tk.Label(top, text="🂤 바카라", font=styles.FONT_H1, bg=styles.BG_TABLE, fg=styles.GOLD).pack(side="left")
        self.token_label = tk.Label(top, text="", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE, fg=styles.GOLD_LIGHT)
        self.token_label.pack(side="right")

        # --- 메시지 라벨 ---
        self.message_label = tk.Label(self, text="베팅할 대상을 선택하고 토큰을 입력하세요.", 
                                      font=styles.FONT_H2, bg=styles.BG_TABLE, fg=styles.WHITE)
        self.message_label.pack(pady=(16, 8))

        # --- 카드 테이블 구역 ---
        table_frame = tk.Frame(self, bg=styles.BG_TABLE)
        table_frame.pack(pady=4)

        # 플레이어 구역 (좌측)
        p_zone = tk.Frame(table_frame, bg=styles.BG_TABLE)
        p_zone.grid(row=0, column=0, padx=40)
        tk.Label(p_zone, text="PLAYER", font=styles.FONT_H2, bg=styles.BG_TABLE, fg=styles.ACCENT_BLUE).pack()
        self.p_score_lbl = tk.Label(p_zone, text="점수: 0", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE, fg=styles.WHITE)
        self.p_score_lbl.pack(pady=4)
        self.p_cards_frame = tk.Frame(p_zone, bg=styles.BG_TABLE, height=120)
        self.p_cards_frame.pack()

        # 뱅커 구역 (우측)
        b_zone = tk.Frame(table_frame, bg=styles.BG_TABLE)
        b_zone.grid(row=0, column=1, padx=40)
        tk.Label(b_zone, text="BANKER", font=styles.FONT_H2, bg=styles.BG_TABLE, fg=styles.ACCENT_RED).pack()
        self.b_score_lbl = tk.Label(b_zone, text="점수: 0", font=styles.FONT_BODY_BOLD, bg=styles.BG_TABLE, fg=styles.WHITE)
        self.b_score_lbl.pack(pady=4)
        self.b_cards_frame = tk.Frame(b_zone, bg=styles.BG_TABLE, height=120)
        self.b_cards_frame.pack()

        # --- 베팅 구역 ---
        bet_container = styles.make_card(self, padx=20, pady=16)
        bet_container.pack(pady=10)

        tk.Label(bet_container, text="참여 토큰:", font=styles.FONT_BODY, bg=styles.BG_PANEL, fg=styles.WHITE).grid(row=0, column=0, padx=6)
        self.bet_entry = styles.make_entry(bet_container, width=14)
        self.bet_entry.insert(0, "100")
        self.bet_entry.grid(row=0, column=1, padx=6, ipady=3)

        btns_frame = tk.Frame(bet_container, bg=styles.BG_PANEL)
        btns_frame.grid(row=1, column=0, columnspan=2, pady=(14, 0))

        self.btn_player = styles.make_button(btns_frame, "플레이어 승 (1배)", lambda: self._start_round("player"), "Accent.TButton")
        self.btn_tie = styles.make_button(btns_frame, "무승부/타이 (8배)", lambda: self._start_round("tie"), "Success.TButton")
        self.btn_banker = styles.make_button(btns_frame, "뱅커 승 (0.95배)", lambda: self._start_round("banker"), "Danger.TButton")

        self.btn_player.grid(row=0, column=0, padx=6)
        self.btn_tie.grid(row=0, column=1, padx=6)
        self.btn_banker.grid(row=0, column=2, padx=6)

        # --- 전광판 (스코어보드) 구역 ---
        board_frame = tk.Frame(self, bg=styles.BG_TABLE)
        board_frame.pack(pady=10)
        tk.Label(board_frame, text="📊 게임 승패 기록 (Bead Plate)", font=styles.FONT_SMALL, bg=styles.BG_TABLE, fg=styles.GRAY).pack(anchor="w", padx=2, pady=(0,4))
        
        # 6줄 x 16칸 세팅
        self.rows = 6
        self.cols = 16
        self.cell_size = 24
        self.board_canvas = tk.Canvas(
            board_frame, 
            width=self.cols * self.cell_size, 
            height=self.rows * self.cell_size, 
            bg="#fdfdfd", highlightthickness=2, highlightbackground=styles.BORDER
        )
        self.board_canvas.pack()
        self._draw_grid()

        # 돌아가기 버튼
        back_btn = styles.make_button(self, "← 게임 선택으로", lambda: self.app.show_frame("GameSelectFrame"), "Ghost.TButton", width=18)
        back_btn.pack(pady=(10, 20))

    def _draw_grid(self):
        """스코어보드의 빈 격자를 그립니다."""
        self.board_canvas.delete("all")
        w = self.cols * self.cell_size
        h = self.rows * self.cell_size
        # 가로선
        for r in range(self.rows + 1):
            y = r * self.cell_size
            self.board_canvas.create_line(0, y, w, y, fill="#e0e0e0")
        # 세로선
        for c in range(self.cols + 1):
            x = c * self.cell_size
            self.board_canvas.create_line(x, 0, x, h, fill="#e0e0e0")

    def _update_scoreboard(self):
        """저장된 history 데이터를 기반으로 스코어보드에 동그라미를 채웁니다."""
        self._draw_grid()
        
        # 기록이 전광판 칸 수를 넘어가면, 제일 오래된 열(Column)부터 밀어내어 자연스럽게 스크롤링 되도록 처리
        max_items = self.rows * self.cols
        excess = max(0, len(self.history) - max_items)
        shift_cols = (excess + self.rows - 1) // self.rows
        start_idx = shift_cols * self.rows
        display_history = self.history[start_idx:]
        
        for i, winner in enumerate(display_history):
            col = i // self.rows
            row = i % self.rows
            
            x = col * self.cell_size
            y = row * self.cell_size
            p = 2 # 패딩(여백)
            
            if winner == "banker":
                color = styles.ACCENT_RED
                text = "B"
            elif winner == "player":
                color = styles.ACCENT_BLUE
                text = "P"
            else:
                color = styles.ACCENT_GREEN
                text = "T"
                
            # 동그라미 그리기
            self.board_canvas.create_oval(x+p, y+p, x+self.cell_size-p, y+self.cell_size-p, fill=color, outline=color)
            # 글자(B, P, T) 새기기
            self.board_canvas.create_text(x+self.cell_size/2, y+self.cell_size/2, text=text, fill="#ffffff", font=("Helvetica", 10, "bold"))

    def _render_card(self, parent, card):
        """UI에 카드 이미지를 추가합니다."""
        color = styles.card_color(card)
        lbl = tk.Label(parent, text=f"{card.name}\n{card.suit}", font=styles.FONT_CARD,
                       bg=styles.CARD_FACE, fg=color, width=3, relief="flat", bd=0,
                       highlightbackground=styles.BORDER, highlightthickness=1, justify="center")
        lbl.pack(side="left", padx=4)
        return lbl

    def _update_scores_ui(self):
        p_score, b_score = self.game.get_scores()
        self.p_score_lbl.configure(text=f"점수: {p_score}")
        self.b_score_lbl.configure(text=f"점수: {b_score}")

    def on_show(self):
        self.app.refresh_user()
        self.token_label.configure(text=f"보유 토큰: {self.app.current_user['tokens']:,}")
        self._reset_table()

    def _reset_table(self):
        for w in self.p_cards_frame.winfo_children(): w.destroy()
        for w in self.b_cards_frame.winfo_children(): w.destroy()
        self.p_score_lbl.configure(text="점수: 0")
        self.b_score_lbl.configure(text="점수: 0")
        self.message_label.configure(text="베팅할 대상을 선택하고 토큰을 입력하세요.", fg=styles.WHITE)
        self._set_buttons_state("normal")

    def _set_buttons_state(self, state):
        self.bet_entry.configure(state=state)
        self.btn_player.configure(state=state)
        self.btn_tie.configure(state=state)
        self.btn_banker.configure(state=state)

    def _start_round(self, target: str):
        if self.is_dealing: return

        try:
            bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("오류", "토큰은 숫자로 입력해주세요.")
            return

        username = self.app.current_user["username"]
        allowed, reason = db.check_bet_allowed(username, bet)
        if not allowed:
            messagebox.showwarning("참여 불가", reason)
            return

        self._reset_table()
        self.is_dealing = True
        self._set_buttons_state("disabled")
        self.message_label.configure(text=f"{target.upper()}에 베팅하셨습니다. 딜링을 시작합니다...", fg=styles.GOLD_LIGHT)
        
        self.game = BaccaratGame(bet, target)
        
        # 애니메이션 스케줄링 (온라인 카지노처럼 카드 한장씩 오픈)
        self.after(500, self._anim_deal_p1)

    # --- 딜링 애니메이션 로직 ---
    def _anim_deal_p1(self):
        self._render_card(self.p_cards_frame, self.game.player_cards[0])
        self.after(400, self._anim_deal_b1)

    def _anim_deal_b1(self):
        self._render_card(self.b_cards_frame, self.game.banker_cards[0])
        self.after(400, self._anim_deal_p2)

    def _anim_deal_p2(self):
        self._render_card(self.p_cards_frame, self.game.player_cards[1])
        self.after(400, self._anim_deal_b2)

    def _anim_deal_b2(self):
        self._render_card(self.b_cards_frame, self.game.banker_cards[1])
        self._update_scores_ui()
        self.after(800, self._anim_third_cards)

    def _anim_third_cards(self):
        p_third, b_third = self.game.determine_third_cards()
        
        # 서드카드 딜링 순서 (플레이어 먼저, 그 다음 뱅커)
        if p_third:
            self._render_card(self.p_cards_frame, p_third)
            self._update_scores_ui()
            
        def _deal_b3():
            if b_third:
                self._render_card(self.b_cards_frame, b_third)
                self._update_scores_ui()
            self.after(600, self._finish_round)

        # 딜레이를 주어 긴장감 조성
        delay = 800 if p_third else 200
        self.after(delay, _deal_b3)

    def _finish_round(self):
        result, payout = self.game.settle()
        username = self.app.current_user["username"]

        db.add_today_bet(username, self.game.bet_amount)
        new_tokens = db.update_tokens(username, payout)
        csv_logger.log_game(username, GAME_TYPE, self.game.bet_amount, result, payout, new_tokens)

        # 1. 히스토리 저장 및 스코어보드 전광판 갱신
        self.history.append(self.game.winner)
        self._update_scoreboard()

        # 2. 결과 텍스트 처리
        win_str = {"player": "플레이어 승!", "banker": "뱅커 승!", "tie": "무승부 (타이)!"}[self.game.winner]
        
        if result == "win":
            msg = f"🎉 {win_str} 베팅 성공! (+{payout:,} 토큰)"
            fg_color = styles.GREEN_OK
        elif result == "push":
            msg = f"🤝 {win_str} 베팅금 반환 (푸시)"
            fg_color = styles.GOLD_LIGHT
        else:
            msg = f"💀 {win_str} 베팅 실패 (-{self.game.bet_amount:,} 토큰)"
            fg_color = styles.RED

        self.message_label.configure(text=msg, fg=fg_color)
        
        self.app.refresh_user()
        self.token_label.configure(text=f"보유 토큰: {self.app.current_user['tokens']:,}")
        self.is_dealing = False
        self._set_buttons_state("normal")