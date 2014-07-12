#!/usr/bin/env python

import math
import common
import wcsim

def test_load():
    w = wcsim.Events(common.filepath())
    assert w
    assert w.nentries == 1
    e = w(0)
    assert e

def test_iter():
    w = wcsim.Events(common.filepath())
    assert w
    for e in w:
        assert e.GetNumberOfEvents() == 1
        t = e.GetTrigger(0)
        assert t
        assert t.GetNumTubesHit()
        assert t.GetNumDigiTubesHit()
        assert t.GetNtrack()
        assert t.GetNcherenkovhittimes()
        assert t.GetNcherenkovhits()
        assert t.GetNcherenkovdigihits()

def test_geom():
    g = wcsim.Geom(common.filepath())
    assert g
    assert g.nentries
    geo = g(0)
    npmts = geo.GetWCNumPMT()
    assert npmts
    #print npmts
    for ipmt in range(npmts):
        pmt = geo.GetPMT(ipmt)
        assert pmt
        assert pmt.GetTubeNo()-ipmt == 1
        #print ipmt, pmt.GetTubeNo(), pmt.GetCylLoc()

    # test the above type of PMT access which is internal to the Geom class
    for ipmt in range(npmts):
        p = g.pmt(ipmt+1)
        assert p.GetTubeNo() == ipmt+1

def test_data():
    d = wcsim.Data(common.filepath())
    hits = d.hits(0)
    assert len(hits)
    for t,q,(ploc, pdir) in hits:
        prad = math.sqrt(sum([ploc[i]*ploc[i] for i in range(3)]))
        assert prad > 1000



if '__main__' == __name__:
    test_load()
    test_iter()
    test_geom()
    test_data()
