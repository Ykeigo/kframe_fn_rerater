import re
import xlrd
import xlwt

outFile = xlwt.Workbook()
outSheet = outFile.add_sheet('sheet1')

ansFile = xlrd.open_workbook('my20171129JFN_KCF.xls', formatting_info=True)

ansSheets = ansFile.sheets()
ansSheet = ansSheets[1]

index = open("kf3nums.txt")

l = "0"

outLine = 0
ansLine =1
rightAnswerNum = 0
midashi = ""
verb = ""
while l:

    l = index.readline()
    if len(l) <= 6:
        break
    if l[-1] == "\n":
        l = l[:-1]
    print(l)
    file = open("results/v6/"+ l +".log")
    content = file.read()
    file.close()

    file = open("results/v6/"+ l +".log")

    #answerファイルからその動詞検索
    file.readline()
    file.readline()
    l = file.readline()

    midashi = l[4:]
    print(midashi)
    outSheet.write(outLine,0,midashi)
    file.close()

    # lexunit列挙

    ansExtracter = re.compile('ans.*xml')
    resLineExtracter = re.compile('input:.*score')
    resLines = resLineExtracter.findall(content)

    verb = ansSheet.cell_value(ansLine, 1)[:-4]

    if len(resLines) == 0:
        print("FNフレームが見つかりませんでした")
        outLine += 1
        ansLine += 1

        print(verb)
        print(ansSheet.cell_value(ansLine, 1)[:-4])
        while verb in ansSheet.cell_value(ansLine, 1)[:-4]:
            ansLine += 1
            if ansLine >= ansSheet.nrows:
                break
        print(ansSheet.cell_value(ansLine, 1)[:-4])

        continue

    if len(resLines) == 0:
        outLine += 1

    for line in resLines:
        print(ansLine)
        if ansLine >= ansSheet.nrows:
            break
        if verb not in ansSheet.cell_value(ansLine, 1)[:-4]:
            break
        ans = ansExtracter.search(line)
        if ans != None:
            fnName = ans.group()[4:-4]
            print(fnName)
            outSheet.write(outLine, 1, fnName)
            col = 3
            answer = ""
            for col in range(len(ansSheet.row_values(ansLine))):
                #セルを選択する
                cell = ansSheet.cell(ansLine, col)
                #print(ansSheet.cell_value(ansLine, col))

                #背景色を取得する
                xf = ansFile.xf_list[cell.xf_index]

                font = ansFile.font_list[xf.font_index]
                if not font:
                    break
                color = ansFile.colour_map.get(font.colour_index)
                #print(color)

                if color[0] > 200:
                    answer = ansSheet.cell_value(ansLine, col)
                    break
                col += 1

            outSheet.write(outLine, 2, answer)
            if answer == fnName:
                rightAnswerNum += 1
            outLine += 1
            ansLine += 1

    if ansLine >= ansSheet.nrows:
        break

    print(verb)
    print(ansSheet.cell_value(ansLine, 1)[:-4])

    if ansLine >= ansSheet.nrows:
        break
    while verb in ansSheet.cell_value(ansLine, 1)[:-4]:
        ansLine += 1

outSheet.write(outLine, 1, rightAnswerNum)

outFile.save('results/v6/result.xls')
print("saved")
file.close()