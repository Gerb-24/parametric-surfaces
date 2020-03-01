import numpy as np
from itertools import chain
import math


def rounder(x):
    return "[{0} {1} {2}]".format(round(x[0], 2),round(x[1], 2),round(x[2], 2))


def normer(x, start):
    vec = start-x
    norm_vec = vec / np.linalg.norm(vec)
    return norm_vec


def scaler(func,x, y, xamount, yamount, length, width):
    u = x/(xamount*length)
    v = y/(yamount*width)
    newfunc = lambda a, b: func(a,b)*2**8
    return newfunc(u, v)


def bezscaler(func, x, y, xamount, yamount, length, width):
    u = x/(xamount*length)*0.99995
    v = y/(yamount*width)
    return np.array([func(u,v)[0]*2**4,func(u,v)[1]*2**4,func(u,v)[2]*2**12])


cos = lambda x: np.cos(x*2*np.pi)
sin = lambda x: np.sin(x*2*np.pi)


def normal_vec(func, x, y):
    return normer(np.array([x,y,0]), func(x,y))


def distance(func, x, y):
    return round(np.linalg.norm(np.array([x,y,0])-func(x,y)),2)


def dispmaker(info):
    x, y, z, length, width, func = info[0], info[1], info[2], info[3], info[4], info[5]
    start = "[{0} {1} {2}]".format(x, y, z)
    s = '''
                        dispinfo
                        {{       
                                "power" "3"
                                "startposition" "{0}"
                                "flags" "0"
                                "elevation" "0"
                                "subdiv" "0"
                                normals
                                {{
'''.format(start)

    r = 0
    while r < 9:
        normallist = []
        i = 0
        while i < 9:
            normallist.append(normal_vec(func, r * length / 8 + x, i * width / 8 + y))
            i += 1
        k ='''                                        "row{0}" "{1}"
'''.format(r, ' '.join(' '.join(str(x) for x in elem) for elem in normallist))
        s += k
        r += 1
    s += '''                                }
                                distances
                                {
'''
    r = 0
    while r < 9:
        rowdist = []
        i = 0
        while i < 9:
            rowdist.append(distance(func, r * length / 8 + x, i * width / 8 + y))
            i += 1
        k = '''                                        "row{0}" "{1}"
'''.format(r, ' '.join(map(str, rowdist)))
        s += k
        r += 1
    s+='''                                }
                                offsets
                                {
                                        "row0" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row1" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row2" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row3" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row4" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row5" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row6" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row7" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row8" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                }
                                offset_normals
                                {
                                        "row0" "0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1"
                                        "row1" "0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1"
                                        "row2" "0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1"
                                        "row3" "0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1"
                                        "row4" "0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1"
                                        "row5" "0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1"
                                        "row6" "0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1"
                                        "row7" "0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1"
                                        "row8" "0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1"
                                }
                                alphas
                                {
                                        "row0" "0 0 0 0 0 0 0 0 0"
                                        "row1" "0 0 0 0 0 0 0 0 0"
                                        "row2" "0 0 0 0 0 0 0 0 0"
                                        "row3" "0 0 0 0 0 0 0 0 0"
                                        "row4" "0 0 0 0 0 0 0 0 0"
                                        "row5" "0 0 0 0 0 0 0 0 0"
                                        "row6" "0 0 0 0 0 0 0 0 0"
                                        "row7" "0 0 0 0 0 0 0 0 0"
                                        "row8" "0 0 0 0 0 0 0 0 0"
                                }
                                triangle_tags
                                {
                                        "row0" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row1" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row2" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row3" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row4" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row5" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row6" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                        "row7" "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                                }
                                allowed_verts
                                {
                                        "10" "-1 -1 -1 -1 -1 -1 -1 -1 -1 -1"
                                }
                        }
'''
    return s


class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def return_fixed_z(self):
        return self.x, self.y, self.z

    def __add__(self, other):
        return Vertex(self.x+other.x, self.y+other.y, self.z+other.z)


class Face:
    id_counter = 1

    def __init__(self, v1: Vertex, v2: Vertex, v3: Vertex):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def return_all(self):
        return self.v1, self.v2, self.v3

    def __add__(self, other):
        return Face(self.v1+other.v1,self.v2+other.v2,self.v3+other.v3)

    def generate_face(self, uaxis, vaxis, i, dispinfo):
        Face.id_counter += 1
        side = '''
                side
                {{
                        "id" "{9}"
                        "plane" "({0} {1} {2}) ({3} {4} {5}) ({6} {7} {8})"
                        "material" "TOOLS/TOOLSNODRAW"
                        "uaxis" "{10} 0.25"
                        "vaxis" "{11} 0.25"
                        "rotation" "0"
                        "lightmapscale" "16"
                        "smoothing_groups" "0"'''.format(*self.v1.return_fixed_z(), *self.v2.return_fixed_z(), *self.v3.return_fixed_z(), self.id_counter, uaxis, vaxis)
        if i == 1:
            side += dispmaker(dispinfo)
        side +='''
                }'''
        return side


class Shape:
    id_counter = 1
    teleport_target = "default"
    use_landmark_angles = True
    csgo = 0

    def __init__(self, *args: Face):
        self.faces = []
        self.faces.extend(args)


    def get_all_vertices(self):
        return list(chain.from_iterable([f.return_all() for f in self.faces]))

    def generate_shape(self, dispinfo):
        s = '''
        solid
        {{
                "id" "{0}"'''.format(self.id_counter)
        Shape.id_counter += 1
        i = 0
        while i < len(self.faces):
            if i == 0 or i == 1:
                uaxis = "[1 0 0 0]"
                vaxis = "[0 -1 0 0]"
            elif i == 2 or i == 3:
                uaxis = "[0 1 0 0]"
                vaxis = "[0 0 -1 0]"
            elif i == 4 or i == 5:
                uaxis = "[1 0 0 0]"
                vaxis = "[0 0 -1 0]"

            s += self.faces[i].generate_face(uaxis, vaxis, i, dispinfo)
            i += 1
        s += '''
                editor
                {
                        "color" "0 136 109"
                        "visgroupshown" "1"
                        "visgroupautoshown" "1"
                }
        }'''

        return s


def brushmaker(length, width, x, y, z, func):
    h, l, w = Vertex(0, 0, 128), Vertex(length, 0, 0), Vertex(0, width, 0)
    sp = Vertex(x, y, z)
    zero = Vertex(0, 0, 0)
    startface = Face(sp, sp, sp)
    face1 = Face(h+w, h+l+w, h+l)+startface
    face2 = Face(zero, l, l+w)+startface
    face3 = Face(h+w, h, zero)+startface
    face4 = Face(l+w, l, h+l)+startface
    face5 = Face(h+l+w, h+w, w)+startface
    face6 = Face(l, zero, h)+startface
    dispinfo = [x, y, z, length, width, func]

    return Shape(face1, face2, face3, face4, face5, face6).generate_shape(dispinfo)


def brushwriter(file, xamount, yamount, length, width, func):
    i = 0
    while i < xamount:
        j = 0
        while j < yamount:
            file.writelines(brushmaker(length, width, i*length, j*width, 0, func))
            j +=1
        i +=1


intro = '''versioninfo
{
        "editorversion" "400"
        "editorbuild" "8075"
        "mapversion" "0"
        "formatversion" "100"
        "prefab" "0"
}
viewsettings
{
        "bSnapToGrid" "1"
        "bShowGrid" "1"
        "bShowLogicalGrid" "0"
        "nGridSpacing" "64"
        "bShow3DGrid" "0"
}
world
{
        "id" "1"
        "mapversion" "0"
        "classname" "worldspawn"
        "skyname" "sky_tf2_04"
        "maxpropscreenwidth" "-1"
        "detailvbsp" "detail_2fort.vbsp"
        "detailmaterial" "detail/detailsprites_2fort"'''
outro = '''
}
cameras
{
        "activecamera" "-1"
}
cordons
{
        "active" "0"
}'''


def filewriter(xamount, yamount, length, width, func, scaling):
    with open("newmap3.vmf", "w") as text:
        text.writelines(intro)
        brushwriter(text, xamount, yamount, length, width, lambda x,y: scaler(func,x, y, xamount, yamount, length, width)  if scaling == 1 else bezscaler(func, x, y, xamount, yamount,length, width))
        # file, the amount of copies in x direction, amount in y direction, length (x), width (y).
        text.writelines(outro)
