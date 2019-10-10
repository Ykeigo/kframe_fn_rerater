

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
"""
import fnextracter
IDs = fnextracter.ExtractID('./framenet/frames/Come_together.xml')
print(IDs)

elements = []
for i in IDs:
    print(str(i))
    a = fnextracter.ExtractElements('./framenet/lu/lu'+str(i)+'.xml')
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

