import math
import parametric_surfaces_builder as ps
import numpy as np
import normalvec as nvec


# functions for bezier creation
def binomial(i, n):
    """Binomial coefficient"""
    return math.factorial(n) / float(
        math.factorial(i) * math.factorial(n - i))


def bernstein(t, i, n):
    """Bernstein polynom"""
    return binomial(i, n) * (t ** i) * ((1 - t) ** (n - i))


def bezier(t, points):
    """Calculate coordinate of a point in the bezier curve"""
    n = len(points) - 1
    x = y = 0
    for i, pos in enumerate(points):
        bern = bernstein(t, i, n)
        x += pos[0] * bern
        y += pos[1] * bern
    return x, y


def bezier_curve_range(n, points):
    """Range of points in a curve bezier"""
    for i in range(n):
        t = i / float(n - 1)
        yield bezier(t, points)


def general_bezier_mapping(t, pointlist):
    """this glues multiple curves together,
    pointlist is a collection of list consisting of 4 points with which we make the bezier curves"""
    num = len(pointlist)-1
    length = num + 1
    """so this is the amount of bezier curves we have - 1"""
    funclist = []

    def makelambda(list):
        return lambda s:bezier(s,list)

    for i in range(length):
        """now we want to make all the curves"""
        funclist.append(makelambda(pointlist[i]))

    def totalcurve(t, i, list):
        return list[i](length*t-i) if t <= (i+1)/length else totalcurve(t, i+1, list)
    """ putting in our funclist should give our wanted mapping"""

    return totalcurve(t, 0, funclist)


# function used for creating vmf
def curvemaker(pointlist, height, xamount, yamount, displength, dispwidth):
    def mapping(t, pointlist):
        return general_bezier_mapping(t, pointlist)

    def func(x, y):
        return [mapping(x, pointlist)[0], mapping(x, pointlist)[1], y*height]
    ps.filewriter(xamount, yamount, displength, dispwidth, func, 2)

def curvemaker2(pointlist, height, xamount, yamount, displength, dispwidth):
    def mapping(t, pointlist):
        return general_bezier_mapping(t, pointlist)

    def func(x, y):
        return [mapping(x, pointlist)[0], y*height, mapping(x, pointlist)[1]]
    ps.filewriter(xamount, yamount, displength, dispwidth, func, 2)


# two functions used to create the plot
def general_bezier_curve_range_x(rangelist, pointlist):
    """Range of points in a curve bezier"""
    a = []
    for item in rangelist:
         a.append(general_bezier_mapping(item, pointlist)[0])

    return a


def general_bezier_curve_range_y(rangelist, pointlist):
    """Range of points in a curve bezier"""
    a = []
    for item in rangelist:
         a.append(general_bezier_mapping(item, pointlist)[1])

    return a


# functions for interpolation between two curves
def bump_function(t):
    return 0 if t == 0 else (np.exp(-1/t)/(np.exp(-1/t)+np.exp(-1/(1-t))) if t < 1 else 1)


def interp(bez1, bez2, t, y, start=0, end=1):
    return [bump_function((y-start)/(end-start))*bez1(t)[0] + bump_function(1-(y-start)/(end-start))*bez2(t)[0], bump_function((y-start)/(end-start))*bez1(t)[1]+bump_function(1-(y-start)/(end-start))*bez2(t)[1]]


def interpmaker(pointlist1, pointlist2, height, xamount, yamount, displength, dispwidth):
    curve1 = lambda t: general_bezier_mapping(t, pointlist1)
    curve2 = lambda t: general_bezier_mapping(t, pointlist2)

    def func(x, y):
        return [interp(curve1, curve2, x, y)[0], interp(curve1, curve2, x, y)[1], y*height]

    ps.filewriter(xamount, yamount, displength, dispwidth, func, 2)

def general_interpmaker_side(pointlistlist, height, xamount, yamount, displength, dispwidth):

    def makelambda(list):
        return lambda s:general_bezier_mapping(s,list)

    funclist = []
    for elem in pointlistlist:
        funclist.append(makelambda(elem))
    list_length = len(funclist)-1
    # still need to write something for a length of 1

    def func(x, y, i, funclist):

        start = i/list_length
        end = (i+1)/list_length
        if y <= end:
            #print(start, end)
            # print(i)
            return [interp(funclist[i+1], funclist[i], x, y, start = start, end = end)[0], interp(funclist[i+1], funclist[i], x, y, start = start, end = end)[1], y*height]
        else:
            return func(x, y, i+1, funclist)

    newfunc = lambda x,y: func(x, y, 0 , funclist)

    ps.filewriter(xamount, yamount, displength, dispwidth, newfunc, 2)

def general_interpmaker_top(pointlistlist, height, xamount, yamount, displength, dispwidth):

    def makelambda(list):
        return lambda s:general_bezier_mapping(s,list)

    funclist = []
    for elem in pointlistlist:
        funclist.append(makelambda(elem))
    list_length = len(funclist)-1
    # still need to write something for a length of 1

    def func(x, y, i, funclist):

        start = i/list_length
        end = (i+1)/list_length
        if y <= end:
            #print(start, end)
            # print(i)
            return [interp(funclist[i+1], funclist[i], x, y, start = start, end = end)[0], y*height, interp(funclist[i+1], funclist[i], x, y, start = start, end = end)[1]]
        else:
            return func(x, y, i+1, funclist)

    newfunc = lambda x,y: func(x, y, 0 , funclist)

    ps.filewriter(xamount, yamount, displength, dispwidth, newfunc, 2)


# functions for making along the normal of a big curve
def along_normal_maker(pointlist, height,xamount, yamount, displength, dispwidth):
    pl = pointlist

    def mapping(t):
        return np.array([general_bezier_mapping(t, pl)[0],general_bezier_mapping(t, pl)[1]])

    def newmapping(x, y):
        #return mapping(x)+y*nvec.normal(mapping,x)*height
        return mapping(x)+height*np.cos(y*2*np.pi)*nvec.normal(mapping,x/1.00001)

    def func(x, y):
        return [newmapping(x, y)[0], newmapping(x, y)[1], np.sin(y*2*np.pi)*height]
    ps.filewriter(xamount, yamount, displength, dispwidth, func, 2)

def along_curve_maker(longlist, shortlist, xamount, yamount, displength, dispwidth):
    ll = longlist
    sl = shortlist
    rate = 1.5

    def mapping(t):
        return np.array([general_bezier_mapping(t, ll)[0],general_bezier_mapping(t, ll)[1]])

    def curve(s):
        return general_bezier_mapping(s,sl)

    def newmapping(x, y):
        #return mapping(x)+y*nvec.normal(mapping,x)*height
        return mapping(x)-rate*curve(y)[0]*nvec.normal(mapping,x/1.00001)

    def func(x, y):
        return [newmapping(x, y)[0], newmapping(x, y)[1], rate*curve(y)[1]]
    ps.filewriter(xamount, yamount, displength, dispwidth, func, 2)

def along_interp_maker(longlist, pointlistlist, xamount, yamount, displength, dispwidth):
    def newfunc(x, y):
        def makelambda(list):
            return lambda s:general_bezier_mapping(s,list)

        funclist = []
        for elem in pointlistlist:
            funclist.append(makelambda(elem))
        list_length = len(funclist)-1
        # still need to write something for a length of 1

        def func(x, y, i, funclist):

            start = i/list_length
            end = (i+1)/list_length
            if y <= end:
                #print(start, end)
                # print(i)
                return np.array(interp(funclist[i+1], funclist[i], x, y, start = start, end = end))
            else:
                return func(x, y, i+1, funclist)

        return func(x, y, 0 , funclist)


    ll = longlist
    rate = 1.5

    def mapping(t):
        return np.array([general_bezier_mapping(t, ll)[0],general_bezier_mapping(t, ll)[1]])

    def newmapping(x, y):
        #return mapping(x)+y*nvec.normal(mapping,x)*height
        return mapping(x)-rate*newfunc(y, x)[0]*nvec.normal(mapping,x/1.00001)

    def func(x, y):
        return [newmapping(x, y)[0], newmapping(x, y)[1], rate*newfunc(y, x)[1]]
    ps.filewriter(xamount, yamount, displength, dispwidth, func, 2)
