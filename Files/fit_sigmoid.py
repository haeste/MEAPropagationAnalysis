# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 13:48:38 2014

@author: chris
"""
import scipy


def sigmoid(x, a, b,  c, d):
    return ((a**2) + b) / (1 + scipy.exp(-(x - c)/d))


def fit_sigmoid(x,y):
    popt, pcov = scipy.optimize.curve_fit(sigmoid, x, y, p0=[20, 200, 2000, 1200])
    return popt