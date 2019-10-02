"""
import re

s = "ababandababab"
r = re.compile("(?:ab)+")
res = r.findall(s)
print(res)
"""
"""
import kfextracter as kf
k = kf.ExtractYorei('kframe/web70-201101-068476.formatted')
print(len(k))
for i in k:
    print(len(i))
    print(i)
"""
"""
import rerater
import gensim


embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')

score = rerater.calcscore2("../formatted.merge/web70-201101-053033.formatted", "../jfn/frame/Theft.xml", embedding, 0)

print(score)
"""

import fnextracter
IDs = fnextracter.ExtractElements('./framenet/frames/Separating.xml')
print(IDs)
"""
elements = []
for i in IDs:
    print(str(i))
    a = fnextracter.ExtractElements('../jfn/lu/lu'+str(i)+'.xml')
    for j in a:
        exist = False
        for k in range(len(elements)):
            if elements[k][0] == j[0]:
                elements[k].extend(j[2:])
                exist = True
        if exist == False:
            elements.append(j)
print(elements)
"""
#import kfextracter
#print(kfextracter.ExtractYorei('kframe/web70-201101-068476.formatted','ni'))

#import gensim

#subword使ってない↓
#model = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')

#print(model['車'])
#print(type(model['車']))
"""
import numpy as np
a = np.array([1,2,3])
print(len(a))
"""
"""
import gensim
import fnextracter as fnex
import kfextracter as kfex
import numpy as np

CNIL = 0.5


def calcscore2(kframe, fnframe, model):
    # framenetのelementを取り出す
    IDs = fnex.ExtractID(fnframe)
    #print(IDs)

    elems = []
    slash = 0
    while slash < 2:
        fnframe = fnframe[:-1]
        if fnframe[-1] == '/':
            slash += 1

    for i in IDs:
        elems.extend(fnex.ExtractElements(fnframe + 'lu/lu' + str(i) + '.xml') )

    #print(elems)

    ga = kfex.ExtractYorei(kframe, 'ga')
    wo = kfex.ExtractYorei(kframe, 'wo')
    ni = kfex.ExtractYorei(kframe, 'ni')

    #print(ga)
    #print(wo)
    #print(ni)

    gaAvr = np.zeros(len(model["は"]))
    woAvr = np.zeros(len(gaAvr))
    niAvr = np.zeros(len(gaAvr))

    n = 0
    if len(ga) > 0:
        for i in ga:
            if i in model:
                gaAvr += model[i]
                n += 1
        gaAvr = gaAvr / n
    n = 0
    if len(wo) > 0:
        for i in wo:
            if i in model:
                woAvr += model[i]
                n += 1
        woAvr = woAvr / n
    n = 0
    if len(ni) > 0:
        for i in ni:
            if i in model:
                niAvr += model[i]
                n += 1
        niAvr = niAvr / n

    elementAvrs = []

    # が　を最初にどれが（一番cos類似度の高い意味役割）に割り当てる
    gaSem = 'None'
    gaSemScore = 0
    for i in range(len(elems)):
        if elems[i][1] != 'Core' or len(elems[i]) <= 2:  # coreでないか用例なしなら飛ばす
            elementAvrs.append(0)
            continue
        # eAvrは後2回使うので保存しておく
        eAvr = np.zeros(len(model["は"]))
        for j in range(2, len(elems[i])):
            if elems[i][j] not in model:
                continue
            eAvr += model[elems[i][j]]
        eAvr = eAvr / (len(elems[i]) - 2)
        elementAvrs.append(eAvr)

        s = np.dot(gaAvr, eAvr)
        if gaSemScore < s:
            gaSem = elems[i][0]
            gaSemScore = s

    print(gaSem)
    print(gaSemScore)
    # 用例が一個もないなら終了
    if gaSemScore == 0:
        return 0

    #を→にの順で同様に対応する意味役割を決める
    woSem = 'None'
    woSemScore = 0
    niSem = 'None'
    niSemScore = 0

    for i in range(len(elems)):
        if elems[i][1] != 'Core' or len(elems[i]) <= 2:  # coreでないか用例なしなら飛ばす
            continue

        s = np.dot(elementAvrs[i], woAvr)
        if woSemScore < s:
            woSem = elems[i][0]
            woSemScore = s

    if woSemScore < CNIL:
        woSem = 'None'
        woSemScore = CNIL

    print(woSem)
    print(woSemScore)

    for i in range(len(elems)):
        if elems[i][1] != 'Core' or len(elems[i]) <= 2:  # coreでないか用例なしなら飛ばす
            continue

        s = np.dot(elementAvrs[i], niAvr)
        if niSemScore < s:
            niSem = elems[i][0]
            niSemScore = s

    if niSemScore < CNIL:
        niSem = 'None'
        niSemScore = CNIL
    print(niSem)
    print(niSemScore)

    return gaSemScore * np.sqrt(len(ga)) + niSemScore * np.sqrt(len(ni)) + woSemScore * np.sqrt(len(wo))


embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')
print( calcscore2("../formatted.merge/web70-201101-053033.formatted", "../jfn/frame/Emotion_directed.xml", embedding) )
"""