import re
import executeCommand as ec
import os

#動詞取り出す
def ExtractVerb(frameFileName):

    verbs=[]

    #lexunit列挙
    if not os.path.exists(frameFileName):
        print(frameFileName+"は存在しません")
        return verbs

    frame = open(frameFileName, "r")
    contents = frame.read()
    frame.close()

    lexUnitExtracter = re.compile('<lexUnit.*>')
    lexLines = lexUnitExtracter.findall(contents)

    if lexLines:
        #print(matchOB)
        verbExtracter = re.compile('[^\x01-\x7E]+')
        for lexUnitLine in lexLines:

            v = verbExtracter.search(lexUnitLine)
            verbs.append(v.group())


    return verbs

#ID取り出す

def ExtractID(frameFileName):

    LUIDs=[]

    #lexunit列挙
    if not os.path.exists(frameFileName):
        print(frameFileName+"は存在しません")
        return LUIDs
    frame = open(frameFileName, "r")
    contents = frame.read()
    frame.close()

    lexUnitExtracter = re.compile('<lexUnit.*>')
    lexLines = lexUnitExtracter.findall(contents)

    numExtracter = re.compile('[0-9]+')
    lexIDExtracter = re.compile(' ID="[0-9]*"')
    # 喚起語が動詞のやつ以外は性質違うけど格対応見ないなら使ってもいいんじゃね？
    dotvExtracter = re.compile('\..')

    if lexLines:
        #print(matchOB)

        #タグからlemmaIDを取り出す
        for lexUnitLine in lexLines:
            isVerb = dotvExtracter.findall(lexUnitLine)
            if isVerb:
                IDTags = lexIDExtracter.findall(lexUnitLine)
                #print(IDTags)
                for tag in IDTags:
                    n = numExtracter.search(tag)
                    LUIDs.append(n.group())


    return LUIDs

def extractDaihyo(line):
    headExtracter = re.compile("<主辞代表表記.*?>")
    head = headExtracter.search(line)
    head2Extracter = re.compile("<主辞’代表表記.*?>")
    head2 = head2Extracter.search(line)

    repExtracter = re.compile("s/\/[^\+]+//g")

    if head2 != None:

        # print(head2.group())
        wordSimbol = head2.group()[9:]  # <主辞’代表表記:の次の文字から見たい

        # print(wordSimbol)
        word = ''
        add = True
        for i in range(len(wordSimbol)):
            if wordSimbol[i] == '/':
                add = False
                continue
            elif wordSimbol[i] == '+':
                add = True
            if add:
                word = word + wordSimbol[i]

            # print(word)

        return word
    elif head != None:
        # print(head.group())
        word = ''
        wordSimbol = head.group()[8:]  # <主辞代表表記:の次の文字から見たい

        # print(wordSimbol)
        word = ''
        add = True
        for i in range(len(wordSimbol)):
            if wordSimbol[i] == '/':
                add = False
                continue
            elif wordSimbol[i] == '+':
                add = True
            if add:
                word = word + wordSimbol[i]

            # print(word)

        return word

    return None

#文から主表表記（主辞’代表表記があればそっち優先）を取り出す
def extractHead(str):
    res = ec.res_cmd( 'echo "' + str + '" | juman | knp -tab -dpnd ')
    all = ''
    for line in reversed(res):
        daihyo = extractDaihyo(line)
        if daihyo:
            return daihyo

    return None

#例文のエレメント取り出す
#3つ目の要素が例文中の単語
#reibun=は何個目の例文か（0スタート）
def ExtractElements(LUFileName, reibun=-1):
    elements=[]
    #エレメントのname,typeを取り出す

    #<frame>の中の<FE>を見る
    if not os.path.exists(LUFileName):
        print(LUFileName+"は存在しません")
        return elements

    frame = open(LUFileName, "r")
    contents = frame.read()
    frame.close()

    frameTagExtracter = re.compile('<frame>.*</frame>', re.MULTILINE|re.DOTALL)

    FETagExtracter = re.compile('<FE.*/>')
    typeExtracter = re.compile('type=".+?"')
    nameExtracter = re.compile('name=".+?"')

    sentenceTagExtracter = re.compile('<sentence.*?</sentence>', re.MULTILINE|re.DOTALL)
    textExtracter = re.compile('<text>.+')
    labelExtracter = re.compile('<label .*/>')
    endExtracter = re.compile('end="[0-9]+')
    startExtracter = re.compile('start="[0-9]+')


    frameTag = frameTagExtracter.finditer(contents)

    if frameTag:
        # タグからFEタグを取り出す
        # <frame>は一個しかないはずだからforいらんかも

        for f in frameTag:
            FEs = FETagExtracter.findall(f.group(0))
            #print(FEs)
            for fe in FEs:
                type = typeExtracter.search(fe)
                name = nameExtracter.search(fe)
                #print(type.group())
                #print(name.group())
                elements.append( [name.group()[6:-1], type.group()[6:-1]] )#<frame　を消すため

    sentences = sentenceTagExtracter.findall(contents)
    #print(sentences)
    #print(elements)
    sentIndex = 0
    for sentenceTag in sentences:
        if reibun != -1 and sentIndex != reibun:
            sentIndex += 1
            continue
        texts = textExtracter.findall(sentenceTag)
        labels = labelExtracter.findall(sentenceTag)
        #print(texts)

        for text in texts:
            text = text[6:]
            for label in labels:
                name = nameExtracter.search(label)
                #print(name.group()[6:-1])
                for e in elements:
                    #print(e[0])
                    if e[0] == name.group()[6:-1]:
                        end = endExtracter.search(label)
                        start = startExtracter.search(label)
                        if end == None or start == None:
                            continue
                        end = end.group()[5:]#end=を消すため
                        start = start.group()[7:]#start=を消すため

                        #空白消してjumanknp型にする
                        nospace = text[int(start):int(end) + 1].replace(" ", "")
                        if len(nospace) == 0:
                            continue

                        #res = ec.res_cmd("echo " + nospace + " | ./han2zen.pl | nkf | juman | knp -dpnd-fast -tab | ./knp2words.sh")
                        #print(nospace)
                        res = extractHead(nospace)
                        #print(nospace)
                        #sprint(res)
                        #parts = res[0].split(" ")
                        #e.append(parts[-1])
                        if res not in e:
                            e.append(res)
        sentIndex += 1
    #print(sentences)

    return elements

def searchLu_Verb(frameFileName, verb):
    ID = '00000'

    # lexunit列挙
    frame = open(frameFileName, "r")
    contents = frame.read()
    frame.close()

    lexUnitExtracter = re.compile('<lexUnit.*>')
    lexLines = lexUnitExtracter.findall(contents)

    numExtracter = re.compile('[0-9]+')
    lexIDExtracter = re.compile(' ID="[0-9]*"')
    nameExtracter = re.compile('name=".*\.v"')

    if lexLines:
        # print(matchOB)

        # タグからlemmaIDを取り出す
        for lexUnitLine in lexLines:
            name = nameExtracter.search(lexUnitLine)
            if not name:
                continue
            #name=　と　.以降を消す
            name = name.group()[6:]
            dot = False
            while len(name) > 0:
                if name[-1] == '.':
                    name = name[:-1]
                    break
                name = name[:-1]
            #print(name)
            name = extractHead(name.replace(" ", ""))

            if name == verb:
                #↓LUID一個しかないだろうしfindallいらなくね
                IDTag = lexIDExtracter.search(lexUnitLine)
                # print(IDTags)
                if IDTag != None:
                    n = numExtracter.search(IDTag.group())
                    ID = n.group()
                break

    return ID

def ExtractReibun(LUFileName):
    elements = []
    #エレメントのname,typeを取り出す

    #<frame>の中の<FE>を見る
    if not os.path.exists(LUFileName):
        print(LUFileName+"は存在しません")
        return elements

    frame = open(LUFileName, "r")
    contents = frame.read()
    frame.close()

    frameTagExtracter = re.compile('<frame>.*</frame>', re.MULTILINE|re.DOTALL)

    FETagExtracter = re.compile('<FE.*/>')
    typeExtracter = re.compile('type="[a-zA-Z]+')
    nameExtracter = re.compile('name="[a-zA-Z]*')

    sentenceTagExtracter = re.compile('<sentence.*?</sentence>', re.MULTILINE|re.DOTALL)
    textExtracter = re.compile('<text.*?</text>', re.MULTILINE|re.DOTALL)


    frameTag = frameTagExtracter.finditer(contents)

    if frameTag:
        # タグからFEタグを取り出す
        # <frame>は一個しかないはずだからforいらんかも

        for f in frameTag:
            FEs = FETagExtracter.findall(f.group(0))
            #print(FEs)
            for fe in FEs:
                type = typeExtracter.search(fe)
                name = nameExtracter.search(fe)
                #print(type.group())
                #print(name.group())
                elements.append( [name.group()[6:], type.group()[6:]] )#<frame　を消すためだと思われる

    sentences = sentenceTagExtracter.findall(contents)
    texts = []
    for s in sentences:
        text = textExtracter.search(s)
        if text:
            nospace = text.group().replace(" ", "")[6:-7]#空白を消したのち<text>と</text>を消す
            #print(nospace)
            texts.append(nospace)

    #ここからtextsをKNPにかけて格を見る　そんで文のどの位置と対応してるか見てそれがelementsなら格とelementの対応がわかる
    return texts

def getYomi(word):
    yomi = "None"
    res = ec.res_cmd('echo "' + word + '" | juman | knp -tab -dpnd ')
    #print(res)
    for s in reversed(res):
        if s.startswith(word):
            yomi = s.split()[1]

    return yomi

def getRoleReration(verb, luFilePath, knppath):
    reration = []
    #print(luFilePath)
    #luFile[-11:-4].knpを開く 頭のパスと.xmlを消すため
    knpfile = open(knppath + "/" + luFilePath[-11:-4] + ".knp", "r")
    contents = knpfile.read()

    sentenceSeparater = re.compile('# S-ID.*?EOS', re.MULTILINE | re.DOTALL)
    sentences = sentenceSeparater.findall(contents)
    #.knpの行でその動詞で始まってる行を探す

    #受け身文は捨てるパターン
    verbExtracter = re.compile("<格解析結果:" + verb + "[^+]*:.*")
    hiraganaVerbExtracter = re.compile("<格解析結果:" + ".*?/" + getYomi(verb) + ":.*")
    #受け身文は選択肢絞るパターン
    #ukemiExtracter = re.compile("<格解析結果:" + verb + "[^+]*\+れる/れる:.*")
    #受け身文は正規化格解析結果だけ使うパターン 動かしてないので正しく動作するかわからない
    #sekikaVerbExtracter = re.compile("<正規化格解析結果:" + verb + "[^+]*:.*")
    #受け身文の解析結果全部使うパターン
    #verbExtracter = re.compile("<格解析結果:" + verb + ".*")
    sn = 0
    for s in sentences:
        sn += 1
        print(sn)
        depends = []
        #print(s)
        #文節メモ
        bunsetsu = []
        keitaiso = []
        keitaisoCharNum = []
        lines = s.split("\n")
        #print(lines)
        charNum = 0
        for l in lines:
            if len(l) > 0:
                #print(l)
                if l[0] == '*':
                    bunsetsu.append(l)
                elif l[0] == '+':
                    keitaiso.append(len(bunsetsu)-1)
                    keitaisoCharNum.append(charNum)
                else:
                    charNum += len(l.split(" ")[0])
                    # print(l)
        """
        for i in range(len(keitaiso)):
            print(i, end = " ")
            print(extractDaihyo(bunsetsu[keitaiso[i]]))
        """
        lines = verbExtracter.findall(s)
        hiraLines = hiraganaVerbExtracter.findall(s)
        print(hiraLines)
        lines.extend(hiraLines)
        #print(lines)
        #print("source")
        #print(lines)
        #print("depends")
        #そこの[]にそれぞれの格の単語が書いてある
        dependExtracter = re.compile('[ァ-ヴ]+/[^U]/.*?/[0-9]+/')#頭がカタカナのやつだけとる　外の関係は知らん
        numExtracter = re.compile('[0-9]+')
        for line in lines:
            D = dependExtracter.findall(line)
            #print(depends)
            print(D)
            for depend in D:
                head = 0
                for i in range(len(depend)):
                    if depend[i] == '/':
                        head += 1
                        break
                    head += 1
                #if depend[head] != 'U':
                if depend[head] == 'C':
                    kaku = depend[:head-1]
                    #print(depend[:head-1] + "　" + depend[head+2:-1])
                    num = numExtracter.search(depend)
                    if num == None:
                        print("文節番号不明")
                        return []
                    else:
                        keitaisoNum = int(num.group())
                        print(extractDaihyo(bunsetsu[keitaiso[keitaisoNum]]), end = " ")
                        print(keitaisoCharNum[keitaisoNum])
                        depends.append( (kaku, extractDaihyo(bunsetsu[keitaiso[keitaisoNum]])) )


        #ExtractElementする
        elements = ExtractElements(luFilePath)
        #print(elements)
        #print(depends)
        #それぞれの格の単語が含まれるElementがどれか確認する
        for d in depends:
            for role in elements:
                #print(role)
                #前二つはroleとオプション？なのでいらない
                if d[1] in role[2:]:
                    p = (role[0],d[0])
                    if not p in reration:
                        reration.append(p)


    #対応がわかるのでなんかlistに入れて返す

    return reration

def getUkemiReration(verb, luFilePath, knppath):
    reration = []
    depends = []
    #luFile[-11:-4].knpを開く 頭のパスと.xmlを消すため
    knpfile = open(knppath + "/" + luFilePath[-11:-4] + ".knp", "r")
    contents = knpfile.read()

    #.knpの行でその動詞で始まってる行を探す

    #受け身文は選択肢絞るパターン
    ukemiExtracter = re.compile("<格解析結果:" + verb + "[^+]*\+.?れる/.?れる:.*?>")


    #文節メモ
    bunsetsu = []
    keitaiso = []
    lines = contents.split("\n")
    for l in lines:
        if len(l) > 0:
            if l[0] == '*':
                bunsetsu.append(l)
            elif l[0] == '+':
                keitaiso.append(len(bunsetsu)-1)
    """
    for i in range(len(keitaiso)):
        print(i, end = " ")
        print(extractDaihyo(bunsetsu[keitaiso[i]]))
    """
    lines = ukemiExtracter.findall(contents)
    #print(lines)
    #print("source")
    #print(lines)
    #print("depends")
    #そこの[]にそれぞれの格の単語が書いてある
    dependExtracter = re.compile('[ァ-ヴ]+/[^U]/.*?/[0-9]+/')#頭がカタカナのやつだけとる　外の関係は知らん
    numExtracter = re.compile('[0-9]+')
    for line in lines:
        D = dependExtracter.findall(line)
        #print(depends)
        print(D)
        for depend in D:
            head = 0
            for i in range(len(depend)):
                if depend[i] == '/':
                    head += 1
                    break
                head += 1
            if depend[head] != 'U':
                if depend[head] == 'C':
                    kaku = depend[:head-1]
                elif depend[head] == 'N':
                    kaku = "連"
                else:
                    continue

                #print(depend[:head-1] + "　" + depend[head+2:-1])
                num = numExtracter.search(depend)
                if num == None:
                    print("文節番号不明")
                    return []
                else:
                    keitaisoNum = int(num.group())
                    depends.append( (kaku, extractDaihyo(bunsetsu[keitaiso[keitaisoNum]])) )

    #ExtractElementする
    elements = ExtractElements(luFilePath)
    #print(elements)
    #print(depends)
    #それぞれの格の単語が含まれるElementがどれか確認する
    for d in depends:
        for role in elements:
            #print(role)
            #前二つはroleとオプション？なのでいらない
            if d[1] in role[2:]:
                p = (role[0],d[0])
                if not p in reration:
                    reration.append(p)


    #対応がわかるのでなんかlistに入れて返す

    return reration


def searchYogenDaihyo(word):
    exYogen = re.compile('<用言代表表記:.*?>')

    res = ec.res_cmd('echo "' + word + '"| juman | knp -dpnd-fast -tab')

    for r in res:
        yogen = exYogen.search(r)
        if yogen == None:
            continue

        yogen = yogen.group()[8:]

        add = True
        word = ""
        for i in range(len(yogen)):
            if yogen[i] == '/':
                add = False
                continue
            elif yogen[i] == '+':
                add = True
            if add:
                word = word + yogen[i]

        return word

def ExtractFrame(luFilePath):
    verbs = []

    # lexunit列挙
    frame = open(luFilePath, "r")
    contents = frame.read()
    frame.close()

    lexUnitExtracter = re.compile('<lexUnit.*>')
    lexLines = lexUnitExtracter.findall(contents)

    if lexLines:
        # print(matchOB)
        frameExtracter = re.compile('frame="[a-z,A-Z,_]+"')

        for lexLine in lexLines:
            #print(lexLine)
            f = frameExtracter.search(lexLine)
            if f != None:
                return f.group()[7:-1]

    return "None"

def extractParent(frameFileName):
    parents = []

    if not os.path.exists(frameFileName):
        print(frameFileName+"は存在しません")
        return parents

    # lexunit列挙
    frame = open(frameFileName, "r")
    contents = frame.read()
    frame.close()

    inheritExtracter = re.compile('<frameRelation type="Inherits from">.*?</frameRelation>', re.MULTILINE | re.DOTALL )
    inheritBrock = inheritExtracter.search(contents)

    if inheritBrock:
        # print(matchOB)
        frameExtracter = re.compile('<relatedFrame>.*?</relatedFrame>')
        frameLines = frameExtracter.findall(inheritBrock.group())

        for f in frameLines:
            parents.append(f[14:-15])

    return parents

def ExtractSubElements(luPath):

    elements = []

    frameName = ExtractFrame(luPath)
    frameDirPath = luPath

    slash = 0
    while slash < 2:
        if frameDirPath[-1] == '/':
            slash += 1
        frameDirPath = frameDirPath[:-1]

    IDs = ExtractID(frameDirPath + "/frame/" + frameName + ".xml")
    # Calls = fnextracter.ExtractVerb(path)
    if IDs == []:
        return elements
    IDs.remove(luPath[-9:-4])
    #print(IDs)

    slash = 0
    while slash < 1:
        if luPath[-1] == '/':
            slash += 1
        luPath = luPath[:-1]

    for i in IDs:
        #print(str(i))
        a = ExtractElements(luPath + '/lu' + str(i) + '.xml')
        for j in a:
            exist = False
            for k in range(len(elements)):
                if elements[k][0] == j[0]:
                    elements[k].extend(j[2:])
                    exist = True
            if exist == False:
                elements.append(j)
    # print(Calls)
    return elements

def ExtractFrameElements(frameFilePath):

    elements = []

    IDs = ExtractID(frameFilePath)

    slash = 0
    path = frameFilePath
    while slash < 2:
        if path[-1] == '/':
            slash += 1
        path = path[:-1]

    for i in IDs:
        a = ExtractElements(path + '/lu/lu' + str(i) + '.xml')
        for j in a:
            exist = False
            for k in range(len(elements)):
                if elements[k][0] == j[0]:
                    elements[k].extend(j[2:])
                    exist = True
            if exist == False:
                elements.append(j)

    return elements

def ExtractParentsElement(frameFilePath):
    parents = extractParent(frameFilePath)

    slash = 0
    frameDirPath = frameFilePath
    while slash < 1:
        if frameDirPath[-1] == '/':
            slash += 1
        frameDirPath = frameDirPath[:-1]

    IDs = []
    for p in parents:
        IDs.extend( ExtractID(frameDirPath + "/" + p + ".xml") )
    # Calls = fnextracter.ExtractVerb(path)

    elements = []

    slash = 0
    luPath = frameFilePath
    while slash < 2:
        if luPath[-1] == '/':
            slash += 1
        luPath = luPath[:-1]

    for i in IDs:
        #print(str(i))
        a = ExtractElements(luPath + '/lu/lu' + str(i) + '.xml')
        for j in a:
            exist = False
            for k in range(len(elements)):
                if elements[k][0] == j[0]:

                    # 同じ例文があるかもしれないからelementを一個ずつ確認する
                    for e in j[2:]:
                        if e not in elements[k]:
                            elements[k].append(e)

                    exist = True
            if exist == False:
                elements.append(j)
    # print(Calls)
    return elements
