import fnextracter as fe
import sys
import pathMover as pm
import csv
import rerater
import kfextracter as ke
import gensim

args = sys.argv
print(args[1])

embedding = gensim.models.KeyedVectors.load_word2vec_format("./knownEmbedding.vec")

indexFile = open(args[2], "r")
indexReader = csv.reader(indexFile)

FNscores = []

midashi = ke.ExtractMidashi(args[1])
for row in indexReader:
    # print(f.name)
    score = rerater.calcScore(midashi, [(midashi,1.0)], row[1:], embedding)
    if score > 0:
        FNscores.append((row[0], score))

FNscores.sort(key=lambda x: x[1], reverse=True)
indexFile.close()

print(FNscores)

for f in FNscores:
    #print(fe.ExtractFrame(args[1]))

    print(fe.ExtractFrame("20171117/lu/"+f[0]))
    framePath = "20171117/frame/" + fe.ExtractFrame("20171117/lu/"+f[0]) + ".xml"
    exist = False
    """
    elements = fe.ExtractElements_Frame(framePath)
    for i in elements:
        if len(i) > 2:
            exist = True
            print(i)
    #print()
    """
    r = fe.getRoleRelation(midashi,"20171117/lu/"+f[0],"./lu2Reibuns",useFrame=False)
    print(r)
    r= fe.getRoleRelation(midashi,"20171117/lu/"+f[0],"./lu2Reibuns",ukemi=True,useFrame=False)
    print(r)
    rf = fe.getRoleRelation(midashi,"20171117/lu/"+f[0],"./lu2Reibuns")
    print(rf)
    rf = fe.getRoleRelation(midashi,"20171117/lu/"+f[0],"./lu2Reibuns",ukemi=True)
    print(rf)


print("")

