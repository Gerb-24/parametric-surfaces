import math
import parametric_surfaces_builder as ps
import numpy as np


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


def bezier_mapping_of_two_curves(t, pointlist):
    """This glues two bezier curves together"""
    bez1 = lambda t: bezier(t, pointlist[0:4])
    bez2 = lambda t: bezier(t, pointlist[3:7])
    tot_bez = bez1(2*t) if t<1/2 else bez2(2*t-1)
    return tot_bez


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


def curvemaker(pointlist):
    def mapping(t, pointlist):
        return general_bezier_mapping(t, pointlist)

    def func(x, y, pointlist):
        return [mapping(x, pointlist)[0], mapping(x, pointlist)[1], y]

    ps.filewriter(16, 16, 256, 256, lambda x,y: func(x, y, pointlist), 2)

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
