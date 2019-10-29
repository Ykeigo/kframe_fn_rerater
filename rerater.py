import fnextracter as fnex
import kfextracter as kfex
import executeCommand as ec
import numpy as np
import os

Ne = 3
CNIL = 0.0
KFTOPN = 50

def calcScore(midashi, midashiMostSimilars, fnwords, model):
    #print(fnwords)
    similars = []
    for s in midashiMostSimilars:
        similars.append(s[0])

    # print(similars)
    score = 0
    if len(fnwords) > 0:
        reratingv = []
        for v in fnwords:
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


def calcscore2(kframe, fnframedata, model, kakuNum):

    yorei = kfex.ExtractYorei(kframe)

    ga = yorei[kakuNum][0]
    wo = yorei[kakuNum][1]
    ni = yorei[kakuNum][2]
    """
    print("ガ格")
    print(ga)
    print("ヲ格")
    print(wo)
    print("ニ格")
    print(ni)
    """
    gaAvr = np.zeros(len(model["は"]))
    woAvr = np.zeros(len(gaAvr))
    niAvr = np.zeros(len(gaAvr))

    n = 0
    if len(ga) > 0:
        for i in range(min(len(ga),KFTOPN)):
            if ga[i] in model:
                #print(ga[i])
                gaAvr += model[ga[i]]
                n += 1
        if n != 0:
            gaAvr = gaAvr / n
    n = 0
    if len(wo) > 0:
        for i in range(min(len(wo),KFTOPN)):
            if wo[i] in model:
                #print(wo[i])
                woAvr += model[wo[i]]
                n += 1
        if n != 0:
            woAvr = woAvr / n
    n = 0
    if len(ni) > 0:
        for i in range(min(len(ni),KFTOPN)):
            if ni[i] in model:
                #print(ni[i])
                niAvr += model[ni[i]]
                n += 1
        if n != 0:
            niAvr = niAvr / n

    #全部足してから正規化してるから大きさ0になってない
    #↓なにこれ　ベクトルじゃなくなってね
    #gaAvr = np.linalg.norm(gaAvr)
    #woAvr = np.linalg.norm(woAvr)
    #niAvr = np.linalg.norm(niAvr)

    elementAvrs = []
    elems = []

    #全部足したやつを正規化してるから大きさ0になってない
    for i in fnframedata.items():
        elems.append(i[0])
        #↓なにこれ　ベクトルじゃなくなってね
        #elementAvrs.append(np.linalg.norm(np.array(i[1])))
        elementAvrs.append(np.array(i[1]))

    #framenetの用例のベクトルなかったら終了
    if len(elems) == 0:
        return -1

    #print(elems)
    #print(elementAvrs[0])

    gaScore = 0
    woScore = 0
    niScore = 0
    gaSemScore = []
    woSemScore = []
    niSemScore = []

    #print(gaAvr)
    #print(niAvr)
    #print(woAvr)

    for i in range(len(elems)):
        l = np.linalg.norm(elementAvrs[i])
        if np.linalg.norm(gaAvr) > 0 or l == 0:
            s = np.dot(elementAvrs[i], gaAvr) / (l*np.linalg.norm(gaAvr))
            gaSemScore.append(s)
        else:
            gaSemScore.append(0)
        if np.linalg.norm(woAvr) > 0 or l == 0:
            s = np.dot(elementAvrs[i], woAvr) / (l*np.linalg.norm(woAvr))
            woSemScore.append(s)
        else:
            woSemScore.append(0)
        if np.linalg.norm(niAvr) > 0 or l == 0:
            s = np.dot(elementAvrs[i], niAvr) / (l*np.linalg.norm(niAvr))
            niSemScore.append(s)
        else:
            niSemScore.append(0)

    print(gaSemScore)
    print(woSemScore)
    print(niSemScore)

    bestScoreSum = 0
    bestCom = (-1,-1,-1)
    elems.append('None')
    gaSemScore.append(0.0)
    woSemScore.append(0.0)
    niSemScore.append(0.0)

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
                    niScore = max(niSemScore[n], CNIL)

                s = max(gaSemScore[g],CNIL) * np.sqrt(len(ga)) + woScore * np.sqrt(len(ni)) + niScore * np.sqrt(len(wo))
                #print("番号:" + str(g) + "," + str(w) + "," + str(n))
                #print('組み合わせ ガ格:' + elems[g] + 'ヲ格:' + elems[w] + 'ニ格:' + elems[n])
                #print(s)
                if s > bestScoreSum:
                    bestScoreSum = s
                    bestCom = (g, w, n)
    print('最良組み合わせ ガ格:' + elems[bestCom[0]] + 'ヲ格:' + elems[bestCom[1]] + 'ニ格:' + elems[bestCom[2]])
    print("ガ格:" + str(max(gaSemScore[bestCom[0]],CNIL)) + " 重み:" + str(np.sqrt(len(ga))))
    print("ヲ格:" + str(woSemScore[bestCom[1]]) + " 重み:" + str(np.sqrt(len(wo))))
    print("ニ格:" + str(niSemScore[bestCom[2]]) + " 重み:" + str(np.sqrt(len(ni))))

    return (bestScoreSum, (elems[bestCom[0]],elems[bestCom[1]],elems[bestCom[2]]))
