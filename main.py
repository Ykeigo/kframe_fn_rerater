import gensim
import sys
import csv
import kfextracter as kfex
import fnextracter as fnex
import rerater

Nt = 1000

args = sys.argv

if len(sys.argv) < 3:
    print("usage: python3 rerater.py kakuframe JFNindexFile JFN_LUPath knpParsingDir")
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
elements = {}
reibuns = {}

for f in FNscores:
    #print(args)
    #print(args[3] + '/' + f[0])
    #ID = fnex.searchLu_Verb(args[3] + '/' + f[0], midashi)
    #/を削って前の階層に行く
    """
    path = args[3]
    slash = 0
    while slash < 1:
        path = path[:-1]
        if path[-1] == '/':
            slash += 1
    """
    #その動詞のFramenetの用例と格解析結果からの格の対応をとる
    luFilePath = args[3] + '/' + f[0]
    elements[f[0]] = fnex.ExtractElements(luFilePath)
    depends[f[0]] = fnex.getRoleReration(midashi, luFilePath, args[4])
    reibuns[f[0]] = fnex.ExtractReibun(luFilePath)

    print(f[0])
    print(elements[f[0]])
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
    bestReration = ("none", "none", "none")
    maxScore = 0

    #格フレームの用例
    for i in yorei[kfnum]:
        print(i, end="")
        print(yorei[kfnum][i][:10])
    print("")

    for f in FNscores:
        print("frame:" + fnex.ExtractFrame(args[3]+"/"+f[0]))

        s = rerater.calcscore2(args[1], elements[f[0]], embedding, int(kfnum), depends[f[0]])
        if s == -1:
            print("ans:none.xml")
            continue
        print(s)
        print("")

        if maxScore < s[0]:
            maxScore = s[0]
            #print(args[3]+"/"+f[0])
            best = fnex.ExtractFrame(args[3]+"/"+f[0])
            bestReration = s[1]


        compareDict[best] = s

    print("input:" + args[1] + " フレーム" + str(kfnum) + " ans:" + best + ".xml score:" + str(maxScore))

    compareList.append(compareDict)
    """
    for f in FNscores:
        print("frame:" + f[0] + " score = " + compareDict[f[0]])
        print(compareDict)
    print(bestReration)
    """

for i in range(len(compareList)):
    print("格フレーム " + str(i))
    for f in compareList[i]:
        print("FNフレーム" + f + " score:" + str(compareList[i][f][0]))
        print(str(compareList[i][f][1]))