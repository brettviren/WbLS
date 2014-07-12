#!/usr/bin/env python

import math
import common
import ROOT
import wcsim
from rispid import track_distance, charge_track_distr
from timing import point_residuals, track_residuals

canvas = ROOT.TCanvas()
def canvas_print(hint=""):
    canvas.Print("test_rispid.pdf%s"%hint, "pdf")


def test_track_distance():
    td = track_distance([0,0,0],     # vertex
                        [0,0,1],     # track direction
                        [1,0,1],     # pmt "position"
                        angle = 45.0/180*math.pi)
    assert abs(td) < 0.00001

def test_charge_track_distr():
    d = wcsim.Data(common.filepath())

    ctd = ROOT.TH1F("ctd","Charge-Track Distr",1000,-10000,10000)
    ROOT.gStyle.SetOptStat(111111)

    hits = d.hits(0)
    track = d.tracks(0)[0]
    tvtx = [track.GetStart(i) for i in range(3)]
    tdir = [track.GetDir(i) for i in range(3)]
    print 'vertex:', tvtx
    print 'track: ', tdir

    charge_track_distr(lambda x,q: ctd.Fill(x,q), hits, tvtx, tdir)
    assert ctd.GetEntries() <= len(hits), '%d > %d' % (ctd.GetEntries(), len(hits))

    ctd.Draw()
    canvas_print()
                       
def test_timing():
    d = wcsim.Data(common.filepath())
    tim = ROOT.TH1F("tim","Times",300,900,1200)
    ROOT.gStyle.SetOptStat(111111)
    hits = d.hits(0)
    for t,q,pmt in hits:
        tim.Fill(t,q)
    tim.Draw()
    canvas_print()

def test_point_residuals():
    d = wcsim.Data(common.filepath())
    res = ROOT.TH1F("pointres","Point Residuals",400,800,1200)
    ROOT.gStyle.SetOptStat(111111)
    hits = d.hits(0)
    track = d.tracks(0)[0]
    tvtx = [track.GetStart(i) for i in range(3)]
    T0 = track.GetTime()
    print T0
    resids = point_residuals(hits, tvtx, T0)
    for r,dat in zip(resids,hits):
        q = dat[1]
        res.Fill(r, q) 
    res.Draw()
    canvas_print()

def test_track_residuals():
    d = wcsim.Data(common.filepath())
    res = ROOT.TH1F("trackres","Track Residuals",400,800,1200)
    ROOT.gStyle.SetOptStat(111111)
    hits = d.hits(0)
    track = d.tracks(0)[0]
    tvtx = [track.GetStart(i) for i in range(3)]
    tdir = [track.GetDir(i) for i in range(3)]
    T0 = track.GetTime()
    resids = track_residuals(hits, tvtx, tdir, T0)
    for r,dat in zip(resids,hits):
        q = dat[1]
        res.Fill(r, q) 
    res.Draw()
    canvas_print()
    
def timecut_charge_track(filename):
    d = wcsim.Data(filename)

    name = filename[6:-5]       # hack alert: assumes "wcsim-NAME.root"
    title = "%s Charge-Track Distr (timing cut)" % name
    ctd = ROOT.TH1F("ctd",title,1000,-10000,10000)
    ROOT.gStyle.SetOptStat(111111)

    hits = d.hits(0)
    track = d.tracks(0)[0]
    tvtx = [track.GetStart(i) for i in range(3)]
    tdir = [track.GetDir(i) for i in range(3)]
    T0 = track.GetTime()
    #resids = point_residuals(hits, tvtx, T0)
    resids = track_residuals(hits, tvtx, tdir, T0)

    intime_hits = []
    for r,hit in zip(resids,hits):
        if r < 800 or r > 820:
            continue
        intime_hits.append(hit)

    charge_track_distr(lambda x,q: ctd.Fill(x,q), intime_hits, tvtx, tdir)
    assert ctd.GetEntries() <= len(hits), '%d > %d' % (ctd.GetEntries(), len(hits))

    ctd.Draw()
    canvas_print()

def test_timecut_charge_track():
    for fn in ["wcsim-100MeVelectron90.root",
               "wcsim-100MeVelectron.root",
               "wcsim-100MeVmuon90.root",
               "wcsim-100MeVmuon.root"]:
        timecut_charge_track(common.filepath(fn))

if '__main__' == __name__:
    canvas_print("[")
    test_track_distance()
    test_charge_track_distr()
    test_timing()
    test_point_residuals()
    test_track_residuals()
    test_timecut_charge_track()
    canvas_print("]")
