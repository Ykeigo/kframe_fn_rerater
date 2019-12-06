import re
import xlrd
import sys
import os
from statistics import mean

args = sys.argv

group = args[2]
COUNTOTHER = False

macroAvrs = []

for f in os.scandir(path=args[1]):
    print(f.name)

    path = args[1] + "/" + f.name

    ansFile = xlrd.open_workbook('整形済み'+group+'2.xls', formatting_info=True)

    ansSheets = ansFile.sheets()
    ansSheet = ansSheets[0]

    if group == "A":
        index = open("kf3nums.txt")
    elif group == "B":
        index = open("kf3nums2.txt")

    l = "0"

    ansLine = 0
    rightAnswerNum = 0
    allKakuNum = 0
    microAvrs = []
    midashi = ""
    verb = ""
    # 正解した人間がindex人以上で正解した格の個数
    rightUpper = [0] * 11
    # 正解した人間がindex人以上の格の個数
    upper = [0] * 11
    upperMicroAvrs = []

    while 1:
        l = index.readline()
        #print("num:", end = "")
        #print(l)
        if len(l) <= 6:
            break
        if l[-1] == "\n":
            l = l[:-1]

        print(path+"/"+ l +".log")
        file = open(path+"/"+ l +".log")
        content = file.read()
        file.close()

        file = open(path+"/"+ l +".log")

        #answerファイルからその動詞検索
        file.readline()
        file.readline()
        l = file.readline()

        midashi = l[4:]
        #print(midashi)
        file.close()

        # lexunit列挙

        ansExtracter = re.compile('ans.*xml')
        resLineExtracter = re.compile('input:.*score')
        resLines = resLineExtracter.findall(content)

        verb = ansSheet.cell_value(ansLine, 0)

        if len(resLines) == 0:
            #print("FNフレームが見つかりませんでした")
            ansLine += 1

            #print(verb)
            #print(ansSheet.cell_value(ansLine, 0))
            while len(str(ansSheet.cell_value(ansLine, 0))) == 0:
                #print(type(ansSheet.cell_value(ansLine, 0)))
                ansLine += 1
                if ansLine >= ansSheet.nrows:
                    #print("no more verb in anssheet")
                    break
            #print("incremented")
            #print(len(str(ansSheet.cell_value(ansLine, 0))))
            #print(ansLine)

            continue


        kakuNum = 0
        microRightAnswer = 0
        upperKakuNum = [0]*11
        upperMicroRight = [0]*11

        #print(len(resLines))
        for line in resLines:
            #print(ansLine)

            if ansLine >= ansSheet.nrows:
                #print("break")
                break
            if ansSheet.cell_value(ansLine, 0) != "" and verb not in ansSheet.cell_value(ansLine, 0):
                #print("what is ", end="")
                #print(ansSheet.cell_value(ansLine, 0))
                break
            ans = ansExtracter.search(line)
            if ans != None:
                fnName = ans.group()[4:-4]
                #print(fnName)
                answer = ansSheet.cell_value(ansLine,2)
                #print(answer)

                #何人以上正解したか取得
                #print(ansSheet.cell_value(ansLine, 4))
                rightHumanNum = int(ansSheet.cell_value(ansLine, 4))

                #正解なら正解数増やす
                if answer == fnName:
                    rightAnswerNum += 1
                    microRightAnswer += 1
                    for i in range(rightHumanNum + 1):
                        rightUpper[i] += 1
                        upperMicroRight[i] += 1

                if COUNTOTHER or ( answer != "OTHER" and answer != "NOANSWER" and ansSheet.cell_value(ansLine,3) != "NOVERB"):
                    kakuNum += 1

                    for i in range(rightHumanNum + 1):
                        upperKakuNum[i] += 1

                ansLine += 1

        if ansLine >= ansSheet.nrows:
            #print("break")
            break

        #print("verb = " + verb)
        #print(ansSheet.cell_value(ansLine, 0))

        while ansSheet.cell_value(ansLine, 0) == "":
            #print(type(ansSheet.cell_value(ansLine, 0)))
            ansLine += 1
            #print(ansLine)

        upperMicroAvr = [0]*11
        microAvr = microRightAnswer/kakuNum

        for i in range(11):
            #print(str(i)+"人以上正解の格フレーム"+str(upperKakuNum[i])+"個中"+str(upperMicroRight[i])+"個正解", end = " ")
            if upperKakuNum[i] == 0:
                upperMicroAvr[i] = -1
            else:
                upperMicroAvr[i] = upperMicroRight[i] / upperKakuNum[i]
            #print(upperMicroAvr[i])


        microAvrs.append(microAvr)
        upperMicroAvrs.append(upperMicroAvr)

        allKakuNum += kakuNum
        for i in range(11):
            upper[i] += upperKakuNum[i]

    #print(upper)
    #print(rightUpper)

    for i in range(11):
        print(str(upper[i])+ "個中" + str(rightUpper[i]) + "個正解 正解率" + str(rightUpper[i]/upper[i]) )

    macroAvrs.append((f.name, rightUpper[i]/upper[i], mean(microAvrs)))

for i in macroAvrs:
    print(i)