#!/usr/bin/env

import math
from rispid import track_distance # this should be moved out of rispid

light_speed = 29.979246         # cm/ns

def point_residuals(hits, vtx, t0=1000.0, n=1.33):
    residuals = []
    for t,q,(ploc, pdir) in hits:
        ray = [vtx[i] - ploc[i] for i in range(3)]
        dist = math.sqrt(sum([ray[i]*ray[i] for i in range(3)]))
        ltime = dist * n / light_speed
        res = t - t0 - ltime
        residuals.append(res)
    return residuals


def track_residuals(hits, tvtx, tdir, t0=1000.0, n=1.33):
    residuals = []
    for t,q,(ploc, pdir) in hits:
        td = track_distance(tvtx, tdir, ploc)
        ray = [ploc[i] - (tvtx[i] + td*tdir[i]) for i in range(3)]
        light = math.sqrt(sum([ray[i]*ray[i] for i in range(3)]))
        res = t - (t0 + td/light_speed + light*n/light_speed)
        residuals.append(res)
    return residuals
