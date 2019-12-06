import gensim
import sys
import csv
import kfextracter as kfex
import json
import fnextracter as fnex
import rerater
import random

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

#midashiMostSimilars = embedding.most_similar(midashi, topn=Nt)
midashiMostSimilars = []
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
kakuFrameNum = kfex.getFrameNum(args[1])
print(kakuFrameNum)
for kfnum in range(kakuFrameNum):

    best = 'none.xml' #excelにまとめるときに.xmlがついてないと困る
    bestReration = ("none", "none", "none")
    if len(FNscores) == 0:
        print("input:" + args[1] + " フレーム" + str(kfnum) + " ans:" + "none.xml" + " score:" + str(0))
        print(bestReration)
        continue

    best = FNscores[random.randint(0,len(FNscores)-1)][0]

    print("input:"+args[1] + " フレーム" + str(kfnum) + " ans:" + best + " score:" + str(0))
    print(bestReration)

jfnEmFile.close()
