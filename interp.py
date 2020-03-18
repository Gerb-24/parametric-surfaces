import ast
import bezierfuncs as bez
import os

directory = r"C:\Users\Acer\Documents\GitHub\parametric-surfaces\saved files\revit"
filepathlist = []
for filename in os.listdir(directory):
    filepathlist.append(os.path.join(directory,filename))


def pointlist_maker(pointdict):
    pointlist = []
    pointlist.append([pointdict[0]["node"],pointdict[0]["handles"][0]])
    for i in range(1,(len(pointdict)-1)):
        pointlist[i-1].extend([pointdict[i]["handles"][0], pointdict[i]["node"]])
        pointlist.append([pointdict[i]["node"],pointdict[i]["handles"][1]])
    pointlist[(len(pointdict)-2)].extend([pointdict[len(pointdict)-1]["handles"][0], pointdict[len(pointdict)-1]["node"]])
    return(pointlist)

pointlistlist = []
for elem in filepathlist:
    with open(elem, "r") as text:
        pointdict = ast.literal_eval(text.readline())
        pointlistlist.append(pointlist_maker(pointdict))

bez.general_interpmaker_top(pointlistlist, 8*256, 5, 8, 256, 256)
print("Done")
