import re
import xlrd
import fnextracter
import os

ansFile = xlrd.open_workbook('results/整形済みB2.xls', formatting_info=True)

ansSheets = ansFile.sheets()
ansSheet = ansSheets[0]

index = open("kf3nums2.txt")

l = "0"

outLine = 0
ansLine = 0
rightAnswerNum = 0
midashi = ""
verb = ""

rightSum = 0
noCountKaku = 0
other = 0

while l:

    l = index.readline()
    if len(l) <= 6:
        break
    if l[-1] == "\n":
        l = l[:-1]
    #print(l)
    file = open("results/v6/"+ l +".log")
    content = file.read()
    file.close()

    file = open("results/v6/"+ l +".log")

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
        print("FNフレームが見つかりませんでした")
        outLine += 1
        ansLine += 1

        #print(verb)
        #print(ansSheet.cell_value(ansLine, 0))
        while verb in ansSheet.cell_value(ansLine, 0):
            ansLine += 1
            if ansLine >= ansSheet.nrows:
                break
        #print(ansSheet.cell_value(ansLine, 0))

        continue

    if len(resLines) == 0:
        outLine += 1

    for line in resLines:
        #print(ansLine)
        if ansLine >= ansSheet.nrows:
            break
            #print("break1")
        #print("ans:" + ansSheet.cell_value(ansLine, 0)[:-1] + " verb:" + verb)
        if ansSheet.cell_value(ansLine, 0) != "" and verb not in ansSheet.cell_value(ansLine, 0):
            #print("break2")
            break
        ans = ansExtracter.search(line)
        if ans != None:
            fnName = ans.group()[4:-4]
            #print("fnname:" + fnName)
            col = 3
            answer = ""
            rightNum = 0
            answer = ansSheet.cell_value(ansLine, 2)
            if isinstance(answer, str):
                verbs = []
                if os.path.exists("framenet/frames/"+answer+".xml"):
                    verbs = fnextracter.ExtractVerb("framenet/frames/"+answer+".xml")
                #print(verb)
                if verb[-1] == "\n":
                    verb = verb[:-1]
                if answer == "OTHER":
                    other+=1
                    print(ansLine)
                    print(answer)
                    print(verb)
#                if verb not in verbs:
#                    if answer != "OTHER" and answer != "NOANSWER":
                        #print(ansLine)
                        #print(answer)
                        #print(verb)
                        #print(verbs)
                    noCountKaku += 1
            if answer == fnName:
                rightAnswerNum += 1
            outLine += 1
            ansLine += 1

    if ansLine >= ansSheet.nrows:
        break

    #print(verb)
    #print(ansSheet.cell_value(ansLine, 0))

    if ansLine >= ansSheet.nrows:
        break
    while ansSheet.cell_value(ansLine, 0) == "":
        ansLine += 1

print("saved")
print(noCountKaku)
print(other)
file.close()