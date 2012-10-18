#!/bin/bash

build_dir=/data3/lbne/bv/wbls/sim/WbLS/people/bv/build/
mkdir -p $build_dir

log=$build_dir/build.log

do_it () {
    base=/data3/lbne/bv/wbls/install
    pushd $build_dir
    cmake \
	-DCMAKE_BUILD_TYPE=Debug \
	-DGeant4_DIR=$base/geant4/4.9.5.p01/lib64/Geant4-9.5.1 \
	-DROOT_DIR=$base/root/5.32.02 \
	-DGCCXML_home=$base/gccxml/0.9.0_20120309 \
	-DROOT_genreflex_cmd=genreflex \
	-DVGM_DIR=$VGM_INSTALL \
	-DVGM_SYSTEM=$VGM_SYSTEM \
	-DHEPMC_DIR=$base/hepmc/2.06.08 \
	../cowbells && \
	make CPPFLAGS=-DGEANT4_USE_OPENGL_X11=1\
              && \
	popd
    echo ok, log in $log
}

#do_it 2>&1 | tee $log
do_it
