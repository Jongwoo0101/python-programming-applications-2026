from tkinter import *
import csv
from openpyxl import Workbook


# Entry 표 생성
def makeEmptySheet(r, c):
    retList = []

    for i in range(r):
        tmpList = []

        for j in range(c):
            ent = Entry(window, width=10, justify="center")
            ent.grid(row=i, column=j)
            tmpList.append(ent)

        retList.append(tmpList)

    return retList


csvList = []

# CSV 읽기
with open("StudentInfo.csv", "r", encoding="utf-8") as inFp:
    csvReader = csv.reader(inFp)

    header = next(csvReader)
    csvList.append(header)

    for row in csvReader:

        # 전체 평점 계산
        avg = (float(row[5]) + float(row[6]) + float(row[7]) + float(row[8])) / 4

        row[9] = f"{avg:.2f}"

        csvList.append(row)

rowNum = len(csvList)
colNum = len(csvList[0])

window = Tk()
window.title("학생 정보")

workSheet = makeEmptySheet(rowNum, colNum)

# GUI 출력
for i in range(rowNum):
    for j in range(colNum):

        ent = workSheet[i][j]

        # 제목행
        if i == 0:
            ent.configure(bg="lightgray")

        else:

            # 주소가 경기도면 행 전체 노란색
            if "경기도" in csvList[i][2]:
                ent.configure(bg="yellow")

            # 성적이 3.5 이상이면 해당 셀만 분홍색
            if 5 <= j <= 8:
                if float(csvList[i][j]) >= 3.5:
                    ent.configure(bg="magenta")

        ent.insert(0, csvList[i][j])

# 전체 평점 내림차순 정렬
studentList = csvList[1:]

studentList.sort(key=lambda x: float(x[9]), reverse=True)

# 엑셀 저장
wb = Workbook()
ws = wb.active
ws.title = "Student"

ws.append(header)

for row in studentList:
    ws.append(row)

wb.save("Sortingbygrades.xlsx")

window.mainloop()