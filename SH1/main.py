# -*- coding: utf-8 -*-
"""
SH1 (시흥랜드) 에듀 - GUI 기반 학습/미니게임 플랫폼
실행: python3 main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sh1_casino.gui.app import SH1App


def main():
    app = SH1App()
    app.mainloop()


if __name__ == "__main__":
    main()
