import gensim
import sys
import csv
import kfextracter as kfex
import fnextracter as fnex
import rerater
import pathMover as pm

Nt = 1000

args = sys.argv

if len(args) < 5:
    print("usage: python3 rerater.py kakuframe JFNindexFile JFN_LUPath knpParsingDir")
    exit()

if len(args) == 6:
    # BETAの値は関係ない
    rerater.setALPHABETA(float(args[5]), 0)
    #print("setting only alpha?")
    #exit()
#if len(args) == 7:
#    rerater.setALPHABETA(float(args[5]),float(args[6]))

print('embedding読み込み')
# subword使ってない↓
embedding = gensim.models.KeyedVectors.load_word2vec_format("./knownEmbedding.vec")#('./knownEmbedding.vec')


# その格フレームの喚起語を取得
midashi = kfex.ExtractMidashi(args[1])
print("見出し："+midashi)
if midashi not in embedding:
    print("midashi " + midashi + " not in vocabulary")
    print("program terminated")
    exit()

#midashiMostSimilars = embedding.most_similar(midashi, topn=Nt)
midashiMostSimilars = []
#その単語自身を追加
midashiMostSimilars.append((midashi,1.0))

print("Framenet確認中")
FNscores = []
# Framenetのフォルダ内全部見ながら見出し語取得

indexFile = open(args[2], "r")
indexReader = csv.reader(indexFile)

for row in indexReader:
    # print(f.name)
    score = rerater.calcScore(midashi, midashiMostSimilars, row[1:], embedding)
    if score > 0:
        FNscores.append((row[0], score))

FNscores.sort(key=lambda x: x[1], reverse=True)
indexFile.close()

print(FNscores)

#候補のスコア計算して一番いいやつを正解とする
yorei = kfex.ExtractYorei(args[1])

depends = {}
ukemiDepends = {}
elements = {}
reibuns = {}

for f in FNscores:
    e = {}
    #その動詞のFramenetの用例と格解析結果からの格の対応をとる
    luFilePath = args[3] + '/' + f[0]
    e["lu"] = fnex.ExtractElements(luFilePath)

    framePath = luFilePath
    framePath = pm.movePath(framePath,2)
    framePath = framePath + "/frame/" + fnex.ExtractFrame(luFilePath) + ".xml"

    subElements = fnex.ExtractSubElements(luFilePath)

    frameReibunElements = fnex.ExtractElements_Frame(framePath)
    for i in range(len(subElements)):
        for j in range(len(frameReibunElements)):
            if len(frameReibunElements[j]) > 2:
                if subElements[i][0] == frameReibunElements[j][0]:
                    subElements[i].extend(frameReibunElements[j][2:])
                else:
                    subElements.append(frameReibunElements[j])

    e["frame"] = subElements
    e["parent"] = fnex.ExtractParentsElement(framePath)

    elements[f[0]] = e


    depends[f[0]] = fnex.getRoleRelation(midashi, luFilePath, args[4])#,useFrame=False)
    ukemiDepends[f[0]] = fnex.getRoleRelation(midashi, luFilePath, args[4], ukemi=True)#, useFrame=False)
    reibuns[f[0]] = fnex.ExtractReibun(luFilePath)

    print(f[0])
    print("LU elements: " , end = "")
    print(elements[f[0]]["lu"])
    print("frame elements: " , end = "")
    print(elements[f[0]]["frame"])
    print("parent elements: " , end = "")
    print(elements[f[0]]["parent"])
#print(elements)
#print("ele")

compareList = []

for kfnum in range(min( kfex.getFrameNum(args[1]), 55)):
    # 55っていう数字は川原さんの正解データで一番多い動詞のフレーム数が53だったから

    compareDict = {}

    print("例文:")
    for r in reibuns:
        print(fnex.ExtractFrame(args[3]+"/"+r))
        for i in reibuns[r]:
            print(i)
    print("")

    best = 'none.xml' #excelにまとめるときに.xmlがついてないと困る
    maxScore = 0

    #格フレームの用例
    for i in yorei[kfnum]:
        print(i, end="")
        print(yorei[kfnum][i][:10])
    print("")

    for f in FNscores:
        print("frame:" + fnex.ExtractFrame(args[3]+"/"+f[0]))

        s = rerater.calcscore2(args[1], elements[f[0]], embedding, int(kfnum), depends[f[0]], ukemiDepends[f[0]])
        if s == -1:
            print("ans:none.xml")
            continue
        print(s)
        print("")

        if maxScore < s[0]:
            maxScore = s[0]
            #print(args[3]+"/"+f[0])
            best = fnex.ExtractFrame(args[3]+"/"+f[0])

        compareDict[fnex.ExtractFrame(args[3]+"/"+f[0])] = s

    for f in compareDict:
        print("FNフレーム" + f + " score:" + str(compareDict[f][0]))
        print(str(compareDict[f][1]))

    print("input:" + args[1] + " フレーム" + str(kfnum) + " ans:" + best + ".xml score:" + str(maxScore))

    compareList.append(compareDict)
    """
    for f in FNscores:
        print("frame:" + f[0] + " score = " + compareDict[f[0]])
        print(compareDict)
    print(bestRelation)
    """

for i in range(len(compareList)):
    print("格フレーム " + str(i))
    for f in compareList[i]:
        print("FNフレーム" + f + " score:" + str(compareList[i][f][0]))
        print(str(compareList[i][f][1]))