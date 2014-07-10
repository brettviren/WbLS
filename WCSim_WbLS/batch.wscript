#!/usr/bin/env python
'''This is a waf script.  

To use it:

 - copy this file to a working directory and name it "wscript"

 - get a copy of the "waf" program.  One is provided in the source at
   WbLS/worch/waf or down load it from https://code.google.com/p/waf/

 - Assuming you copy it to the working directory, trigger it unpack by
   running:

  ./waf --version

 - It is assumed that the program "wcsim-wbls" is in your PATH

 - to configure a bunch of runs do, for example:

  ./waf configure --nevents=1000 \
                  --particles=e-,mu- \
                  --energies=100,500,1000 \
                  --scint=0,90

 - finally to start the runs do just

  ./waf

Output will go to a subdirectory "runs/" and each run to a sub
directory below which is named using the parameter set for eac run.

'''

out='runs'

macfiles = dict(
    jobOptions = '''# this is a generated file
/WCSim/physics/list WCSim
''',
    jobOptions2 = '''# this is a generated file
/WCSim/physics/secondaries/model BINARY
''',
    novis = '''# this is a generated file
/run/verbose 0
/tracking/verbose 0
/hits/verbose 0
/WCSim/PMTQEMethod     Stacking_And_SensitiveDetector
/WCSim/WCgeom DUSEL_200kton_12inch_HQE_12perCent
/WCSim/SavePi0 true
/mygen/generator normal
/gun/particle {particle}
/gun/energy {energy} MeV
/gun/direction 1 0 0 
/gun/position 0 0 0 
/WCSim/ConstructWLS false
/WCSim/ConstructWLSP false
/WCSim/ConstructLC false
/WCSim/WLSPSHAPE circle
/WCSim/PMTCollEff on
/WCSim/PMTCollEff_Method 1
/WCSim/PMT_Timing_Var on
/WCSim/Construct
/WCSimIO/RootFile {outputfile}
/run/beamOn {nevents}
''',
    tuning_parameters = '''# this is a generated file
/WCSim/tuning/abwff 1.0
/WCSim/tuning/rayff 1.0
/WCSim/tuning/rgcff 0.24
/WCSim/tuning/bsrff 0.7
/WCSim/tuning/topveto 0
/WCSim/tuning/tvspacing 100
/WCSim/tuning/photonYield {scint}
''')


def options(opt):
    opt.add_option('--particles', action='store', default='e-',
                   help='List of particle names')
    opt.add_option('--energies', action='store',  default='1000',
                   help='List of energies in MeV')
    opt.add_option('--scint', action='store', default='0',
                   help='List of scintilation yields in photons/MeV')
    opt.add_option('--nevents', action='store', default='100',
                   help='Number of events per sample')

def configure(cfg):
    cfg.find_program('wcsim-wbls',var='WCSIM')

    sims = []
    for nevents in cfg.options.nevents.split(','):
        nevents = int(nevents)
        for particle in cfg.options.particles.split(','):
            if particle[-1] not in '-+': particle += '-'
            assert particle in ['e-','e+','mu-','mu+'] # small sanity check
            for energy in cfg.options.energies.split(','):
                energy = float(energy)
                for scint in cfg.options.scint.split(','):
                    scint = float(scint)
                    sims.append((nevents,particle,energy,scint))
    cfg.env.sims = sims

def macfiles_gen(task):

    dat = task.generator.dat
    for macfile in task.outputs:
        name = str(macfile).replace('.mac','')
        content = macfiles[name]
        outdir = task.outputs[0].parent.abspath()
        outfile = outdir + '/wcsim.root'
        text = content.format(outputfile=outfile, **dat)
        macfile.write(text)
        
def build(bld):

    for nevents,particle,energy,scint in bld.env.sims:
        dat = dict(nevents=nevents,particle=particle,
                   energy=energy,scint=scint)
        subdir="{nevents}evts_{particle}_{energy}MeV_{scint}".format(**dat)
        subnode = bld.path.get_bld().make_node(subdir)
        subnode.mkdir()
        print 'SUBDIR',subnode.abspath()
        macpaths = ['%s/%s.mac'%(subdir,name) for name in macfiles.keys()]
        bld(rule=macfiles_gen, target=macpaths,
            update_outputs=True, cwd=subnode.abspath(), dat=dat)
        bld(rule="${WCSIM} novis.mac > log 2>&1", source=macpaths, 
            output=subdir+"/wcsim.root", 
            shell=True, cwd=subnode.abspath())
