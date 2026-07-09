# -*- coding: utf-8 -*-
"""
gui/styles.py
에듀테인먼트 카지노 테마 - 색상/폰트 상수 및 크로스플랫폼(macOS 포함) 위젯 스타일

[중요] macOS(Aqua)에서는 tk.Button / tk.Radiobutton 이 bg, fg, activebackground 같은
색상 옵션을 대부분 무시합니다. 그래서 이전 버전은 M1 맥에서 버튼이 죄다 기본
회색으로만 보였습니다. 해결책은 ttk.Style(테마="clam")을 사용하는 것입니다.
clam 테마는 순수 파이썬으로 그려지기 때문에 Windows / macOS / Linux 어디서든
동일하게 색이 적용됩니다. 이 파일에서 ttk 스타일을 한 번만 등록해두고,
각 화면(gui/*.py)에서는 make_button() / make_entry() 헬퍼만 가져다 쓰면 됩니다.
"""
import tkinter as tk
from tkinter import ttk

# ----------------------------------------------------------------- 색상 팔레트
BG_DARK = "#0c1a26"        # 메인 배경 (딥 네이비)
BG_PANEL = "#152B3D"       # 카드/패널 배경
BG_CARD = "#1E3A50"        # 패널 내부의 한 단계 밝은 박스
BG_TABLE = "#0f3d2e"       # 게임 테이블(펠트) 배경

GOLD = "#f2b705"
GOLD_LIGHT = "#ffd76a"
ACCENT_BLUE = "#4fb3ff"
ACCENT_BLUE_LIGHT = "#9adcff"
ACCENT_GREEN = "#33d17a"
ACCENT_GREEN_LIGHT = "#8af0b3"
ACCENT_PURPLE = "#b98cff"
ACCENT_PURPLE_LIGHT = "#dcc6ff"
ACCENT_RED = "#ff5d5d"
ACCENT_RED_LIGHT = "#ffaaaa"

WHITE = "#f5f6fa"
GRAY = "#93a1b0"
GRAY_DARK = "#4b5b6b"
BORDER = "#2a4256"

CARD_FACE = "#fdfdfd"
CARD_RED = "#e63946"
CARD_BLACK = "#1c1c1c"
CARD_BACK = "#2a4256"

ENTRY_BG = "#0f2233"

GREEN_OK = ACCENT_GREEN
RED = ACCENT_RED

# ----------------------------------------------------------------- 크로스플랫폼 고딕 폰트 패밀리 지정
# macOS: Apple SD Gothic Neo / Windows: 맑은 고딕(Malgun Gothic) / Linux 및 기본: sans-serif
FONT_FAMILY = ("Apple SD Gothic Neo", "Malgun Gothic", "Helvetica", "Arial", "sans-serif")

FONT_TITLE = (FONT_FAMILY, 27, "bold")
FONT_H1 = (FONT_FAMILY, 19, "bold")
FONT_H2 = (FONT_FAMILY, 15, "bold")
FONT_BODY = (FONT_FAMILY, 12)
FONT_BODY_BOLD = (FONT_FAMILY, 12, "bold")
FONT_CARD = (FONT_FAMILY, 17, "bold")
FONT_SMALL = (FONT_FAMILY, 10)
FONT_TOKEN = (FONT_FAMILY, 17, "bold")

_STYLE_SINGLETON = None


def _configure_button_style(style: ttk.Style, name: str, bg: str, fg: str,
                             hover: str, pressed: str = None):
    pressed = pressed or hover
    style.configure(
        name,
        background=bg,
        foreground=fg,
        font=FONT_BODY_BOLD,
        padding=(18, 11),
        borderwidth=0,
        relief="flat",
        focuscolor=bg,   # 포커스 점선 테두리를 배경색과 같게 만들어 숨김
    )
    style.map(
        name,
        background=[("disabled", GRAY_DARK), ("pressed", pressed), ("active", hover)],
        foreground=[("disabled", "#8a97a3")],
    )


def init_styles(root: tk.Misc):
    """앱 시작 시 한 번만 호출. ttk 위젯이 macOS 에서도 색이 제대로 나오도록 설정한다."""
    global _STYLE_SINGLETON
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=BG_DARK, foreground=WHITE, font=FONT_BODY)
    style.configure("TFrame", background=BG_DARK)

    # 버튼 스타일들 (용도별 색상)
    _configure_button_style(style, "Primary.TButton", GOLD, "#241a00", GOLD_LIGHT)
    _configure_button_style(style, "Accent.TButton", ACCENT_BLUE, "#03202f", ACCENT_BLUE_LIGHT)
    _configure_button_style(style, "Success.TButton", ACCENT_GREEN, "#04231a", ACCENT_GREEN_LIGHT)
    _configure_button_style(style, "Purple.TButton", ACCENT_PURPLE, "#1c0f33", ACCENT_PURPLE_LIGHT)
    _configure_button_style(style, "Danger.TButton", ACCENT_RED, "#2a0808", ACCENT_RED_LIGHT)
    _configure_button_style(style, "Ghost.TButton", BG_CARD, WHITE, BG_PANEL)

    # 입력창
    style.configure(
        "Dark.TEntry",
        fieldbackground=ENTRY_BG,
        foreground=WHITE,
        insertcolor=WHITE,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        borderwidth=1,
        padding=8,
    )
    style.map("Dark.TEntry", bordercolor=[("focus", GOLD)])

    # 표(Treeview) - 기록/통계 화면에서 사용
    style.configure(
        "Casino.Treeview",
        background=BG_PANEL,
        fieldbackground=BG_PANEL,
        foreground=WHITE,
        rowheight=28,
        font=FONT_SMALL,
        borderwidth=0,
    )
    style.configure(
        "Casino.Treeview.Heading",
        background=BG_CARD,
        foreground=GOLD_LIGHT,
        font=FONT_BODY_BOLD,
        borderwidth=0,
        relief="flat",
    )
    style.map("Casino.Treeview", background=[("selected", ACCENT_BLUE)],
              foreground=[("selected", "#03202f")])

    style.configure("Casino.Vertical.TScrollbar", background=BG_CARD,
                     troughcolor=BG_DARK, bordercolor=BG_DARK, arrowcolor=WHITE)

    _STYLE_SINGLETON = style
    return style


# ----------------------------------------------------------------- 위젯 헬퍼
def make_button(parent, text, command=None, style="Primary.TButton", width=None):
    """어떤 OS에서도 색이 제대로 보이는 버튼 생성 (ttk 기반)"""
    kwargs = {"text": text, "command": command, "style": style}
    if width is not None:
        kwargs["width"] = width
    return ttk.Button(parent, **kwargs)


def make_entry(parent, width=28, show=None):
    kwargs = {"style": "Dark.TEntry", "width": width}
    if show:
        kwargs["show"] = show
    return ttk.Entry(parent, **kwargs)


def make_card(parent, bg=BG_PANEL, padx=32, pady=26, border=BORDER):
    """은은한 테두리가 있는 카드형 패널"""
    return tk.Frame(parent, bg=bg, padx=padx, pady=pady,
                     highlightbackground=border, highlightthickness=1)


def card_color(card) -> str:
    return CARD_RED if card.suit in ("♥", "♦") else CARD_BLACK