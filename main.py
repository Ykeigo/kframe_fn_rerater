import gensim
import sys
import os
import kfextracter as kfex
import rerater

Nt = 1000

args = sys.argv

if len(sys.argv) < 4:
    print("usage: python3 rerater.py kakuframe FramenetDirectory kakuFrameNum")
    exit()

print('embedding読み込み')
# subword使ってない↓
embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')

print("Framenet確認中")

# その格フレームの喚起語を取得
midashi = kfex.ExtractMidashi(args[1])

if midashi not in embedding:
    print("midashi " + midashi + " not in vocabulary")
    print("program terminated")
    exit()

midashiMostSimilars = embedding.most_similar(midashi, topn=Nt)
midashiMostSimilars.append(midashi)
FNscores = []
# Framenetのフォルダ内全部見ながら見出し語取得
for f in os.scandir(path=args[2]):
    # print(f.name)
    score = rerater.calcScore(midashi, midashiMostSimilars, args[2] + "/" + f.name,embedding)
    if score > 0:
        FNscores.append((f.name, score))

FNscores.sort(key=lambda x: x[1], reverse=True)
#print(FNscores)

#候補のスコア計算して一番いいやつを正解とする
best = 'none'
bestReration = ("none", "none", "none")
maxScore = 0
for kfnum in range(kfex.getFrameNum(args[1])):
    for f in FNscores:
        s = rerater.calcscore2(args[1], args[2] + "/" + f[0], embedding, int(kfnum))
        #print(s)
        if maxScore < s[0]:
            maxScore = s[0]
            best = f[0]
            bestReration = s[1]

    print("input:"+args[1] + " フレーム"+str(kfnum) + " ans:" + best)
    print(bestReration)