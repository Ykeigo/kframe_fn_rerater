import re
import sys
import os
import time

def ExtractVerb(fileName):

    sentences=[]

    #lexunit列挙
    frame = open(fileName, "r")
    contents = frame.read()
    frame.close()

    textExtracter = re.compile('<text>.*?</text>')
    textLines = textExtracter.findall(contents)

    if textLines:
        #print(matchOB)
        for line in textLines:
            l = line[6:-7].replace(" ", "")

            sentences.append(l)


    frame.close()
    return sentences

args = sys.argv

output = open("full.txt", mode='w')

for f in os.scandir(path=args[1]):
    sentences = ExtractVerb(args[1]+"/"+f.name)
    for s in sentences:
        print(s)
        output.write(s+"\n")

    print("")
    output.write("\n")
    #time.sleep(1)
output.close()