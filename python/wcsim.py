#!/usr/bin/env python

import ROOT
ROOT.gSystem.Load("libWCSimRoot")

class TreeReader(object):
    def __init__(self, filename, 
                 branchname="wcsimrootevent", 
                 treename="wcsimT", 
                 klass = ROOT.WCSimRootEvent):
        '''
        Create a connection to a tree in the given file
        '''
        self.tfile = ROOT.TFile.Open(filename)
        self.tree = self.tfile.Get(treename)
        ebranch = self.tree.GetBranch(branchname)
        self.event = klass()
        ebranch.SetAddress(ROOT.AddressOf(self.event))
        self._entry = -1
        self.nentries = self.tree.GetEntries()

    def __call__(self, entry):
        '''
        Load tree entry number <entry> and return the event.

        Raises StopIteration if entry is out of bounds.
        '''
        self._entry = entry
        if self._entry >= self.nentries:
            raise StopIteration
        self.tree.GetEntry(entry)
        return self.event

    def __iter__(self):
        '''
        wcsimtree = WCSimTree("wcsim.root")
        for evt in wcsimtree:
            trig = evt.GetTrigger(0)
            ...
        '''
        self._entry = -1
        return self

    def next(self):
        return self(self._entry + 1)

    

class Events(TreeReader):
    def __init__(self, filename):
        '''
        Create a connection to a WCSim event tree in the given file
        '''
        super(Events, self).__init__(filename)

class Geom(TreeReader):
    def __init__(self, filename):
        super(Geom, self).__init__(filename, 
                                   branchname="wcsimrootgeom", 
                                   treename="wcsimGeoT", 
                                   klass=ROOT.WCSimRootGeom)
        self.geo = self(0)
        self.npmts = self.geo.GetWCNumPMT()
        self._locdir = []
        for ipmt in range(self.npmts):
            pmt = self.geo.GetPMT(ipmt)
            ploc = [pmt.GetPosition(i) for i in range(3)]
            pdir = [pmt.GetOrientation(i) for i in range(3)]
            self._locdir.append((ploc,pdir))

    def pmt(self, pmtid):
        return self.geo.GetPMT(pmtid-1)

    def pmt_locdir(self, pmtid):
        return self._locdir[pmtid-1]

class Data(object):
    def __init__(self, filename):
        self.events = Events(filename)
        self.geom = Geom(filename)
        

    def trigger(self, entry, trigger = 0):
        evt = self.events(entry)
        trig = evt.GetTrigger(trigger)
        return trig

    def tracks(self, entry):
        trig = self.trigger(entry)
        tarray = trig.GetTracks()
        return [tarray.At(i) for i in range(tarray.GetSize())]

    def hits(self, entry):
        trig = self.trigger(entry)
        ret = []
        digihits = trig.GetCherenkovDigiHits()
        for ihit in range(trig.GetNcherenkovdigihits()):
            dh = digihits.At(ihit)
            pmtid = dh.GetTubeId()
            hit = (dh.GetT(), dh.GetQ(), self.geom.pmt_locdir(pmtid))
            ret.append(hit)
        return ret

        
