# -*- coding: utf-8 -*-
"""
gui/styles.py
카지노 컨셉의 다크 그린 & 골드 테마 색상/폰트 상수 (가독성 개선 버전)
"""

# 1. 색상 (배경의 명도 차이를 키워 입체감과 대비를 높임)
BG_DARK = "#051f11"        # 메인 배경 (더 어두운 딥 그린으로 깊이감 부여)
BG_PANEL = "#0a361e"       # 패널/카드 배경
BG_TABLE = "#126b3c"       # 테이블 펠트 색 (더 밝고 선명한 카지노 그린으로 텍스트를 돋보이게 함)

GOLD = "#f1c40f"           # 포인트 골드 (기존보다 더 밝고 쨍하게)
GOLD_LIGHT = "#f8ea8c"
WHITE = "#ffffff"          # f5f5f5에서 완전한 흰색으로 변경하여 텍스트 가독성 극대화
RED = "#ff4757"            # 더 눈에 띄는 빨간색
GREEN_OK = "#2ecc71"
GRAY = "#bdc3c7"           # 어두운 배경에서 잘 보이는 밝은 회색

CARD_BG = "#ffffff"
CARD_RED = "#e74c3c"       # 카드 문양을 더 뚜렷한 빨간색으로
CARD_BLACK = "#111111"

# 2. 버튼 및 입력창 (배경색인 초록색과 완벽히 분리되도록 변경)
BUTTON_BG = "#c0392b"      # 카지노의 상징적인 레드 칩 색상 사용 (초록 배경에서 가장 눈에 띔)
BUTTON_HOVER = "#e74c3c"   
ENTRY_BG = "#1a1a1a"       # 입력창은 어두운 무채색(다크그레이)으로 하여 초록색과 분리

# 3. 폰트 (전체적으로 크기를 1~2포인트 키워 눈의 피로를 줄임)
FONT_TITLE = ("Georgia", 28, "bold")
FONT_H1 = ("Georgia", 20, "bold")
FONT_H2 = ("Georgia", 16, "bold")
FONT_BODY = ("Helvetica", 12)          # 11 -> 12
FONT_BODY_BOLD = ("Helvetica", 12, "bold")
FONT_CARD = ("Helvetica", 18, "bold")  # 16 -> 18
FONT_SMALL = ("Helvetica", 10)         # 9 -> 10
FONT_CHIP = ("Georgia", 16, "bold")


def style_button(btn, bg=BUTTON_BG, fg=WHITE, font=FONT_BODY_BOLD, hover=BUTTON_HOVER):
    """tk.Button에 카지노 테마를 입히고 hover 효과를 추가한다."""
    btn.configure(
        bg=bg, fg=fg, font=font, activebackground=hover, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2", 
        padx=16, pady=10, # 클릭하기 쉽도록 패딩(버튼 크기)을 약간 증가
        highlightthickness=0,
    )
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
    return btn


def card_color(card) -> str:
    return CARD_RED if card.suit in ("♥", "♦") else CARD_BLACK