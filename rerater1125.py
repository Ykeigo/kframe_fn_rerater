import fnextracter as fnex
import kfextracter as kfex
import executeCommand as ec
import numpy as np
import os

Ne = 3
CNIL = 0.0
KFTOPN = 100

ALPHA = 0.8
BETA = 0.1

NORERATION = 0.25
NONETOKEN = "None"
SAMEKAKU = 0.6

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

def calcscore2(kframe, elements, model, kakuNum, reration, ukemiReration ):
    print(elements)
    #print(elements)

    ###################
    #  mainから渡すやつ #
    ###################
    yorei = kfex.ExtractYorei(kframe)
    kfweight = kfex.getYoreiNum(kframe)
    """
    print("ガ格")
    print(ga)
    print("ヲ格")
    print(wo)
    print("ニ格")
    print(ni)
    """
    kfavrs = {}
    # 用例の中に未知語があればTrue,なければFalse
    kfmichigo = {}
    # 語彙にある単語の数を記録する　あとでニとヘを合成するときにいる
    kfValidWordNum = {}

    n = 0
    #格フレームの用例の単語ベクトルの平均をとる
    for i in yorei[kakuNum]:
        kfmichigo[i] = False
        avr = np.zeros(len(model["は"]))
        for j in range(min(len(yorei[kakuNum][i]), KFTOPN)):
            if yorei[kakuNum][i][j] in model:
                # print(ga[i])
                avr += model[yorei[kakuNum][i][j]]
                n += 1
            else:
                kfmichigo[i] = True
        if n != 0:
            avr = avr / n
        # 用例が一個もなければ勝手に0になる
        kfavrs[i] = avr
        kfValidWordNum[i] = n

    #print(kfavrs)

    #luの単語ベクトルの平均をとる
    #print(elements)
    elementAvrs = {}
    fnmichigo = {}

    for el in elements["lu"]:
        avrGroups = {}
        fnmichigo[el[0]] = False
        luavr = np.zeros(len(model["は"]))
        fravr = np.zeros(len(model["は"]))
        paavr = np.zeros(len(model["は"]))

        n = 0
        for i in el[2:]:
            if i in model:
                # print(ga[i])
                luavr += model[i]
                n += 1
            else:
                fnmichigo[el[0]] = True
        if n != 0:
            luavr = luavr / n
        # 用例が一個もなければ勝手に0になる
        avrGroups["lu"] = luavr

        n = 0
        for i in elements["frame"]:
            #print(i[0])
            if i[0] == el[0]:
                for j in i[2:]:
                    #print(j)
                    if j in model:
                        #print("is in embedding")
                        # print(ga[i])
                        fravr += model[j]
                        n += 1
                if n != 0:
                    fravr = fravr / n
                # 用例が一個もなければ勝手に0になる
                break
        avrGroups["frame"] = fravr

        n = 0
        for i in elements["parent"]:
            #print(i[0])
            if i[0] == el[0]:
                for j in i[2:]:
                    #print(j)
                    if j in model:
                        #print("is in embedding")
                        # print(ga[i])
                        paavr += model[j]
                        n += 1
                if n != 0:
                    paavr = paavr / n
                # 用例が一個もなければ勝手に0になる
                break
        avrGroups["parent"] = paavr

        elementAvrs[el[0]] = avrGroups

    avrGroups["lu"] = np.zeros(len(model["は"]))
    avrGroups["frame"] = np.zeros(len(model["は"]))
    avrGroups["parent"] = np.zeros(len(model["は"]))

    elementAvrs[NONETOKEN] = avrGroups
    fnmichigo[NONETOKEN] = False

    #print(elementAvrs.keys())

    # rerationにヒントがあるか確認する　あればそれを使う
    # 一対一で選択肢がないものを全部currenComsに入れる
    guaranteed = []  # 一対一で確定したもの
    # この辞書に入ってたら選択肢が絞られるやつ
    limitedkf = {}
    limitedfn = {}
    # 格とelementに対してgivenに何回ずつ入ってたかを確認する

    reration.extend(convUkemiReration(ukemiReration))

    for g in reration:
        # print(g[0])
        if g[1] in limitedkf:
            l = limitedkf[g[1]].copy()
            # print(type(l))
            l.append(g[0])
            limitedkf[g[1]] = l
        else:
            limitedkf[g[1]] = [g[0]]
        if g[0] in limitedfn:
            l = limitedfn[g[0]].copy()
            l.append(g[1])
            limitedfn[g[0]] = l
        else:
            limitedfn[g[0]] = [g[1]]

    d = limitedkf.copy()
    for k in d:
        # 一対一の対応だったら確定
        # print(k)
        if len(limitedkf[k]) == 1 and len(limitedfn[limitedkf[k][0]]) == 1:
            guaranteed.append((limitedkf[k][0],limitedfn[limitedkf[k][0]][0]))
            limitedfn.pop(limitedkf[k][0])
            limitedkf.pop(k)

    # guaranteed = 確定
    # fndic,kfdicに入ってる = しぼれる
    # ↑に入ってない = 全部試す

    #格フレームの格の名前リストを作る
    kfnames = []
    elementNames = []

    if "ガ" not in kfweight[kakuNum]:
        print("frame" + str(kakuNum) + " にはガ格がありません")

    #ヘとニを類似度によっては合成する
    if "ニ" in kfavrs and "ヘ" in kfavrs:
        # kfValidWordNum["ニ"]
        sim = 0
        if kfValidWordNum["ニ"] > 0 and kfValidWordNum["ヘ"]: # 語彙にない単語だけだと平均ベクトルが0になって0で割ることになる
            sim = np.dot(kfavrs["ニ"],kfavrs["ヘ"]) / (np.linalg.norm(kfavrs["ニ"]) * np.linalg.norm(kfavrs["ヘ"]))
            print("ニ格とヘ格の類似度:"+str(sim))

        if sim > SAMEKAKU:
            kfweight[kakuNum]["ニ"] += kfweight[kakuNum]["ヘ"]
            kfavrs["ニ"] = (kfavrs["ニ"] * kfValidWordNum["ニ"] + kfavrs["ヘ"] * kfValidWordNum["ヘ"]) / (kfValidWordNum["ニ"] + kfValidWordNum["ヘ"])

            kfavrs.pop("ヘ")

    for i in kfavrs:
        # 必須格かどうかはとりあえず置いておいて全部使う
        # 必須格じゃないやつにroleが対応づいたぞっていうrelationがきた時だるいから
        #print(i)
        if i[0] == '@':
            i = i[1:]

        if "ガ" not in kfweight[kakuNum]:
            kfnames.append(i)
        elif kfweight[kakuNum][i] >= kfweight[kakuNum]["ガ"]:
            #print(str(kfweight[kakuNum][i]) + " " + str(kfweight[kakuNum]["ガ"]))
            kfnames.append(i)
    kfnames.append(NONETOKEN)

    # guaranteedにその格フレームには含まれていない格が入ってることがあるのでそれを消す
    # kfnamesにはガ格より用例数が少ない格は入ってないので例文で明示されていたとしてもそれはノーカン
    #print(guaranteed)
    sa = 0
    for i in range(len(guaranteed)):
        #print(i-sa)
        #print(guaranteed[i-sa])
        if guaranteed[i-sa][1] not in kfnames:
            guaranteed.pop(i-sa)
            sa += 1

    #limitedkfも同じ
    l = limitedkf.copy()
    for i in l:
        if i not in kfnames:
           limitedkf.pop(i)

    #FNフレームのroleの名前リストを作る
    for i in elements["lu"]:
        #意味役割はCoreだけ見る
        if i[1] == "Core":
            elementNames.append(i[0])
    elementNames.append(NONETOKEN)

    # limitedfnも同じ
    l = limitedfn.copy()
    for i in l:
        if i not in elementNames:
            limitedkf.pop(i)

    #確定してるやつをrole名前リストから削除
    for g in guaranteed:
       #print(g)
        if g[0] in elementNames:
            elementNames.remove(g[0])
        if g[1] in kfnames:
            kfnames.remove(g[1])
    """
    for l in limitedkf:
        if l in kfnames:
            kfnames.remove(l)
    """
    #ヒントになってるやつは確定ではないので選択肢にNoneを入れておく
    #print(limitedkf)
    for l in limitedkf:
        limitedkf[l].append(NONETOKEN)
    for l in limitedfn:
        limitedfn[l].append(NONETOKEN)

    semScores = {}
    #全組み合わせの類似度を計算しておく
    for i in kfavrs:
        l = np.linalg.norm(kfavrs[i])
        sems = {}
        for j in elementAvrs:
            groups = {}
            #print(elementAvrs[j].keys())
            #print(i)
            #print(j)
            #print(j, end = " ")
            #print(l, end = " ")
            #print(np.linalg.norm(elementAvrs[j]["lu"]))

            if np.linalg.norm(elementAvrs[j]["lu"]) > 0 and l > 0:
                s = np.dot(kfavrs[i],elementAvrs[j]["lu"]) / (l * np.linalg.norm(elementAvrs[j]["lu"]))
                groups["lu"] = s
                #sems[j] = s
            # 未知語でもいいからなんか用例あったら無関係の関連度入れとく
            #elif l == 0 and kfmichigo[i] and j != NONETOKEN:
            #    sems[j] = NORERATION
            #elif np.linalg.norm(elementAvrs[j]) == 0 and fnmichigo[j] and j != NONETOKEN:
            #    sems[j] = NORERATION
            # 用例がなければ類似度0
            # 用例がなければ無関係の類似度
            elif j != NONETOKEN:
                groups["lu"] = NORERATION
                #sems[j] = NORERATION
            else:
                groups["lu"] = 0

            if np.linalg.norm(elementAvrs[j]["frame"]) > 0 and l > 0:
                s = np.dot(kfavrs[i],elementAvrs[j]["frame"]) / (l * np.linalg.norm(elementAvrs[j]["frame"]))
                groups["frame"] = s
            elif j != NONETOKEN:
                groups["frame"] = NORERATION
            else:
                groups["frame"] = 0

            if np.linalg.norm(elementAvrs[j]["parent"]) > 0 and l > 0:
                s = np.dot(kfavrs[i],elementAvrs[j]["parent"]) / (l * np.linalg.norm(elementAvrs[j]["parent"]))
                groups["parent"] = s
            elif j != NONETOKEN:
                groups["parent"] = NORERATION
            else:
                groups["parent"] = 0
            #print(groups)
            sems[j] = groups

        semScores[i] = sems

    #print(kfmichigo)
    #print(fnmichigo)
    print("使う格: ", end="")
    print(kfnames)
    print("element: ", end="")
    print(elementNames)
    print("このluの単語群間の類似度: ")
    #print(semScores)
    print("     ", end = "")
    for i in elements["lu"]:
        if i[1] == "Core" or len(i) >= 3:
            print(i[0], end = " ")
    print("")
    print("     ", end = "")
    for i in elements["lu"]:
        if i[1] == "Core" or len(i) >= 3:
            if len(i) >= 3:
                print(i[2], end = " ")
            else:
                print("なし", end=" ")
    print("")
    for i in semScores:
        if "ガ" in kfweight[kakuNum] and kfweight[kakuNum][i] < kfweight[kakuNum]["ガ"]:
            continue
        #格の名前表示
        print(i, end = " ")
        if len(i) == 1:
            print("  ", end = "")
        #類似度表示
        for j in elements["lu"]:
            if j[1] == "Core" or len(j) >= 3:
                print('{:.5f}'.format(semScores[i][j[0]]["lu"]), end = " ")
        print("")

    print("格解析結果: ", end="")
    print(reration)
    print("格解析結果（受け身）: ", end="")
    print(ukemiReration)
    print("確定したペア: ", end="")
    print(guaranteed)
    print("ヒントのあるペア: ", end="")
    print(limitedkf)
    print(limitedfn)
    allCom = []

    # 全組み合わせ作る
    comAll(kfnames, elementNames, guaranteed, allCom, limitedfn)

    #print(allCom)
    #print(kfweight)
    # 出てきた全組み合わせでスコア計算してくっつける
    for c in allCom:
        score = 0
        #print(c)
        for p in c:
            #重みはlogでもいいかもしれない
            #print(c)
            #print(p)
            if kakuNum >= len(kfweight):
                print(str(kakuNum) + "is out of kfweight")
            elif p[1] not in kfweight[kakuNum]:
                print( p[1] + "is not in kfweight[" + str(kakuNum) + "]")

            s1 = semScores[p[1]][p[0]]["lu"] * ALPHA
            s2 = semScores[p[1]][p[0]]["frame"] * BETA
            s3 = semScores[p[1]][p[0]]["parent"] * (1-ALPHA-BETA)

            #s = semScores[p[1]][p[0]] * np.sqrt(int(kfweight[kakuNum][p[1]]))
            #s = semScores[p[1]][p[0]] * np.log10(int(kfweight[kakuNum][p[1]]))
            score += (s1+s2+s3) #* pow( int(kfweight[kakuNum][p[1]]) , 1.0/2)

        c.append(score)
        #print(c)

    #
    sortedCom = sorted(allCom, key=lambda x: x[-1], reverse=True)

    bestCom = sortedCom[0]
    #print(bestCom)

    """
    print('最良組み合わせ ガ格:' + elementNames[bestCom[0]] + 'ヲ格:' + elementNames[bestCom[1]] + 'ニ格:' + elementNames[bestCom[2]])
    print("ガ格:" + str(max(gaSemScore[bestCom[0]],CNIL)) + " 重み:" + str(np.sqrt(len(ga))))
    print("ヲ格:" + str(woSemScore[bestCom[1]]) + " 重み:" + str(np.sqrt(len(wo))))
    print("ニ格:" + str(niSemScore[bestCom[2]]) + " 重み:" + str(np.sqrt(len(ni))))
    """

    for i in range(len(bestCom) - 1):
        #print(bestCom[i] ,end = " ")

        luSim = semScores[bestCom[i][1]][bestCom[i][0]]["lu"]
        frSim = semScores[bestCom[i][1]][bestCom[i][0]]["frame"]
        paSim = semScores[bestCom[i][1]][bestCom[i][0]]["parent"]
        frameWordsSim = semScores[bestCom[i][1]][bestCom[i][0]]
        parentWordsSim = semScores[bestCom[i][1]][bestCom[i][0]]
        #print(semScores[bestCom[i][1]][bestCom[i][0]], end = " ")
        #print( kfweight[kakuNum][bestCom[i][1]] )
        s = (luSim*ALPHA + frSim*BETA + paSim*(1-ALPHA-BETA)) #* pow( kfweight[kakuNum][bestCom[i][1]] , 1.0/2 )
        #s = semScores[bestCom[i][1]][bestCom[i][0]] * np.sqrt(kfweight[kakuNum][bestCom[i][1]))
        #s = semScores[bestCom[i][1]][bestCom[i][0]] * np.log10(kfweight[kakuNum][bestCom[i][1]])
        bestCom[i] = (bestCom[i][0], bestCom[i][1], luSim, frSim, paSim, s)

    print(kfweight[kakuNum])
    return (bestCom[-1], bestCom[:-1])


def comAll(kfnames,roleNames,currentComs,allComs,limitedfn):
    #print(kfnames)
    #print(limitedfn)
    #print(roleNames)
    #print(currentComs)
    #print("")
    #kfnamesかelementsNamesがなければ組み合わせ完成
    if len(kfnames) == 1:
        if kfnames[0] == NONETOKEN:
            #print("append")
            #print(currentComs)
            c = currentComs.copy()
            allComs.append(c)
            return
        else:
            return
    #limitedkfがまだあればそこからの組み合わせを使う
    elif len(limitedfn) > 0:
        head = ""

        # ここで試す格のキー（どれでもいいから一個）をとりたい
        # 頭悪そうに見えるけどこれ以外方法があるかわからん
        for k in limitedfn: #kはroleの名前
            head = k


            #limitedfnに含まれるroleがもう使われてるか確認
            exist = False
            for c in currentComs:
                if c[0] == head:
                    exist = True
                    break

            if not exist:
                #print(k)
                for k in limitedfn[head]: #fはk格と対応づくかもしれないrole
                    #print(f)
                    #print(currentComs)
                    #print(roleNames)
                    if k in kfnames:
                        # ガ格は絶対なんかに対応づける
                        #if head == "ガ" and f == "None":
                        #    return

                        #print("ok")
                        #print(k + " " + f)
                        #print(kfnames)
                        #print(k)

                        #格、role、ヒントあり格のリスト全部コピーして使ったやつ削って渡す
                        #print(head)
                        #print(kfnames)
                        kfn = kfnames.copy()
                        #None格はいつも存在していてほしい
                        if k != NONETOKEN:
                            kfn.remove(k)
                        rn = roleNames.copy()
                        #Noneに対応づけた=そのroleは対応づかなかった なので消してもok
                        #if k != NONETOKEN:
                        rn.remove(head)

                        lfn = limitedfn.copy()
                        lfn.pop(head)
                        #currentComsはコピーしなくていい
                        #格がNoneだったら組み合わせに入れない、そのroleは使わなかったことにする
                        if k != NONETOKEN:
                            currentComs.append((head, k))
                        #print(currentComs)
                        #print("limited")
                        comAll(kfn, rn,currentComs, allComs, lfn)
                        if k != NONETOKEN:
                            currentComs.pop(-1)
                        #print(currentComs)

    #limitedkfがなければ全パターン試す
    else:
        k = 0
        #print(kfnames[k])
        for f in roleNames:
            #ガ格は絶対なんかに対応づける
            if kfnames[k] == "ガ" and f == "None":
                #print("ガ格が対応づいてない")
                return

            rns = roleNames.copy()
            #Noneは何回でも使いたいので消さない
            if f != "None":
                rns.remove(f)

            # ここでk以前は見ないことにする これによって格を割り当てる順番が決まる
            # これにより (1,a)(2,b)　と(2,a)(1,b)　みたいなのが生まれるのを防げる
            currentComs.append((f,kfnames[k]))
            #print("free")
            comAll(kfnames[k+1:], rns, currentComs, allComs, limitedfn)
            currentComs.pop(-1)

        #print("prog" + kfnames[k])

def convUkemiReration(reration):
    probability = []
    limited = {}

    for r in reration:
        if r[1] == "ガ":
            probability.append((r[0],"ヲ"))
            probability.append((r[0],"ニ"))
            probability.append((r[0],"ノ"))
        elif r[1] == "ヲ":
            probability.append((r[0],"ガ"))
            probability.append((r[0],"ヲ"))
        elif r[1] == "ニ":
            probability.append((r[0],"ガ"))
            probability.append((r[0],"ニ"))

        elif r[1] == "連":
            probability.append((r[0], "ガ"))
            probability.append((r[0], "ヲ"))
            probability.append((r[0], "ニ"))
            probability.append((r[0], "デ"))
        else:
            #ガ、ヲ、ニ格と連体修飾以外は見ない
            continue

    #print(probability)
    return probability