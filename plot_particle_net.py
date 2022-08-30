#!/usr/bin/env python
import ROOT as rt
from DataFormats.FWLite import Events,Handle
import itertools as it
from ROOT import btagbtvdeep
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# file evaluated with DeepJet framework
# jets redone from AOD using CMSSW TF modules
#cmssw_miniaod = "test_particle_net_MINIAODSIM.root"
#cmssw_miniaod = "test_particle_net_MINIAODSIM_noragged.root"

cmssw_miniaod = "step2_ailab01.root"
#cmssw_miniaod = "step2_directPN.root"

#jetsLabel = "selectedUpdatedPatJets"
#jetsLabel = "recoGenJets_slimmedGenJetsAK8"
#jetsLabel = "patJets_slimmedJetsAK8__PAT"
jetsLabel = "slimmedJetsAK8"

from RecoBTag.ONNXRuntime.pfParticleNet_cff import _pfParticleNetJetTagsProbs
#from RecoBTag.ONNXRuntime.pfParticleNet_cff import _pfParticleNetSonicJetTagsProbs
#disc_names = _pfParticleNetJetTagsProbs+_pfParticleNetSonicJetTagsProbs
disc_names = _pfParticleNetJetTagsProbs

jet_pt = "fj_pt"
jet_eta = "fj_eta"

c_numbers = ['event_n']

#for d_name in disc_names:
#    print(d_name)

c_cmssw = { d_name : []  for d_name in disc_names + [jet_pt, jet_eta] + c_numbers }
jetsHandle = Handle("std::vector<pat::Jet>")
cmssw_evs = Events(cmssw_miniaod)

max_n_jets = 1000000
max_n_events = 500000
n_jets = 0

for i, ev in enumerate(cmssw_evs):
    event_number = ev.object().id().event()
    if (n_jets >= max_n_jets): break
    ev.getByLabel(jetsLabel, jetsHandle)
    jets = jetsHandle.product()
    for i_j,j in enumerate(jets):
        uncorr = j.jecFactor("Uncorrected")
        ptRaw = j.pt()*uncorr
        if ptRaw < 150.0 or abs(j.eta()) > 2.4: continue
        if (n_jets >= max_n_jets): break
        c_cmssw["event_n"].append(event_number)
        c_cmssw[jet_pt].append(ptRaw)
        c_cmssw[jet_eta].append(j.eta())
        discs = j.getPairDiscri()
        for d in discs:
            if d.first in disc_names:
                c_cmssw[d.first].append(d.second)
        n_jets +=1
        
df_cmssw = pd.DataFrame(c_cmssw)
df_cmssw.sort_values(['event_n', jet_pt], ascending=[True, False], inplace=True)
df_cmssw.reset_index(drop=True)
#print(df_cmssw[['event_n','fj_eta','fj_pt',
#                'pfParticleNetJetTags:probTbq','pfParticleNetSonicJetTags:probTbq',
#            ]])
print(df_cmssw[['event_n','fj_eta','fj_pt',
                'pfParticleNetJetTags:probTbq', 'pfParticleNetJetTags:probTbqq', 'pfParticleNetJetTags:probTbc'
            ]])

n_bins = 50

print('number of tags', len(disc_names))
fig, axs = plt.subplots(5,4,figsize=(50,40))
for i,ax in enumerate(axs.flatten()):
    cmssw_col = disc_names[i]
    ax.hist(df_cmssw[cmssw_col], bins=np.linspace(np.amin(df_cmssw[cmssw_col]), np.amax(df_cmssw[cmssw_col]), n_bins))
    ax.set_yscale('log')
    ax.set_ylim(0.5, 1000)
    ax.set_xlim(0, 1)
    ax.set_xlabel(cmssw_col)
    ax.set_ylabel('Jets')
#fig.savefig('particle_net_hist.png')
fig.savefig('particle_net_hist_noragged.png')