#!/bin/bash

ACCESS=ssh
CORES=8
BATCH=""
CMSSWVER=CMSSW_12_4_0_pre2
CMSSWVERS=(
CMSSW_12_4_0_pre2 \
)

usage(){
        EXIT=$1

        echo "setup.sh [options]"
        echo ""
        echo "-B                  configure some settings for checkout within batch setups (default = ${BATCH})"
        echo "-C                  choose CMSSW version (default = ${CMSSWVER}, choices=${CMSSWVERS[@]})"
        echo "-a [protocol]	  use protocol to clone (default = ${ACCESS}, alternative = https)"
        echo "-j [cores]          run CMSSW compilation on # cores (default = ${CORES})"
        echo "-h                  display this message and exit"

        exit $EXIT
}

# process options
while getopts "BC:a:j:h" opt; do
        case "$opt" in
        B) BATCH=--upstream-only
        ;;
	C) CMSSWVER=$OPTARG
        ;;
	a) ACCESS=$OPTARG
        ;;
	j) CORES=$OPTARG
        ;;
	h) usage 0
        ;;
	esac
done

# check options
if [ "$ACCESS" = "ssh" ]; then
        ACCESS_GITHUB=git@github.com:
        ACCESS_GITLAB=ssh://git@gitlab.cern.ch:7999/
        ACCESS_CMSSW=--ssh
elif [ "$ACCESS" = "https" ]; then
        ACCESS_GITHUB=https://github.com/
        ACCESS_GITLAB=https://gitlab.cern.ch/
        ACCESS_CMSSW=--https
else
    	usage 1
fi

# check CMSSW version
if [[ ! " ${CMSSWVERS[@]} " =~ " $CMSSWVER " ]]; then
        echo "Unsupported CMSSW version: $CMSSWVER"
        usage 1
fi

export SCRAM_ARCH=slc7_amd64_gcc10
scram project $CMSSWVER
cd ${CMSSWVER}/src
eval `scramv1 runtime -sh`
git cms-init $ACCESS_CMSSW $BATCH
git clone ${ACCESS_GITHUB}nirmalthomas2609/sonic-workflows -b ragged/development

# use updated triton external
cd ${CMSSW_BASE}
mkdir build && cd build
cp ${CMSSW_BASE}/src/sonic-workflows/triton.tar.gz .
tar -xzf triton.tar.gz
cp ${CMSSW_BASE}/src/sonic-workflows/triton-inference-client.xml $CMSSW_BASE/config/toolbox/$SCRAM_ARCH/tools/selected/

# get packages and build
cd ${CMSSW_BASE}/src
scram setup triton-inference-client
git cms-checkout-topic $ACCESS_CMSSW nirmalthomas2609:dev/particlenet-ragged-new
#git cms-checkout-topic $ACCESS_CMSSW nirmalthomas2609:debug
scram b checkdeps
git cms-addpkg HeterogeneousCore/SonicTriton
git clone ${ACCESS_GITHUB}kpedro88/HeterogeneousCore-SonicTriton -b ragged HeterogeneousCore/SonicTriton/data

scram b -j ${CORES}

mkdir -p RecoBTag/Combined/data/particlenet_modelsForSonic
git clone ${ACCESS_GITHUB}nirmalthomas2609/sonic-models -b dev/ragged-cpu-export-onnx-name-ragged RecoBTag/Combined/data/particlenet_modelsForSonic/
cp -r RecoBTag/Combined/data/particlenet_modelsForSonic/models/* RecoBTag/Combined/data/particlenet_modelsForSonic/
rm -r RecoBTag/Combined/data/particlenet_modelsForSonic/models