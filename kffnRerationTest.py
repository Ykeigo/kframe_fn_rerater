import rerater


kfnames = ["ガ","ト", "ニ", "ヘ", "デ", "カラ"]
roleNames =["Area","Direction","Goal","Path","Theme","Source","None"]

reration = [('Theme', 'ガ'), ('Goal', 'ヘ'), ('Goal', 'ニ'), ('Path', 'ヲ'), ('Carrier', 'デ'), ('Direction', 'ニ')]


"""
kfnames = ['ガ', 'ト', 'デ', 'カラ', 'ヨリ', 'マデ', 'ヘ']
roleNames =['Agent', 'Entity', "None"]


reration = [('Content', 'ニ')]
"""


guaranteed = []  # 一対一で確定したもの
# この辞書に入ってたら選択肢が絞られるやつ
limitedkf = {}
limitedfn = {}
# 格とelementに対してgivenに何回ずつ入ってたかを確認する

for g in reration:
    #print(g[0])
    if g[1] in limitedkf:
        l = limitedkf[g[1]].copy()
        #print(type(l))
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
    #print(k)
    if len(limitedkf[k]) == 1 and len(limitedfn[limitedkf[k][0]]) == 1:
        guaranteed.append((limitedkf[k][0],limitedfn[limitedkf[k][0]][0]))
        limitedfn.pop(limitedkf[k][0])
        limitedkf.pop(k)

for l in limitedkf:
    limitedkf[l].append("None")

allcom = []
print(allcom)
print(guaranteed)
print(limitedkf)
print(limitedfn)
rerater.comAll(kfnames,roleNames, guaranteed, allcom, limitedkf)

for i in allcom:
    print(i)
