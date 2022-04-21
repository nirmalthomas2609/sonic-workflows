import ROOT
ROOT.gROOT.SetBatch(True)
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('python')
options.inputFiles="/uscms_data/d1/wmccorma/test_workflow_prePR_Apr11/CMSSW_12_0_0_pre5/src/sonic-workflows/step2_ailab01.root"
options.parseArguments()
# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.FWLiteEnabler.enable()
# load FWlite python libraries
from DataFormats.FWLite import Handle, Events
particles, particleLabels = Handle("std::vector<reco::GenParticle>"),"genParticles"
print(particleLabels)
events = Events(options)
for ievent,event in enumerate(events):
    event.getByLabel(particleLabels, particles)
    nparticles = particles.product().size()
    print("processing event", ievent, "of", events.size())
    for ip, p in enumerate(particles.product()):
        pt = p.pt()
        if(pt > 10 and p.mother().pdgId() > 5000):
            eta = p.eta()
            mass = p.mass()
            pdgid = p.pdgId()
            status = p.status()
            print("pt",pt,"\t eta", eta,"\t pdgid", pdgid, "\t mass", mass, "\t status", status)
            print("mom ", p.mother().pdgId())
