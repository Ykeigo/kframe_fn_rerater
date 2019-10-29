import gensim
import sys
import csv
import kfextracter as kfex
import json
import fnextracter as fnex
import rerater
import time

Nt = 1000

args = sys.argv

if len(sys.argv) < 3:
    print("usage: python3 rerater.py kakuframe JFNindexFile JFNEmbeddingFile topNFrames")
    exit()

print('embedding読み込み')
# subword使ってない↓
embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')


# その格フレームの喚起語を取得
midashi = kfex.ExtractMidashi(args[1])
print("見出し："+midashi)
if midashi not in embedding:
    print("midashi " + midashi + " not in vocabulary")
    print("program terminated")
    exit()

midashiMostSimilars = embedding.most_similar(midashi, topn=Nt)

#その単語自身を追加
midashiMostSimilars.append((midashi,1.0))

print("Framenet確認中")
FNscores = []
# Framenetのフォルダ内全部見ながら見出し語取得

indexFile = open(args[2], "r")
indexReader = csv.reader(indexFile)

jfnEmFile = open(args[3], "r")
jfnDict = json.load(jfnEmFile)

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
for kfnum in range(kfex.getFrameNum(args[1])):

    best = 'none'
    bestReration = ("none", "none", "none")
    maxScore = 0

    ga = yorei[kfnum][0]
    wo = yorei[kfnum][1]
    ni = yorei[kfnum][2]

    print("ガ格")
    print(ga[:20])
    print("ヲ格")
    print(wo[:20])
    print("ニ格")
    print(ni[:20])

    for f in FNscores:
        #print(fnex.ExtractVerb(args[2] + "/" + f[0]))
        print(f[0])
        """
        ids = fnex.ExtractID("../jfn/frame/"+f[0])
        print(ids)
        elements = []
        for i in ids:
            print(str(i))
            a = fnex.ExtractElements('../jfn/lu/lu' + str(i) + '.xml')
            for j in a:
                exist = False
                for k in range(len(elements)):
                    if elements[k][0] == j[0]:
                        elements[k].extend(j[2:])
                        exist = True
                if not exist:
                    elements.append(j)
        print(elements)
        """

        s = rerater.calcscore2(args[1], jfnDict[f[0]], embedding, int(kfnum))
        if s == -1:
            print("ans:none.xml")
            continue
        print(s)

        if maxScore < s[0]:
            #print("over")
            maxScore = s[0]
            best = f[0]
            bestReration = s[1]

    print("input:"+args[1] + " フレーム" + str(kfnum) + " ans:" + best + " score:" + str(maxScore))
    print(bestReration)

jfnEmFile.close()
