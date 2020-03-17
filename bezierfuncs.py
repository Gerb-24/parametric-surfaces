import math
import parametric_surfaces_builder as ps
import numpy as np


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


def interp(bez1, bez2, t, y):
    return [bump_function(y)*bez1(t)[0] + bump_function(1-y)*bez2(t)[0], bump_function(y)*bez1(t)[1]+bump_function(1-y)*bez2(t)[1]]


def interpmaker(pointlist1, pointlist2, height, xamount, yamount, displength, dispwidth):
    curve1 = lambda t: general_bezier_mapping(t, pointlist1)
    curve2 = lambda t: general_bezier_mapping(t, pointlist2)

    def func(x, y):
        return [interp(curve1, curve2, x, y)[0], interp(curve1, curve2, x, y)[1], y*height]

    ps.filewriter(xamount, yamount, displength, dispwidth, func, 2)
