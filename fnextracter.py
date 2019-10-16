import re
import executeCommand as ec
import os

#動詞取り出す
def ExtractVerb(frameFileName):

    verbs=[]

    #lexunit列挙
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
    frame = open(frameFileName, "r")
    contents = frame.read()
    frame.close()

    lexUnitExtracter = re.compile('<lexUnit.*>')
    lexLines = lexUnitExtracter.findall(contents)

    numExtracter = re.compile('[0-9]+')
    lexIDExtracter = re.compile(' ID="[0-9]*"')

    if lexLines:
        #print(matchOB)

        #タグからlemmaIDを取り出す
        for lexUnitLine in lexLines:
            IDTags = lexIDExtracter.findall(lexUnitLine)
            #print(IDTags)
            for tag in IDTags:
                n = numExtracter.search(tag)
                LUIDs.append(n.group())


    return LUIDs


#文から主表表記（主辞’代表表記があればそっち優先）を取り出す
def extractHead(str):
    res = ec.res_cmd( 'echo "' + str + '" | juman | knp -tab -dpnd ')
    all = ''
    for line in reversed(res):
        #print(i)
        headExtracter = re.compile("<主辞代表表記.*?>")
        head = headExtracter.search(line)
        head2Extracter = re.compile("<主辞’代表表記.*?>")
        head2 = head2Extracter.search(line)
        if head2 != None:
            #print(head2.group())
            wordSimbol = head2.group()[9:]# <主辞’代表表記:の次の文字から見たい
            word = ''
            add = True
            for i in range(len(wordSimbol)):
                if wordSimbol[i] == '/':
                    add = False
                    continue
                elif wordSimbol[i] == '+':
                    add = True
                    continue
                if add:
                    word = word + wordSimbol[i]

            return word
        if head != None:
            #print(head.group())
            word = ''
            wordSimbol = head.group()[8:]# <主辞代表表記:の次の文字から見たい
            for i in range(len(wordSimbol)):
                if wordSimbol[i] == '/':
                    break
                word = word + wordSimbol[i]
            return word

    return None

#例文のエレメント取り出す
#3つ目の要素が例文中の単語
def ExtractElements(LUFileName):

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
    typeExtracter = re.compile('type="[a-zA-Z]+')
    nameExtracter = re.compile('name="[a-zA-Z]*')

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
                elements.append( [name.group()[6:], type.group()[6:]] )

    sentences = sentenceTagExtracter.findall(contents)
    #print(sentences)
    for sentenceTag in sentences:

        texts = textExtracter.findall(sentenceTag)
        labels = labelExtracter.findall(sentenceTag)
        #print(texts)

        for text in texts:
            text = text[6:]
            for label in labels:
                name = nameExtracter.search(label)
                #print(name.group())
                for e in elements:
                    #print(e[0])
                    if e[0] in name.group():
                        end = endExtracter.search(label)
                        start = startExtracter.search(label)
                        if end == None or start == None:
                            continue
                        end = end.group()[5:]#end=を消すため
                        start = start.group()[7:]#start=を消すため

                        #空白消してjumanknp型にする
                        nospace = text[int(start):int(end) - 1].replace(" ", "")
                        if len(nospace) == 0:
                            continue

                        #res = ec.res_cmd("echo " + nospace + " | ./han2zen.pl | nkf | juman | knp -dpnd-fast -tab | ./knp2words.sh")
                        res = extractHead(nospace)
                        #print(nospace)
                        #sprint(res)
                        #parts = res[0].split(" ")
                        #e.append(parts[-1])
                        e.append(res)
    #print(sentences)

    return elements
