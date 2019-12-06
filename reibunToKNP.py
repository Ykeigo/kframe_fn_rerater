import fnextracter as fe
import sys
import executeCommand as ec
import os

args = sys.argv

for f in os.scandir(path=args[1]):
    currentFile = open(args[2] + '/' + f.name[:-4] + ".knp", mode='w')

    reibuns = fe.ExtractReibun(args[1] + "/" + f.name)

    for r in reibuns:
        print(r)
        res = ec.res_cmd( 'echo "' + r + '" | juman | knp -tab')
        print(res)
        for l in res:
            currentFile.write(l+'\n')

    currentFile.close()