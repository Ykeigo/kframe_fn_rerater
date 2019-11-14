
"""
#単語ベクトルの平均の類似度ってほんとに単語群の類似度になるの？
import gensim
import numpy as np

embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')

kuruma = embedding.most_similar("車", topn=100)

densya = embedding.most_similar("電車", topn=100)

kare = embedding.most_similar("カレー", topn=100)

#print(kuruma)

kurumav = np.zeros(len(embedding["は"]))
densyav = np.zeros(len(embedding["は"]))
karev = np.zeros(len(embedding["は"]))

for i in range(100):
    kurumav += embedding[kuruma[i][0]]
    densyav += embedding[densya[i][0]]
    karev += embedding[kare[i][0]]

print("kurumav len = " + str(np.linalg.norm(kurumav)))
print("densyav len = " + str(np.linalg.norm(densyav)))
print("karev len = " + str(np.linalg.norm(karev)))

print("kurumav densyav similarity = " + str(np.dot(kurumav, densyav)))
print("kurumav karev similarity = " + str(np.dot(kurumav, karev)))
print("densyav karev similarity = " + str(np.dot(densyav, karev)))
"""

"""
import sys
import fnextracter

args = sys.argv
path = args[1]
verb = args[2]
ID = fnextracter.searchSentence_Verb(path, verb)

print(ID)
reration = []


slash = 0
while slash < 2:
    path = path[:-1]
    if path[-1] == '/':
        slash += 1

if ID != None:
    reration = fnextracter.getRoleReration(verb, path+'lu/lu'+ID+'.xml', "/home/oyanagi/rerater/luReibuns")
print(reration)
"""
"""
import sys
import kfextracter as kf

args = sys.argv
print(kf.ExtractMidashi(args[1]))
y = kf.ExtractYorei(args[1])
print(y)
"""
"""
import fnextracter as fn

print(fn.getRoleReration("振る舞う", "20171117/lu/lu24919.xml", "/home/oyanagi/rerater/luReibuns"))
"""

"""
#import kfextracter
#print(kfextracter.ExtractYorei('kframe/web70-201101-068476.formatted','ni'))

#import gensim

#subword使ってない↓
#model = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')

#print(model['車'])
#print(type(model['車']))
"""
"""
import numpy as np
a = np.array([1,2,3])
print(len(a))
"""
"""
import kfextracter as kf

i = kf.getYoreiNum('075241.kf')
for j in i:
    print(j)
"""

import fnextracter as fn
a = fn.getUkemiReration("振る舞う","20171117/lu/lu24919.xml", "lu2Reibuns")
print(a)