import fnextracter as fnex
import executeCommand as ec
import os
import sys
import gensim

indexFile = open('./LUIndex.csv', mode='w')

args = sys.argv

#embedding自体はいらんけど語彙の確認のためにいる
embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')

for f in os.scandir(path=args[1]):

    vs = fnex.ExtractVerb(args[1] + "/" + f.name)
    #print(vs)
    # print(vs)

    additional = []
    for i in range(len(vs)):
        # 返ってくるのは一行のはずだからたぶんこれでいい
        if vs[i] not in embedding:
            res = fnex.searchYogenDaihyo(vs[i])
            vs[i] = res

    indexFile.write(f.name)
    for v in vs:
        indexFile.write("," + v)
    print(f.name)
    print(v)

    indexFile.write("\n")

indexFile.close()