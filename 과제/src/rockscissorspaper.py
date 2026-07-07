from tkinter import *
import random

# 게임 횟수
total = 0
player_win = 0
computer_win = 0

player_choice = ""
computer_choice = ""

photo = None
photoRock = None
photoPaper = None
photoScissors = None


def play(choice):
    global total, player_win, computer_win
    global player_choice, computer_choice
    global photo

    player_choice = choice

    computer_choice = random.choice(["가위", "바위", "보"])

    # 컴퓨터 이미지 출력
    if computer_choice == "가위":
        photo = photoScissors
    elif computer_choice == "바위":
        photo = photoRock
    else:
        photo = photoPaper

    computerLabel.config(image=photo)

    # 승패 판정
    if player_choice == computer_choice:
        result = "무승부!"
    elif (player_choice == "가위" and computer_choice == "보") or \
         (player_choice == "바위" and computer_choice == "가위") or \
         (player_choice == "보" and computer_choice == "바위"):
        result = "인간 승리!"
        player_win += 1
    else:
        result = "컴퓨터 승리!"
        computer_win += 1

    total += 1

    resultLabel.config(text=f"인간 : {player_choice}    컴퓨터 : {computer_choice}    {result}")

    scoreLabel.config(text=f"총 게임 횟수 : {total}  인간 승리 : {player_win}  컴퓨터 승리 : {computer_win}")


window = Tk()
window.title("가위바위보 게임")
window.geometry("700x700")

# 이미지 불러오기
photoScissors = PhotoImage(file="./image/가위.png").subsample(4, 4)
photoRock = PhotoImage(file="./image/바위.png").subsample(4, 4)
photoPaper = PhotoImage(file="./image/보.png").subsample(4, 4)

Label(window, text="Player의 선택은??", font=("맑은 고딕", 16)).pack(pady=10)

frame = Frame(window)
frame.pack()

Button(frame, image=photoScissors, command=lambda: play("가위")).pack(side=LEFT)
Button(frame, image=photoRock, command=lambda: play("바위")).pack(side=LEFT)
Button(frame, image=photoPaper, command=lambda: play("보")).pack(side=LEFT)

Label(window, text="컴퓨터는 다음을 선택하였습니다.", font=("맑은 고딕", 13)).pack(pady=10)

computerLabel = Label(window)
computerLabel.pack()

resultLabel = Label(window, font=("맑은 고딕", 12))
resultLabel.pack(pady=15)

scoreLabel = Label(window, font=("맑은 고딕", 12))
scoreLabel.pack()

window.mainloop()