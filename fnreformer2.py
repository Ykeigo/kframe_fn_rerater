import fnextracter as fnex
import numpy as np
import json
import os
import sys
import gensim


elementsFile = open('./JFNelementTest.json', mode='w')

args = sys.argv

embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')
wordNum = 0
notInVoc = 0
data = {}

for f in os.scandir(path=args[1]):
# framenetのelementを取り出す
    print(f.name)
    elementAvrs = {}

    fnframe = args[1] + "/" + f.name
    IDs = fnex.ExtractID(fnframe)
    if len(IDs) == 0:
        print("no example in " + f.name)
        data[f.name] = None
        continue
    #print(IDs)

    elems = []
    slash = 0
    while slash < 2:
        fnframe = fnframe[:-1]
        if fnframe[-1] == '/':
            slash += 1

    for i in range(0,len(IDs)):
        newElems = fnex.ExtractElements(fnframe + 'lu/lu' + str(IDs[i]) + '.xml')
        #print(newElems)
        #print(elems)
        if len(elems) == 0 and len(newElems) > 0:
            elems.extend(newElems)
            continue

        exist = False
        for j in newElems:
            for k in range(len(elems)):
                if j[0] == elems[k][0]:
                    #print(j[2:])
                    elems[k].extend(j[2:])
                    exist = True
                    break
            #用例に含まれるかは関係なく全部の意味役割のタグが各luに書いてあるはずだからこれいるかどうかわからん
            if not exist:
                #print("no")
                elems.extend(j)
    print("element")
    print(elems)

    for i in range(len(elems)):
        if elems[i][1] != 'Core' or len(elems[i]) <= 2:  # coreでないか用例なしなら飛ばす
            continue
        # eAvrは後2回使うので保存しておく
        eAvr = np.zeros(len(embedding['は']))
        for j in range(2, len(elems[i])):
            if elems[i][j] in embedding:
                eAvr += embedding[elems[i][j]]
                wordNum += 1
            else:
                print(str(elems[i][j]) + "is not in vocabulary")
                notInVoc += 1
        eAvr = eAvr / (len(elems[i]) - 2)
        elementAvrs[elems[i][0]] = eAvr.tolist()

    data[f.name] = elementAvrs
#print(data)
json.dump(data, elementsFile, indent=4)

elementsFile.close()

print(str(wordNum) + " words")
print(str(notInVoc) + " is not in vocabulary")