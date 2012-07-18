#!/usr/bin/env python
'''
Main entry to the cowbells (COsmic WB(el)LS) simulation modules

'''

import PyCintex
import ROOT

import boot
boot.everything()               # boot all the things!

units = PyCintex.Namespace("units").CLHEP

interface = ROOT.Cowbells.interface

