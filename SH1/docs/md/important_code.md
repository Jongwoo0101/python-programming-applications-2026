# 🚀 시흥랜드 에듀 (SH1) - 주요 핵심 코드 및 발표 가이드

본 문서에서는 시스템의 호환성, 비즈니스 로직의 무결성, 확장성, 그리고 데이터의 안정성을 확보하기 위해 고민하고 구현한 5가지 핵심 코드를 소개합니다.

---

## 1. UI/UX: macOS 호환성 및 디자인 통합 로직 (`gui/styles.py`)
> **💡 포인트:** 크로스플랫폼(macOS/Windows) 렌더링 버그 해결 및 폰트 폴백(Fallback) 메커니즘 적용

```python
# macOS(Aqua) 테마의 위젯 색상 무시 버그 우회 및 크로스플랫폼 고딕 폰트 지정
FONT_FAMILY = ("Apple SD Gothic Neo", "Malgun Gothic", "Helvetica", "Arial", "sans-serif")

def init_styles(root: tk.Misc):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")  # 순수 파이썬 기반 clam 테마로 OS 종속성 탈피
    except tk.TclError:
        pass
    
    # 공통 버튼 스타일 매핑 (마우스 호버, 클릭, 비활성화 상태 제어)
    style.map("Primary.TButton",
        background=[("disabled", "#4b5b6b"), ("pressed", "#ffd76a"), ("active", "#f2b705")],
        foreground=[("disabled", "#8a97a3")]
    )
```

* **🗣️ 발표 스피치 가이드:**
  "기본 Tkinter 위젯은 macOS 환경에서 배경색이 무시되거나 한글이 명조체로 강제 렌더링되는 고질적인 문제가 있었습니다. 이를 해결하기 위해 `clam` 테마를 강제 적용하여 OS 독립적인 렌더링 환경을 구축했고, 시스템 폰트 배열을 다중으로 지정해 어떤 환경에서도 의도된 디자인이 깨짐 없이 출력되도록 UI 완성도를 높였습니다."

---

## 2. 게임 로직: 포커 실시간 자산 재검증 및 예외 처리 (`gui/poker_frame.py`)
> **💡 포인트:** 다중 스트리트 베팅 시 발생할 수 있는 초과 베팅 취약점 차단

```python
def _has_enough_for(self, extra_amount: int) -> bool:
    """[버그 수정] 매 스트리트 베팅/콜 전에 실제 잔여 토큰을 재검증"""
    user = self.app.current_user
    # 현재 판에 이미 들어간 토큰을 제외한 순수 잔여 토큰 계산
    remaining = user["tokens"] - self.game.player_total
    return remaining >= extra_amount

def _bet(self):
    # 잔액 부족 시 강제 폴드 처리로 트랜잭션 무결성 유지
    if not self._has_enough_for(self.game.bet_unit):
        messagebox.showwarning("토큰 부족", "남은 토큰이 부족하여 폴드 처리됩니다.")
        self._fold()
        return
    self.game.player_bet()
    self._after_action()
```

* **🗣️ 발표 스피치 가이드:**
  "기존 로직은 포커 게임 시작 시점에만 잔액을 확인하여, 게임 도중 보유 토큰 이상으로 베팅이 가능한 치명적인 논리적 결함이 있었습니다. 이를 해결하기 위해 매 액션(Flop, Turn, River)마다 유저의 실시간 가용 자산을 재검증하는 로직을 추가하였고, 자산이 부족하면 자동으로 폴드 처리되도록 하여 비즈니스 로직의 무결성을 확보했습니다."

---

## 3. 콘텐츠 확장: 데이터 구조 JSON 분리 (`sh1_casino/quiz_manager.py`)
> **💡 포인트:** 데이터와 코드의 분리(Decoupling) 및 복수 정답 판별 알고리즘

```python
def check_answer(quiz: dict, user_answer: str) -> bool:
    correct_answers = quiz.get("answer")
    given = str(user_answer).strip().lower()  # 앞뒤 공백 제거 및 대소문자 무시

    if not correct_answers or not given:
        return False

    # 복수 정답(JSON 내 배열 형태) 구조 지원
    if isinstance(correct_answers, list):
        valid_answers = [str(ans).strip().lower() for ans in correct_answers]
        return given in valid_answers
    
    return str(correct_answers).strip().lower() == given
```

* **🗣️ 발표 스피치 가이드:**
  "프로그램의 유지보수성을 극대화하기 위해 교육용 퀴즈와 상점 데이터를 소스 코드에서 완전히 분리해 JSON 파일로 관리했습니다. 또한 사용자 입력 시의 공백이나 대소문자 예외를 전처리하고, 배열(List) 형태의 복수 정답까지 처리하는 알고리즘을 구현하여 관리자가 손쉽게 콘텐츠를 확장할 수 있는 아키텍처를 완성했습니다."

---

## 4. 데이터베이스: SQLite3 마이그레이션 및 트랜잭션 제한 (`database.py`)
> **💡 포인트:** 데이터베이스 스키마 마이그레이션 및 과몰입 방지(일일 제한) 코어 로직

```python
def init_db():
    conn = get_connection()
    # [마이그레이션 예외 처리] 구버전 DB(chips) 발견 시 신버전(tokens)으로 자동 컬럼 변경
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [row["name"] for row in cursor.fetchall()]
        if columns and "chips" in columns and "tokens" not in columns:
            conn.execute("ALTER TABLE users RENAME COLUMN chips TO tokens;")
            conn.commit()
    except Exception:
        pass

def check_bet_allowed(username: str, bet_amount: int):
    """일일 토큰 사용 한도 제한 검증 (과몰입 방지 로직)"""
    user = get_user(username)
    today_total = get_today_bet_total(username)
    
    if today_total + bet_amount > user["daily_limit"]:
        remaining = max(0, user["daily_limit"] - today_total)
        return False, f"일일 사용 한도를 초과합니다. (오늘 남은 한도: {remaining} 토큰)"
    return True, ""
```

* **🗣️ 발표 스피치 가이드:**
  "영구 데이터 관리를 위해 SQLite3를 도입했습니다. 특히 업데이트 시 발생할 수 있는 데이터 유실을 막기 위해 초기화 시점에 스키마 구조를 자동 갱신하는 마이그레이션 로직을 내장했습니다. 또한, 게이미피케이션의 부작용인 과몰입을 방지하고자, 트랜잭션 발생 직전 사용자의 일일 한도를 검증하는 방어 로직을 통해 건전한 플랫폼 환경을 구축했습니다."

---

## 5. 파일 I/O: CSV 로거 자가 복구 및 통계 산출 (`csv_logger.py`)
> **💡 포인트:** 파일 파손 시 자가 복구(Self-Healing) 및 실시간 통계 데이터(승률, 손익) 연산

```python
FIELDNAMES = ["timestamp", "username", "game_type", "bet_amount", "result", "token_change", "tokens_after"]

def _ensure_csv():
    # [자가 복구] 파일이 없거나, 비정상적으로 다 날아간 0바이트 상태일 때 자동 헤더 복구
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def get_user_stats(username: str):
    """CSV 로그 데이터 원본을 가공하여 승률 및 순손익 통계 자동 산출"""
    logs = get_user_logs(username)
    overall = {"plays": 0, "wins": 0, "losses": 0, "pushes": 0, "total_bet": 0, "net_profit": 0}
    
    for row in logs:
        overall["plays"] += 1
        if row["result"] == "win": overall["wins"] += 1
        # ... (기타 통계 누적 합산 로직) ...
        
    # Zero Division 오류 방지 처리
    overall["win_rate"] = round((overall["wins"] / overall["plays"]) * 100, 1) if overall["plays"] else 0.0
    return {"overall": overall}
```

* **🗣️ 발표 스피치 가이드:**
  "사용자의 플레이 기록은 외부 호환성을 위해 CSV 파일로 분리 보관됩니다. 파일 시스템 특성상 내용이 증발하는 0바이트 파손 현상을 제어하기 위해, 크기를 감지하여 스스로 헤더를 재구성하는 자가 복구 로직을 추가했습니다. 또한 수많은 텍스트 로그를 실시간으로 파싱 및 연산하여 수학적 예외(0으로 나누기) 없이 승률과 손익 데이터를 안전하게 산출하도록 구현했습니다."
```