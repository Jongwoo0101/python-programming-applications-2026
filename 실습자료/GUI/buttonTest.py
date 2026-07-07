# 버튼을 누르면 파이썬이 종료되는 코드
from tkinter import *

window = Tk()

button1 = Button(window, text="파이썬 종료", fg="red", command=window.destroy)

button1.pack()

window.mainloop()