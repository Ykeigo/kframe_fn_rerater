import re
import os

#見出し取り出す
#読みが複数あるとき正しく動作しない
def ExtractMidashi(frameFileName):

    verbs=[]

    #lexunit列挙
    frame = open(frameFileName, "r")
    contents = frame.read()
    frame.close()
    #print(contents)
    midashiExtracter = re.compile('<見出し>.*/')
    m = midashiExtracter.search(contents)

    print(m)
    if m == None:
        return -1

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

def ExYoreiSupport(line):#たぶんlinesは1行しか入ってない
    yorei = []

    wordExtracter = re.compile(' .*?/.*?:')
    singleWordExtracter = re.compile('.*?/')
    #print("line")
    #print(line)
    # 最初の< >を削る　この中にスペースが入ってるから最初の単語が "@ガ格> 雲/" みたいになる
    for i in range(len(line)):
        if line[0] == '>':
            break
        line = line[1:]
    #print(line)
    words = wordExtracter.findall(line)
    #print(words)
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

    #print("hello")
    if not os.path.exists(frameFileName):
        print(frameFileName+"は存在しません")
        return yorei

    frame = open(frameFileName, "r")
    contents = frame.read()
    #print(contents)
    frame.close()

    frameExtracter = re.compile("<見出し>.*?</見出し>", re.MULTILINE | re.DOTALL)

    frames = frameExtracter.findall(contents)

    #print(frames)

    for i in range(len(frames)):

        yoreiInFrame = {}

        kakuLineExtracter = re.compile('<格 [ァ-ヴ,@]*?格 [0-9]*?>.*')
        kakuline = kakuLineExtracter.findall(frames[i])
        """
        for g in ga:
            print(g)
        for n in ni:
            print(n)
        for w in wo:
            print(w)
        """
        kakuExtracter = re.compile('<格.*?格')

        for k in kakuline:
            kaku = kakuExtracter.search(k)
            kaku = kaku.group()[3:-1]
            #print(kaku)
            #print(k)
            if kaku[0] == '@':
                kaku = kaku[1:]

            yoreiInFrame[kaku] = ExYoreiSupport(k)

        yorei.append(yoreiInFrame)

    return yorei


def getFrameNum(frameFileName):

    yorei=[]

    #lexunit列挙
    frame = open(frameFileName, "r")
    contents = frame.read()
    #print(contents)

    frameExtracter = re.compile("<見出し>.*?</見出し>", re.MULTILINE | re.DOTALL)

    frames = frameExtracter.findall(contents)

    return len(frames)


def getYoreiNum(frameFileName):

    # 格をインデックスとする辞書 の フレーム番号をインデックスとするリスト を返す
    yoreiNums = []

    #lexunit列挙
    frame = open(frameFileName, "r")
    contents = frame.read()
    #print(contents)

    kakuExtracter = re.compile('<格 [ァ-ヴ,@]*?格 [0-9]*?>')

    kakuNameExtracter = re.compile('<格.*?格')
    numExtracter = re.compile('[0-9]*?>')
    frameExtracter = re.compile("<見出し>.*?</見出し>", re.MULTILINE | re.DOTALL)
    
    frames = frameExtracter.findall(contents)

    #フレームの塊全部確認
    for frame in frames:
        yoreiNum = {}

        kaku = kakuExtracter.findall(frame)
        #print(kaku)
        #格全部確認
        for k in kaku:
            name = kakuNameExtracter.search(k)
            num = numExtracter.search(k)

            #print(name.group())
            #print(num.group())

            #あればいらんとこ全部削って返す
            if name != None and num != None:
                name = name.group()[3:-1]
                num = num.group()[:-1]
                if name[0] == '@':
                    name = name[1:]

                yoreiNum[name] = num

            elif name != None:
                print("以下の格の用例数取得失敗")
                print(name.group())
            elif num != None:
                print("以下の用例数の格の名前の取得失敗")
                print(num.group())

        yoreiNums.append(yoreiNum)

    return yoreiNums
