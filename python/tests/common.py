#!/usr/bin/env python

import os
import sys

testdir = os.path.dirname(os.path.realpath(__file__))
pydir = os.path.dirname(testdir)
sys.path.insert(0, pydir)

def filepath(filename = "wcsim-100MeVelectron.root"):
    return os.path.join(testdir, filename)

