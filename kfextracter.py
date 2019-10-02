import re

#見出し取り出す
#読みが複数あるとき正しく動作しない
def ExtractMidashi(frameFileName):

    verbs=[]

    #lexunit列挙
    frame = open(frameFileName, "r", encoding='euc-jp', errors='ignore')
    contents = frame.read()
    #print(contents)
    midashiExtracter = re.compile('<見出し>.*/')
    m = midashiExtracter.search(contents)
    if m == None:
        return -1
    #print(matchOB)

    me = re.compile('[^\x01-\x7E]+?/')
    v = me.findall(m.group()[5:])
    #print(v)
    if v == None:
        return -1

    midashi = v[0][:-1]
    for i in range(1,len(v)):
        #print(midashi)
        midashi = midashi + '+' + v[i][:-1]
    return midashi

def ExYoreiSupport(lines):#たぶんlinesは1行しか入ってない
    yorei = []

    wordExtracter = re.compile(' .*?/.*?:')
    singleWordExtracter = re.compile('.*?/')

    for line in lines:
        # 最初の< >を削る　この中にスペースが入ってるから最初の単語が "@ガ格> 雲/" みたいになる
        for i in range(len(line)):
            if line[0] == '>':
                break
            line = line[1:]

        words = wordExtracter.findall(line)
        # print(words)
        for word in words:
            pos = word.find('+')
            if pos == -1:#最後じゃなくてないって意味
                elem = singleWordExtracter.search(word)
                yorei.append(elem.group()[1:-1])

            else:
                word1 = word[:pos]
                word2 = word[pos:]
                # print(word1)
                # print(word2)

                elem1 = singleWordExtracter.search(word1)
                elem2 = singleWordExtracter.search(word2)

                yorei.append(elem1.group()[1:-1] + "+" + elem2.group()[1:-1])


        # print(yorei)
    return yorei


def ExtractYorei(frameFileName):

    yorei=[]

    #lexunit列挙
    frame = open(frameFileName, "r", encoding='euc-jp', errors='ignore')
    contents = frame.read()
    #print(contents)

    frameExtracter = re.compile("<見出し>.*?</見出し>", re.MULTILINE | re.DOTALL)

    frames = frameExtracter.findall(contents)

    #print(frames)

    for i in range(len(frames)):

        yoreiInFrame = []

        gaExtracter = re.compile('<格.*ガ格>.*')
        ga = gaExtracter.findall(frames[i])
        niExtracter = re.compile('<格.*ニ格>.*')
        ni = niExtracter.findall(frames[i])
        woExtracter = re.compile('<格.*ヲ格>.*')
        wo = woExtracter.findall(frames[i])
        """
        for g in ga:
            print(g)
        for n in ni:
            print(n)
        for w in wo:
            print(w)
        """
        yorei.append((ExYoreiSupport(ga), ExYoreiSupport(wo), ExYoreiSupport(ni)))

    return yorei


def getFrameNum(frameFileName):

    yorei=[]

    #lexunit列挙
    frame = open(frameFileName, "r", encoding='euc-jp', errors='ignore')
    contents = frame.read()
    #print(contents)

    frameExtracter = re.compile("<見出し>.*?</見出し>", re.MULTILINE | re.DOTALL)

    frames = frameExtracter.findall(contents)

    return len(frames)