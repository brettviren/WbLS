#!/usr/bin/env python
'''
Make dE/dX plots
'''

import cowbells
import ROOT

canvas = ROOT.TCanvas()


def cprint(printfilename = "dedx.pdf", extra=""):
    print 'Printing to %s' % printfilename
    canvas.Modified()
    canvas.Update()
    canvas.Print(printfilename + extra,"pdf")
    return


materials = [
    "Water", "WBLS", "Acrylic", "BlackAcrylic", "SiO2", "B2O3",
    "Na2O", "Al2O3", "Glass", "Vacuum", "Teflon",
]



def get_trees(filenames):
    trees = []
    files = []
    for filename in filenames:
        print filename
        fp = ROOT.TFile.Open(filename)
        cb = fp.Get("cowbells")
        trees.append(cb)
        files.append(fp)
        continue
    return trees,files

def filename2energy(filename):
    return int (filename.split('-')[1])

def plotexit(*filenames):
    trees,files = get_trees(filenames)

    vacid = materials.index("Vacuum")
    tefid = materials.index("Teflon")

    hists = []
    mevs = []
    maxy=0
    for index,cb in enumerate(trees):
        mev = filename2energy(filenames[index])
        name = "Eexit%d" % index
        h = ROOT.TH1F(name, "Energy at exit for %d MeV KE"%mev, 250,0,2500)
        count = cb.Draw("energy2>>%s"%name,
                        "trackid==1 && mat1==%d && mat2==%d" % (tefid,vacid),"goff")
        if not count: 
            print 'Skipping %d MeV which has no exiting protons' % mev
            continue

        maxy = max(maxy, h.GetMaximum())
        hists.append(h)
        mevs.append(mev)
        print '%d MeV with max Y = %d' % (mev,maxy)
        continue

    tt = ROOT.TText()
    tt.SetTextAlign(22)
    tt.SetTextSize(tt.GetTextSize()*0.5)
    frame = canvas.DrawFrame(0,1,2500,maxy*1.05,'Energy of proton exiting Teflon tub')
    frame.SetXTitle('Kinetic Energy (MeV)')

    for h,mev in zip(hists,mevs):
        h.Draw("same")
        diff = mev-h.GetMean()
        tt.DrawText(mev,h.GetMaximum(),'%d MeV / lost %.1f MeV'%(mev,diff))
        continue

    pdffile = "dedx_exitplot.pdf"
    cprint(pdffile)
    return

def multiplot(matid, *filenames):
    matid = int(matid)
    matname = materials[matid]
    dedx_max = 12;
    hdedx = ROOT.TH2F("dedx","dE/dx (MeV/cm) vs energy for material %s"%matname,
                     250,0,2500, 10*dedx_max, 0, dedx_max)
    
    print hdedx.GetTitle()

    pdffile = "dedx_multiplot_%s.pdf" % matname
    cprint(pdffile,"[")

    trees,files = get_trees(filenames)
    for index, cb in enumerate(trees):
        name = "temp%d" % index
        htmp = ROOT.TH2F(name,"dE/dx (MeV/cm) vs energy for material %s energy #%d"%\
                             (matname, index),
                         250,0,2500, 10*dedx_max, 0, dedx_max)
        # multiply by 10 to put it in MeV/cm instead of native MeV/mm
        count = cb.Draw("10*edep/dist:0.5*(energy1+energy2)>>%s"%name,
                        "mat1==%d&&mat2==%d&&trackid==1"%(matid,matid))
        print '%d from %s' % (count, files[index].GetName())
        htmp.Draw("colz")
        cprint(pdffile)
        hdedx.Add(htmp)
        continue
    hdedx.Draw("colz")
    cprint(pdffile)
    cprint(pdffile,"]")
    return (trees,files)



def plot(filename, energy):
    return

if __name__ == '__main__':
    import sys
    func = eval(sys.argv[1])
    func(*sys.argv[2:])
