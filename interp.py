import ast
import bezierfuncs as bez

filepath1 = r"C:\Users\Acer\Documents\GitHub\parametric-surfaces\saved files\cliff_interp.bez"
filepath2 = r"C:\Users\Acer\Documents\GitHub\parametric-surfaces\saved files\cliff_interp2.bez"

with open(filepath1, "r") as text:
    pointdict1 = ast.literal_eval(text.readline())
with open(filepath2, "r") as text:
    pointdict2 = ast.literal_eval(text.readline())

def pointlist_maker(pointdict):
    pointlist = []
    pointlist.append([pointdict[0]["node"],pointdict[0]["handles"][0]])
    for i in range(1,(len(pointdict)-1)):
        pointlist[i-1].extend([pointdict[i]["handles"][0], pointdict[i]["node"]])
        pointlist.append([pointdict[i]["node"],pointdict[i]["handles"][1]])
    pointlist[(len(pointdict)-2)].extend([pointdict[len(pointdict)-1]["handles"][0], pointdict[len(pointdict)-1]["node"]])
    return(pointlist)

pointlist1 = pointlist_maker(pointdict1)
pointlist2 = pointlist_maker(pointdict2)

bez.interpmaker(pointlist1, pointlist2, 5*128, 5, 2, 256, 256)
print("Done")
