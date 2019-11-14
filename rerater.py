import fnextracter as fnex
import kfextracter as kfex
import executeCommand as ec
import numpy as np
import os

Ne = 3
CNIL = 0.0
KFTOPN = 100

NONETOKEN = "None"

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


def calcscore2(kframe, elements, model, kakuNum, reration ):

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

    n = 0
    #格フレームの用例の単語ベクトルの平均をとる
    for i in yorei[kakuNum]:
        avr = np.zeros(len(model["は"]))
        for j in range(min(len(yorei[kakuNum][i]), KFTOPN)):
            if yorei[kakuNum][i][j] in model:
                # print(ga[i])
                avr += model[yorei[kakuNum][i][j]]
                n += 1
        if n != 0:
            avr = avr / n
        # 用例が一個もなければ勝手に0になる
        kfavrs[i] = avr

    #print(kfavrs)

    #FNフレームの単語ベクトルの平均をとる
    #print(elements)
    elementAvrs = {}
    n = 0
    for el in elements:
        avr = np.zeros(len(model["は"]))
        for i in el[2:]:
            if i in model:
                # print(ga[i])
                avr += model[i]
                n += 1
        if n != 0:
            avr = avr / n
        # 用例が一個もなければ勝手に0になる
        elementAvrs[el[0]] = avr

    elementAvrs[NONETOKEN] = np.zeros(len(model["は"]))

    #print(elementAvrs.keys())

    semScores = {}
    #全組み合わせの類似度を計算しておく
    for i in kfavrs:
        l = np.linalg.norm(kfavrs[i])
        sems = {}
        for j in elementAvrs:
            if np.linalg.norm(elementAvrs[j]) > 0 and l > 0:
                s = np.dot(kfavrs[i],elementAvrs[j]) / (l * np.linalg.norm(elementAvrs[j]))
                sems[j] = s
            else:
                sems[j] = 0.0

        semScores[i] = sems

    #print(semScores)

    # rerationにヒントがあるか確認する　あればそれを使う
    # 一対一で選択肢がないものを全部currenComsに入れる
    guaranteed = []  # 一対一で確定したもの
    # この辞書に入ってたら選択肢が絞られるやつ
    limitedkf = {}
    limitedfn = {}
    # 格とelementに対してgivenに何回ずつ入ってたかを確認する

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
    elems = []
    for i in kfavrs:
        # 必須格かどうかはとりあえず置いておいて全部使う
        # 必須格じゃないやつにroleが対応づいたぞっていうrelationがきた時だるいから
        #print(i)
        if i[0] == '@':
            i = i[1:]
        exist = False
        #確定してる格は使わない
        for g in guaranteed:
            if i == g:
                exist = True
                break

        if not exist:
            kfnames.append(i)

    # guaranteedにその格フレームには含まれていない格が入ってることがあるのでそれを消す
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
    for i in elements:
        #意味役割はCoreだけ見る
        if i[1] == "Core":
            elems.append(i[0])
    elems.append(NONETOKEN)

    #確定してるやつをrole名前リストから削除
    for g in guaranteed:
       #print(g)
        if g[0] in elems:
            elems.remove(g[0])
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
    print("element: ", end="")
    print(elems)
    print("格解析結果: ", end="")
    print(reration)
    print("確定したペア: ", end="")
    print(guaranteed)
    print("ヒントのあるペア: ", end="")
    print(limitedkf)
    allCom = []
    comAll(kfnames, elems, guaranteed, allCom, limitedkf)

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

            s = semScores[p[1]][p[0]] #* pow( int(kfweight[kakuNum][p[1]]) , 1.0/3)
            #s = semScores[p[1]][p[0]] * np.sqrt(int(kfweight[kakuNum][p[1]]))
            #s = semScores[p[1]][p[0]] * np.log10(int(kfweight[kakuNum][p[1]]))
            score += s


        c.append(score)
        #print(c)

    #
    sortedCom = sorted(allCom, key=lambda x: x[-1], reverse=True)

    bestCom = sortedCom[0]
    #print(bestCom)

    """
    print('最良組み合わせ ガ格:' + elems[bestCom[0]] + 'ヲ格:' + elems[bestCom[1]] + 'ニ格:' + elems[bestCom[2]])
    print("ガ格:" + str(max(gaSemScore[bestCom[0]],CNIL)) + " 重み:" + str(np.sqrt(len(ga))))
    print("ヲ格:" + str(woSemScore[bestCom[1]]) + " 重み:" + str(np.sqrt(len(wo))))
    print("ニ格:" + str(niSemScore[bestCom[2]]) + " 重み:" + str(np.sqrt(len(ni))))
    """

    for i in range(len(bestCom) - 1):
        #print(bestCom[i] ,end = " ")

        words_s = semScores[bestCom[i][1]][bestCom[i][0]]
        #print(semScores[bestCom[i][1]][bestCom[i][0]], end = " ")
        #print( kfweight[kakuNum][bestCom[i][1]] )
        s = words_s #* pow( int(kfweight[kakuNum][bestCom[i][1]]) , 1.0/3)
        #s = semScores[bestCom[i][1]][bestCom[i][0]] * np.sqrt(int(kfweight[kakuNum][bestCom[i][1]]))
        #s = semScores[bestCom[i][1]][bestCom[i][0]] * np.log10(int(kfweight[kakuNum][bestCom[i][1]]))
        bestCom[i] = (bestCom[i][0], bestCom[i][1], words_s, s)

    print(kfweight[kakuNum])
    return (bestCom[-1], bestCom[:-1])


def comAll(kfnames,roleNames,currentComs,allComs,limitedkf):
    #print(kfnames)
    #print(roleNames)
    #print(currentComs)
    #kfnamesかelementsNamesがなければ組み合わせ完成
    if len(kfnames) == 0:
        #print("append")
        #print(currentComs)
        c = currentComs.copy()
        allComs.append(c)
        return
    #limitedkfがまだあればそこからの組み合わせを使う
    elif len(limitedkf) > 0:
        head = ""

        # ここで試す格のキー（どれでもいいから一個）をとりたい
        # 頭悪そうに見えるけどこれ以外方法があるかわからん
        for k in limitedkf: #kは格の名前
            head = k


            #limitedkfに含まれる格がもう使われてるか確認
            exist = False
            for c in currentComs:
                if c[1] == head:
                    exist = True
                    break

            if not exist:
                #print(k)
                for f in limitedkf[head]: #fはk格と対応づくかもしれないrole
                    #print(f)
                    #print(currentComs)
                    #print(roleNames)
                    if f in roleNames:
                        #print("ok")
                        #print(k + " " + f)
                        #print(kfnames)
                        #print(k)

                        #格、role、ヒントあり格のリスト全部コピーして使ったやつ削って渡す
                        #print(head)
                        #print(kfnames)
                        kfn = kfnames.copy()
                        kfn.remove(head)
                        rn = roleNames.copy()
                        if f != NONETOKEN:
                            rn.remove(f)

                        lkf = limitedkf.copy()
                        lkf.pop(head)
                        #currentComsはコピーしなくていい
                        currentComs.append((f, head))
                        #print(currentComs)
                        comAll(kfn, rn,currentComs, allComs, lkf)
                        currentComs.pop(-1)
                        #print(currentComs)

    #limitedkfがなければ全パターン試す
    else:
        k = 0
        #print(kfnames[k])
        for f in roleNames:
            #ガ格は絶対なんかに対応づける
            if kfnames[k] == "ガ" and f == "None":
                return

            rns = roleNames.copy()
            #Noneは何回でも使いたいので消さない
            if f != "None":
                rns.remove(f)

            # ここでk以前は見ないことにする これによって格を割り当てる順番が決まる
            # これにより (1,a)(2,b)　と(2,a)(1,b)　みたいなのが生まれるのを防げる
            currentComs.append((f,kfnames[k]))
            comAll(kfnames[k+1:], rns, currentComs, allComs, limitedkf)
            currentComs.pop(-1)


        #print("prog" + kfnames[k])


