
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