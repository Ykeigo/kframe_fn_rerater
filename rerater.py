import fnextracter as fnex
import kfextracter as kfex
import executeCommand as ec
import numpy as np
import os

Ne = 3
CNIL = 0.3

def calcScore(midashi, midashiMostSimilars, fn, model):

    vs = fnex.ExtractVerb(fn)

    # print(vs)

    additional = []
    for i in range(len(vs)):
        # 返ってくるのは一行のはずだからたぶんこれでいい
        res = ec.res_cmd("echo " + vs[i] + " | ./han2zen.pl | nkf | juman | knp -dpnd-fast -tab | ./knp2words.sh")
        parts = res[0].split(" ")
        vs[i] = parts[0]
        for j in range(1, len(parts)):
            additional.append(parts[j])

    # print(vs)
    vs.extend(additional)
    similars = []
    for s in midashiMostSimilars:
        similars.append(s[0])

    # print(similars)
    score = 0
    if vs:
        reratingv = []
        for v in vs:
            # print(v)
            if v in similars:
                try:
                    sim = model.similarity(midashi, v)
                    # print(sim)
                    reratingv.append((v, sim))
                except KeyError as error:
                    print(v + " skipped:not in vocabulary")
            # else:
            # print(v + ' not in similars')
        reratingv.sort()
        # print(reratingv)
        for i in range(min(Ne, len(reratingv))):
            score += reratingv[i][1]
            # print(midashi + " - " + reratingv[i][0] + " " + str(reratingv[i][1]))
    # print(fn + " " + str(score))
    return score


def calcscore2(kframe, fnframe, model, kakuNum):

    # framenetのelementを取り出す
    IDs = fnex.ExtractID(fnframe)
    if len(IDs) == 0:
        return 'None'
    #print(IDs)

    elems = []
    slash = 0
    while slash < 2:
        fnframe = fnframe[:-1]
        if fnframe[-1] == '/':
            slash += 1

    elems.extend(fnex.ExtractElements(fnframe + 'lu/lu' + str(IDs[0]) + '.xml'))

    for i in range(1,len(IDs)):
        newElems = fnex.ExtractElements(fnframe + 'lu/lu' + str(IDs[i]) + '.xml')
        exist = False
        for j in newElems:
            for k in range(len(elems)):
                if j[0] == elems[k][0]:
                    elems[k].extend(j[2:])
                    exist = True
                    break
            #用例に含まれるかは関係なく全部の意味役割のタグが各luに書いてあるはずだからこれいるかどうかわからん
            if not exist:
                elems.extend(j)

    print(elems)

    yorei = kfex.ExtractYorei(kframe)

    ga = yorei[kakuNum][0]
    wo = yorei[kakuNum][1]
    ni = yorei[kakuNum][2]

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

    #gaSem = 'None'
    gaSemScore = []
    for i in range(len(elems)):
        if elems[i][1] != 'Core' or len(elems[i]) <= 2:  # coreでないか用例なしなら飛ばす
            elementAvrs.append(0)
            gaSemScore.append(0)
            continue
        # eAvrは後2回使うので保存しておく
        eAvr = np.zeros(len(model['は']))
        for j in range(2, len(elems[i])):
            if elems[i][j] in model:
                eAvr += model[elems[i][j]]
        eAvr = eAvr / (len(elems[i]) - 2)
        elementAvrs.append(eAvr)

        s = np.dot(gaAvr, eAvr)
        gaSemScore.append(s)
        #if gaSemScore < s:
        #    gaSem = elems[i][0]
        #    gaSemScore = s

    #print(gaSem)
    #print(gaSemScore)
    # 用例が一個もないなら終了
    #if gaSemScore == None:
    if len(gaSemScore) == 0:
        return 0

    #を→にの順で同様に対応する意味役割を決める
    #woSem = 'None'
    woSemScore = []
    #niSem = 'None'
    niSemScore = []

    for i in range(len(elems)):
        if elems[i][1] != 'Core' or len(elems[i]) <= 2:  # coreでないか用例なしなら飛ばす
            woSemScore.append(0)
            continue

        s = np.dot(elementAvrs[i], woAvr)
        woSemScore.append(s)
        #if woSemScore < s:
        #    woSem = elems[i][0]
        #    woSemScore = s

    #if woSemScore < CNIL:
    #    woSem = 'None'
    #    woSemScore = CNIL

    #print(woSem)
    #print(woSemScore)

    for i in range(len(elems)):
        if elems[i][1] != 'Core' or len(elems[i]) <= 2:  # coreでないか用例なしなら飛ばす
            niSemScore.append(0)
            continue

        s = np.dot(elementAvrs[i], niAvr)
        niSemScore.append(s)
        #if niSemScore < s:
        #    niSem = elems[i][0]
        #    niSemScore = s

    #if niSemScore < CNIL:
    #    niSem = 'None'
    #    niSemScore = CNIL
    #print(niSem)
    #print(niSemScore)

    bestScoreSum = 0
    bestCom = (-1,-1,-1)
    for g in range(len(gaSemScore)):
        #ガ格は絶対どれかの意味役割に対応づける
        if gaSemScore[g] <= 0:
            continue
        for w in range(len(niSemScore)):
            #ガ格と同じやつはだめ
            if w == g or woSemScore[w] < CNIL:
                w = -1
                woScore = CNIL
            else:
                woScore = max(woSemScore[w], CNIL)
                #continue

            for n in range(len(niSemScore)):
                #ガ、ヲ格と同じやつはだめ
                nisCore = 0
                if n == g or n == w or niSemScore[n] < CNIL:
                    n = -1
                    niScore = CNIL
                    #continue
                else:
                    niScore = niSemScore[n]

                s = max(gaSemScore[g],CNIL) * np.sqrt(len(ga)) + woScore * np.sqrt(len(ni)) + niScore * np.sqrt(len(wo))
                #print(s)
                if s > bestScoreSum:
                    bestScoreSum = s
                    bestCom = (g,w,n)
    elems.append(('None', 'noCore'))
    print('最良組み合わせ ガ格:' + elems[bestCom[0]][0] + 'ヲ格:' + elems[bestCom[1]][0] + 'ニ格:' + elems[bestCom[2]][0])

    return (bestScoreSum, (elems[bestCom[0]][0],elems[bestCom[1]][0],elems[bestCom[2]][0]))
