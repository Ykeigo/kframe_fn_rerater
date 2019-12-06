import fnextracter as fnex
import os
import sys
import gensim

args = sys.argv

notInVocab = 0

#embedding自体はいらんけど語彙の確認のためにいる
embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')

for f in os.scandir(path=args[1]):

    elems = fnex.ExtractElements(args[1] + "/" + f.name)
    # print(vs)
    print(f.name, file=sys.stderr)  # とても汚いけど標準出力は吸われるのでこうする

    exist = False
    additional = []
    for role in elems:
        if role[1] == "Core":
            for elem in role[2:]:
                if elem not in embedding:

                    if not exist:
                        print(f.name)
                        exist = True

                    notInVocab += 1
                    print(elem)

print(notInVocab)