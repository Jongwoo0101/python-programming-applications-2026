from tkinter import *

def showImage():
    global photo

    # 선택한 동물에 따라 이미지 변경
    if var.get() == 1:
        photo = PhotoImage(file="./image/강아지.png")
    elif var.get() == 2:
        photo = PhotoImage(file="./image/고양이.png")
    elif var.get() == 3:
        photo = PhotoImage(file="./image/토끼.png")
    else:
        return

    # 이미지 크기 조절 (테스트에 사용된 이미지: 640x640)
    photo = photo.subsample(3, 3)

    # 기존 내용 삭제
    canvas.delete("all")

    # 배경을 흰색으로 변경
    canvas.config(bg="white")

    # Canvas 중앙에 이미지 출력
    canvas.create_image(150, 110, image=photo)


# 메인 윈도우
window = Tk()
window.title("애완동물 선택하기")
window.geometry("420x520")

# 제목
labelTitle = Label(
    window,
    text="좋아하는 동물 투표",
    font=("맑은 고딕", 20, "bold"),
    fg="blue"
)
labelTitle.pack(pady=10)

# 라디오 버튼
var = IntVar()

Radiobutton(window, text="강아지", variable=var, value=1).pack()
Radiobutton(window, text="고양이", variable=var, value=2).pack()
Radiobutton(window, text="토끼", variable=var, value=3).pack()

# 버튼
Button(window, text="사진 보기", command=showImage).pack(pady=10)

# 처음에는 파란 박스만 표시
canvas = Canvas(window, width=300, height=220, bg="blue", highlightthickness=1, highlightbackground="black")
canvas.pack(pady=10)

window.mainloop()