import sys
import re
import os

args = sys.argv

# lexunit列挙
#file = open(args[1], "r", encoding='euc-jp', errors='ignore')
file = open(args[1], mode="r", errors='ignore')

#lines = file.readlines()

fileNum = int(args[3]) - 1#0からはじめたいので+1されることを考えて-1
currentMidashi = "a"
currentFile = open(args[2]+'/empty.dat', mode='w')#empty.datはいらないけどcurrentFile.closeができるよう作る
indexFile = None
if not os.path.isfile(args[2]+'/index.csv'):
    indexFile = open(args[2]+'/index.csv', mode='w')
else:
    indexFile = open(args[2]+'/index.csv', mode='a')

#print(file)

for line in file:
    contents = line
    # print(contents)
    midashiExtracter = re.compile('<見出し>.*:')
    midashi = midashiExtracter.match(line)
    if midashi != None:
        if midashi.group() != currentMidashi and midashi.group()[:-2] != currentMidashi:#最後に格フレーム全部の出現頻度の合計みたいなのが書いてある「:全」ってのがある
            print(midashi.group(), file=sys.stderr) #とても汚いけど標準出力は吸われるのでこうする
            #print(midashi.group())
            currentMidashi = midashi.group()
            fileNum += 1
            currentFile.close()
            currentFile = open(args[2]+'/'+str(fileNum).zfill(6)+".kf", mode='w')

            indexFile.write(line[5:-1]+","+str(fileNum)+'\n')

    currentFile.write(line)
indexFile.close()
fileNum += 1
print(fileNum)