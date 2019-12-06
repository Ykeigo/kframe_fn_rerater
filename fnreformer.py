import fnextracter as fnex
import executeCommand as ec
import os
import sys
import gensim

indexFile = open('./JFNindex.csv', mode='w')

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
            res = ec.res_cmd("echo " + vs[i] + " | ./han2zen.pl | nkf | juman | knp -dpnd-fast -tab | ./knp2words.sh")
            parts = res[0].split(" ")
            vs[i] = parts[0]
            for j in range(1, len(parts)):
                additional.append(parts[j])

    vs.extend(additional)

    indexFile.write(f.name)
    for v in vs:
        indexFile.write("," + v)

    indexFile.write("¥n")

indexFile.close()