import ast
import bezierfuncs as bez

mode = "along"
def pointlist_maker(pointdict):
    pointlist = []
    pointlist.append([pointdict[0]["node"],pointdict[0]["handles"][0]])
    for i in range(1,(len(pointdict)-1)):
        pointlist[i-1].extend([pointdict[i]["handles"][0], pointdict[i]["node"]])
        pointlist.append([pointdict[i]["node"],pointdict[i]["handles"][1]])
    pointlist[(len(pointdict)-2)].extend([pointdict[len(pointdict)-1]["handles"][0], pointdict[len(pointdict)-1]["node"]])
    return(pointlist)

def before_mapping(pll, height, xamount, yamount, displength, dispwidth):

    if mode == "along":
        if pll[1] == []:
            print("there are no small curves")
            return
        if len(pll[1]) == 1:
            bez.along_curve_maker(pll[0], pll[1][0], xamount, yamount, displength, dispwidth)
            return
        else:
            bez.along_interp_maker(pll[0], pll[1], xamount, yamount, displength, dispwidth)
            return
    elif mode == "tube":
        bez.along_normal_maker(pll[0], height, xamount, yamount, displength, dispwidth)
        return
    elif mode == "height":
        bez.curvemaker(pll[0], height, xamount, yamount, displength, dispwidth)
        return

filepath = r"C:\Users\Acer\Documents\GitHub\parametric-surfaces\saved files\new_format.bez"

with open(filepath, "r") as text:
    pointdictdict = ast.literal_eval(text.readline())
    vmfdict = ast.literal_eval(text.readline())


int_vmfdict = {}
for key,value in vmfdict.items():
    int_vmfdict[key] = int(value)
pointlistlist = []
pointlistlist.append(pointlist_maker(pointdictdict["longcurve"]))
shortcurvelist = []
for elem in pointdictdict["shortcurvelist"]:
    shortcurvelist.append(pointlist_maker(elem))
pointlistlist.append(shortcurvelist)
before_mapping(pointlistlist, int_vmfdict["height"], int_vmfdict["xamount"], int_vmfdict["yamount"], int_vmfdict["displength"], int_vmfdict["dispwidth"])
