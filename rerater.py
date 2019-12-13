import fnextracter as fnex
import kfextracter as kfex
import executeCommand as ec
import numpy as np
import os

# 意味役割はCoreだけ見る、ただし格解析の結果対応づくことが明示されていた場合はCoreでなくとも使う
# 格はガ格より多く使われている格だけ使う（検討の余地）

Ne = 3
CNIL = 0.0
KFTOPN = 20

ALPHA = 0.7
BETA = 0.1

# NORERATION = 0.25 #単語ベクトルの平均の関連度ならこんなもんだけど単語ベクトルの関連度の平均だとこれはでかい
NORERATION = 0.1
NONETOKEN = "None"
SAMEKAKU = 0.6

def setALPHABETA(a,b):
    global ALPHA
    ALPHA = a
    global BETA
    BETA = b

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

def calcscore2(kframe, elements, model, kakuNum, relation, ukemiRelation ):
    print(elements)
    #print(elements)

    ###################
    #  mainから渡すやつ #
    ###################
    yoreis = kfex.ExtractYorei(kframe)
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

    #nihe = ["ニ","ヘ"]

    # 格フレームの用例のベクトルの平均を計算しておく
    for kaku in yoreis[kakuNum]:
        n = 0
        kfmichigo[kaku] = False
        avr = np.zeros(len(model["は"]))

        #if kaku not in yoreis[kakuNum]:
        #    continue

        for i in range(min(len(yoreis[kakuNum][kaku]), KFTOPN)):
            if yoreis[kakuNum][kaku][i][0] in model:
                # print(ga[i])
                v = model[yoreis[kakuNum][kaku][i][0]]
                avr += v / np.linalg.norm(v) * yoreis[kakuNum][kaku][i][1]
                n += yoreis[kakuNum][kaku][i][1]
            else:
                kfmichigo[i] = True
        if n != 0:
            avr = avr / n
        # 用例が一個もなければ勝手に0になる
        kfavrs[kaku] = avr
        kfValidWordNum[kaku] = n

    # ヘとニを類似度によっては合成する
    if "ニ" in kfavrs and "ヘ" in kfavrs:
        # kfValidWordNum["ニ"]
        sim = 0
        if kfValidWordNum["ニ"] > 0 and kfValidWordNum["ヘ"] > 0:  # 語彙にない単語だけだと平均ベクトルが0になって0で割ることになる
            sim = np.dot(kfavrs["ニ"], kfavrs["ヘ"]) / (np.linalg.norm(kfavrs["ニ"]) * np.linalg.norm(kfavrs["ヘ"]))
            print("ニ格とヘ格の類似度:" + str(sim))

        if sim > SAMEKAKU:
            kfweight[kakuNum]["ニ"] += kfweight[kakuNum]["ヘ"]
            kfavrs["ニ"] = (kfavrs["ニ"] * kfValidWordNum["ニ"] + kfavrs["ヘ"] * kfValidWordNum["ヘ"]) / (kfValidWordNum["ニ"] + kfValidWordNum["ヘ"])

            yoreis[kakuNum].pop("ヘ")

    #print(kfavrs)

    # rerationにヒントがあるか確認する　あればそれを使う
    # 一対一で選択肢がないものを全部currenComsに入れる
    guaranteed = []  # 一対一で確定したもの
    # この辞書に入ってたら選択肢が絞られるやつ
    limitedkf = {}
    limitedfn = {}
    # 格とelementに対してgivenに何回ずつ入ってたかを確認する

    # ダブり削除
    relation = list(set(relation))

    #guaranteedを作るために一回isGuaranteedする
    r = isGuaranteed(relation)
    guaranteed = r[0]
    limitedkf = r[1]
    limitedfn = r[2]

    convertedUkemi = convUkemiRelation(ukemiRelation)
    convertedUkemi = list(set(convertedUkemi))
    #guaranteedがあるので受け身文のreration削れる
    con = convertedUkemi.copy()
    for i in con:
        # 同じ意味役割を使う関係を削除する
        if i in guaranteed:
            convertedUkemi.pop(i)
        #同じ格を使う関係を削除する
        else:
            for j in guaranteed:
                if guaranteed[j] == con[i]:
                    convertedUkemi[i].remove(guaranteed[j])
    print(convertedUkemi)
    relation.extend(convertedUkemi)
    relation = set(list(relation))

    #limitedkfとlimitedfn作るためにもっかいisGuaranteedする
    r = isGuaranteed(relation)
    #受け身文で確定することはないはずなのguaranteedの部分は使わない
    #guaranteed.extend(r[0])
    limitedkf = r[1]
    limitedfn = r[2]

    # guaranteed = 確定
    # limitedkf,limitedfnに入ってる = しぼれる
    # ↑に入ってない = 全部試す

    #格フレームの格の名前リストを作る
    kfnames = []
    elementNames = []

    if "ガ" not in kfweight[kakuNum]:
        print("frame" + str(kakuNum) + " にはガ格がありません")

    for i in yoreis[kakuNum]:
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
            limitedfn.pop(i)

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

    simScores = {}
    #全組み合わせの類似度を計算しておく
    simLU = calcSimScores(elements["lu"], kfavrs, model)
    simFrame = calcSimScores(elements["frame"], kfavrs, model)
    simParent = calcSimScores(elements["parent"], kfavrs, model)

    for kaku in yoreis[kakuNum]:
        print(kaku, end = "      ")
    print("")
    for role in simLU:
        print(role, end = " ")
        for kaku in simLU[role]:
            print(simLU[role][kaku], end = " ")
        print("")

    for role in simLU:
        scores = {}
        #print(role)
        for kaku in simLU[role]:
            s3 = {}
            s3["lu"] = simLU[role][kaku][0]
            #print("lu "+role+" "+kaku, end=" ")
            #print(simLU[role][kaku])
            if role in simFrame:
                s3["frame"] = simFrame[role][kaku][0]
                #print("frame " + role+" "+kaku,end=" ")
                #print(simFrame[role][kaku])
            else:
                s3["frame"] = 0.0
            if role in simParent:
                s3["parent"] = simParent[role][kaku][0]
                #print("parent " + role+" "+kaku,end=" ")
                #print(simParent[role][kaku])
            else:
                s3["parent"] = 0.0

            scores[kaku] = s3

        simScores[role] = scores


    #print(simScores)

    #print(kfmichigo)
    #print(fnmichigo)
    print("使う格: ", end="")
    print(kfnames)
    print("element: ", end="")
    print(elementNames)
    print("このluの単語群間の類似度: ")
    #print(yoreis)
    print("     ", end = "")
    for i in elements["lu"]:
        if i[1] == "Core" or len(i) >= 3:
            print(i[0], end = " ")
    print("")
    print("     ", end = "")
    for i in elements["lu"]:
        if i == NONETOKEN:
            continue

        if i[1] == "Core" or len(i) >= 3:
            if len(i) >= 3:
                print(i[2], end = " ")
            else:
                print("なし", end=" ")
    print("")
    for i in kfnames:
        if i == NONETOKEN:
            continue
        if "ガ" in kfweight[kakuNum] and kfweight[kakuNum][i] < kfweight[kakuNum]["ガ"]:
            continue
        #格の名前表示
        print(i, end = " ")
        if len(i) == 1:
            print("  ", end = "")
        #類似度表示
        for j in elements["lu"]:
            #print(simScores[j[0]])
            if j[0] == NONETOKEN:
                continue
            if j[1] == "Core" or len(j) >= 3:
                #print()
                print('{:.5f}'.format(simScores[j[0]][i]["lu"]), end = " ")
        print("")

    print("格解析結果: ", end="")
    print(relation)
    print("格解析結果（受け身）: ", end="")
    print(ukemiRelation)
    print("確定したペア: ", end="")
    print(guaranteed)
    print("ヒントのあるペア: ", end="")
    print(limitedkf)
    print(limitedfn)
    allCom = []

    # 全組み合わせ作る
    #print(guaranteed)
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

            s1 = simScores[p[0]][p[1]]["lu"]
            s2 = simScores[p[0]][p[1]]["frame"]
            s3 = simScores[p[0]][p[1]]["parent"]
            """
            certainty = 0.8
            if (p[0],p[1]) in guaranteed:
                certainty = 1.0
            elif p[0] in limitedfn and p[1] in limitedfn[p[0]]:
                certainty = 0.9
            """
            #s = simScores[p[1]][p[0]] * np.sqrt(int(kfweight[kakuNum][p[1]]))
            #s = simScores[p[1]][p[0]] * np.log10(int(kfweight[kakuNum][p[1]]))
            # score += s1*ALPHA + s2*(1-ALPHA) #max(s1 ,s2 * ALPHA) #* pow( int(kfweight[kakuNum][p[1]]) , 1.0/2)
            # score += s1 * ALPHA + s2 * BETA + s3 * (1-ALPHA-BETA)
            score += max(s1 ,s2 * ALPHA) #* certainty

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

        luSim = simScores[bestCom[i][0]][bestCom[i][1]]["lu"]
        frSim = simScores[bestCom[i][0]][bestCom[i][1]]["frame"]
        paSim = simScores[bestCom[i][0]][bestCom[i][1]]["parent"]
        """
        certainty = 0.8
        if (bestCom[i][0], bestCom[i][1]) in guaranteed:
            certainty = 1.0
        elif bestCom[i][0] in limitedfn and bestCom[i][1] in limitedfn[bestCom[i][0]]:
            certainty = 0.9
        """
        #print(simScores[bestCom[i][0]][bestCom[i][1]], end = " ")
        #print( kfweight[kakuNum][bestCom[i][1]] )
        #s = luSim*ALPHA + frSim*(1-ALPHA)#max(luSim, frSim*ALPHA) #* pow( kfweight[kakuNum][bestCom[i][1]] , 1.0/2 )
        s = max(luSim, frSim*ALPHA) #* certainty
        # s = luSim*ALPHA + frSim*(1-ALPHA)
        # s = (luSim*ALPHA + frSim*BETA + paSim*(1-ALPHA-BETA)) #* pow( kfweight[kakuNum][bestCom[i][1]] , 1.0/2 )
        #s = simScores[bestCom[i][0]][bestCom[i][1]] * np.sqrt(kfweight[kakuNum][bestCom[i][1]))
        #s = simScores[bestCom[i][0]][bestCom[i][1]] * np.log10(kfweight[kakuNum][bestCom[i][1]])
        bestCom[i] = (bestCom[i][0], bestCom[i][1], luSim, frSim, paSim, s)

    print(kfweight[kakuNum])
    return (bestCom[-1], bestCom[:-1])


def calcSimScores(elements, kfavrs, model):
    simScores = {}

    #print(elements)
    if (NONETOKEN, "Core") not in elements:
        elements.append((NONETOKEN, "Core"))

    for role in elements:
        scores = {}

        if role[1] != "Core" and len(role) < 3:
            continue
        for kaku in kfavrs:
            maxSim = 0
            maxElement = NONETOKEN
            #NONETOKENなら関連度は0でいい？
            if len(role) < 3:#and role[0] != NONETOKEN:
                maxSim = 0.1
            for elem in role[2:]:
                #print("elem = " + elem)
                # 語彙になければそのelementは使わない　全部あるはずだけど
                if elem not in model:
                    print(elem + " not in model")
                    continue
                sim = 0
                n = 0
                # そのelementと格フレームの全部の用例の類似度計算して足す
                """
                for i in range(min(len(yoreis[kaku]),KFTOPN)):
                    # 語彙になければその用例は使わない
                    if yoreis[kaku][i][0] not in model:
                        continue
                    # 単語動詞の類似度計算
                    #print(elem + " " + yoreis[kaku][i])
                    sim += model.similarity(elem,yoreis[kaku][i][0])*yoreis[kaku][i][1]
                    n += yoreis[kaku][i][1]
                # 格フレームの用例との類似度を平均する
                if n > 0:
                    sim = sim / n
                # None以外は関連度0じゃないようにしておく
                else:
                    sim = NORERATION
                # 類似度高ければそのelementの類似度を使う
                if sim > maxSim:
                    maxElement = elem
                    maxSim = sim
                """
                sim = np.dot(model[elem], kfavrs[kaku]) / np.linalg.norm(model[elem])
                if sim > maxSim:
                    maxElement = elem
                    maxSim = sim

            scores[kaku] = (maxSim, maxElement)
            #print(scores[kaku])

        simScores[role[0]] = scores

    return simScores

def isGuaranteed(relation):
    limitedkf = {}
    limitedfn = {}
    guaranteed = []

    for g in relation:
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

    return (guaranteed, limitedkf, limitedfn)


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

def convUkemiRelation(relation):
    probability = []

    for r in relation:
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

        elif r[1] == "連体":
            probability.append((r[0], "ガ"))
            probability.append((r[0], "ヲ"))
            probability.append((r[0], "ニ"))
            # デ格は河原さんの論文では必要リストに入ってなかった
            # probability.append((r[0], "デ"))
        else:
            # ガ、ヲ、ニ格と連体修飾以外は見ない
            continue

    #print(probability)
    return probability