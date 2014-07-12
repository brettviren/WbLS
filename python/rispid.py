#!/usr/bin/env python
'''
Implement the ideas from 

http://www-sk.icrr.u-tokyo.ac.jp/doc/sk/pub/florian_goebel.pdf
'''
import math

def track_distance(pos, tdir, point, angle = 42.0/180.*math.pi):
    '''Return the distance from <pos> down unit vector <tdir> such that a
    line drawn with the given <angle> from <tdir> hits <point>.
    '''
    rdir = [point[i]-pos[i] for i in range(3)]
    rmag = math.sqrt(sum([rdir[i]*rdir[i] for i in range(3)]))
    rdir = [rdir[i]/rmag for i in range(3)]
    cosine = sum([rdir[i]*tdir[i] for i in range(3)])
    sine = math.sin(math.acos(cosine))
    cos_ceren = math.cos(angle)
    sin_ceren = math.sin(angle)
    return rmag*(cosine - sine * cos_ceren / sin_ceren)


def charge_track_distr(collector, hits, vtx, tdir,  
                       attenlen = 8500,
                       angle = 42.0/180.*math.pi):
    '''Call collector(dist, corrected_charge) for each hit in hits.  The
    distance <dist> is the distance along the track direction <trk>
    from the vertex <vtx> where light would have to be emitted to
    cause hit.  The <hits> is a list of tuples: (time, charge, pmt).
    A pmt object must have a .pos and .dir 3-tuple.
    '''

    for t, q, pmt in hits:
        ploc, pdir = pmt
        td  = track_distance(vtx, tdir, ploc, angle)
        lray = [ploc[i] - (vtx[i]+td*tdir[i]) for i in range(3)]
        lmag = math.sqrt(sum([lray[i]*lray[i] for i in range(3)]))
        pmag = math.sqrt(sum([pdir[i]*pdir[i] for i in range(3)]))
        dot = sum([lray[i]*pdir[i]/(lmag*pmag) for i in range(3)])
        if dot > 0: 
            continue
        lcor = math.exp(lmag/attenlen)
        collector(td, lcor*q)
    return
