"""
import re

lexUnitExtracter = re.compile('<lexUnit.*>')
lexLines = lexUnitExtracter.findall('<lexUnit status="Created" POS="N" name="発明.n" ID="21859" lemmaID="25643" cDate="08/02/2010 11:10:50 EDT Mon">')
if lexLines:
    print(lexLines)
    dotvExtracter = re.compile('\.v')

    if lexLines:
        #print(matchOB)

        #タグからlemmaIDを取り出す
        for lexUnitLine in lexLines:
            isVerb = dotvExtracter.findall(lexUnitLine)
            if isVerb:
                print(isVerb)
"""
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
import kfextracter as ke

print(ke.ExtractYorei("kframe/041770.kf")[0][2])
"""
"""
import rerater
import gensim

embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')


# その格フレームの喚起語を取得
midashi = kfex.ExtractMidashi(args[1])
print("見出し："+midashi)
if midashi not in embedding:
    print("midashi " + midashi + " not in vocabulary")
    print("program terminated")
    exit()

midashiMostSimilars = embedding.most_similar(midashi, topn=Nt)

#その単語自身を追加
midashiMostSimilars.append(midashi)


rerater.calcScore()
"""
"""
import rerater
import gensim


embedding = gensim.models.KeyedVectors.load_word2vec_format('./model.vec')

score = rerater.calcscore2("../formatted.merge/web70-201101-053033.formatted", "../jfn/frame/Theft.xml", embedding, 0)

print(score)
"""
import sys
import fnextracter

args = sys.argv
path = args[1]
IDs = fnextracter.ExtractID(path)
Calls = fnextracter.ExtractVerb(path)
print(IDs)

elements = []

slash = 0
while slash < 2:
    path = path[:-1]
    if path[-1] == '/':
        slash += 1

for i in IDs:
    print(str(i))
    a = fnextracter.ExtractElements(path+'lu/lu'+str(i)+'.xml')
    for j in a:
        exist = False
        for k in range(len(elements)):
            if elements[k][0] == j[0]:
                elements[k].extend(j[2:])
                exist = True
        if exist == False:
            elements.append(j)
print(Calls)
print(elements)

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

