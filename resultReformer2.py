import re
import xlrd
import xlwt
from statistics import mean

group = "A"
version = "36"
COUNTOTHER = False
TOPNKF = 100


outFile = xlwt.Workbook()
outSheet = outFile.add_sheet('sheet1')

ansFile = xlrd.open_workbook('results/整形済み'+group+'2.xls', formatting_info=True)

ansSheets = ansFile.sheets()
ansSheet = ansSheets[0]

if group == "A":
    index = open("otherFiles/kf3nums.txt")
elif group == "B":
    index = open("otherFiles/kf3nums2.txt")

l = "0"

outLine = 0
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
    print("num:", end = "")
    print(l)
    if len(l) <= 6:
        break
    if l[-1] == "\n":
        l = l[:-1]

    file = open("results/v"+version+"/"+ l +".log")
    content = file.read()
    file.close()

    file = open("results/v"+version+"/"+ l +".log")

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

    verb = ansSheet.cell_value(ansLine, 0)

    if len(resLines) == 0:
        print("FNフレームが見つかりませんでした")
        outLine += 1
        ansLine += 1

        print(verb)
        print(ansSheet.cell_value(ansLine, 0))
        while len(str(ansSheet.cell_value(ansLine, 0))) == 0:
            #print(type(ansSheet.cell_value(ansLine, 0)))
            ansLine += 1
            if ansLine >= ansSheet.nrows:
                print("no more verb in anssheet")
                break
        print("incremented")
        #print(len(str(ansSheet.cell_value(ansLine, 0))))
        print(ansLine)

        continue

    if len(resLines) == 0:
        outLine += 1

    kakuNum = 0
    microRightAnswer = 0
    upperKakuNum = [0]*11
    upperMicroRight = [0]*11

    print(len(resLines))
    lineNum = 0
    for line in resLines:
        lineNum += 1
        if lineNum > TOPNKF:
            break

        print(ansLine)

        if ansLine >= ansSheet.nrows:
            print("break")
            break
        if ansSheet.cell_value(ansLine, 0) != "" and verb not in ansSheet.cell_value(ansLine, 0):
            print("what is ", end="")
            print(ansSheet.cell_value(ansLine, 0))
            break
        ans = ansExtracter.search(line)
        if ans != None:
            fnName = ans.group()[4:-4]
            print(fnName)
            outSheet.write(outLine, 1, fnName)
            answer = ansSheet.cell_value(ansLine,2)
            print(answer)
            outSheet.write(outLine, 2, answer)

            #何人以上正解したか取得
            print(ansSheet.cell_value(ansLine, 4))
            rightHumanNum = int(ansSheet.cell_value(ansLine, 4))

            outSheet.write(outLine, 3, rightHumanNum)
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

            outLine += 1
            ansLine += 1

    if ansLine >= ansSheet.nrows:
        print("break")
        break

    print("verb = " + verb)
    print(ansSheet.cell_value(ansLine, 0))

    while ansSheet.cell_value(ansLine, 0) == "":
        print(type(ansSheet.cell_value(ansLine, 0)))
        ansLine += 1
        print(ansLine)

    upperMicroAvr = [0]*11
    microAvr = microRightAnswer/kakuNum

    for i in range(11):
        print(str(i)+"人以上正解の格フレーム"+str(upperKakuNum[i])+"個中"+str(upperMicroRight[i])+"個正解", end = " ")
        if upperKakuNum[i] == 0:
            upperMicroAvr[i] = -1
        else:
            upperMicroAvr[i] = upperMicroRight[i] / upperKakuNum[i]
        print(upperMicroAvr[i])

    outSheet.write(outLine-1, 4, microRightAnswer)
    outSheet.write(outLine-1, 5, kakuNum)
    outSheet.write(outLine-1, 6, str(microAvr))

    microAvrs.append(microAvr)
    upperMicroAvrs.append(upperMicroAvr)

    allKakuNum += kakuNum
    for i in range(11):
        upper[i] += upperKakuNum[i]

outLine += 1

print(upper)
print(rightUpper)

for i in range(11):
    print(str(upper[i])+ "個中" + str(rightUpper[i]) + "個正解 正解率" + str(rightUpper[i]/upper[i]) )

outSheet.write(outLine, 0, "全体の平均")
outSheet.write(outLine, 1, rightAnswerNum)
outSheet.write(outLine, 2, allKakuNum)
outSheet.write(outLine, 3, str(float(rightAnswerNum)/allKakuNum))

outLine += 1
outSheet.write(outLine, 0, "マクロ平均")

outSheet.write(outLine, 1, str(mean(microAvrs)))
outLine += 1
for i in range(11):
    outSheet.write(outLine, 0, str(i)+"人以上正解のフレーム")
    outSheet.write(outLine, 1, upper[i])
    outSheet.write(outLine, 2, str(rightUpper[i]/upper[i]))
    macro = 0
    zeroVerb = 0
    for j in upperMicroAvrs:
        if j[i] == -1:
            zeroVerb += 1
        else:
            macro += j[i]
    outSheet.write(outLine, 3, str(macro/(len(upperMicroAvrs)-zeroVerb)))
    outLine += 1

outFile.save('results/v'+version+'/result'+version+group+'TOP'+str(TOPNKF)+'_NoOTHER.xls')
print("saved")
file.close()