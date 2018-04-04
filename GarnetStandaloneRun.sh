#!/bin/bash
# Test all the topologies using Garnet standalone build for synth traffic simulation.
# Author: Bruno Cesar, bcesar.g6@gmail.com 2018
# base command: ./build/Garnet_standalone/gem5.debug configs/example/garnet_synth_traffic.py --network=garnet2.0 --num-cpus=16 --num-dirs=16 --topology=Mesh_XY --mesh-rows=4 --sim-cycles=50000 --inj-vnet=0 --injectionrate=0.02 --synthetic=uniform_random --link-width-bits=32

user=$(whoami)
OUT_DIR=/home/$user/gem5saidas
echo "Testes - Running as $user"

topologies=('Pt2PtDirCorners' 'Pt2PtDirCorners_2' 'TorusDirCorners' 'TorusDirCorners_2' 'TreeDirCorners' 'TreeDirCorners_2' 'ButteflyDirCorners' 'ButteflyDirCorners_2' 'ClosDirCorners' 'ClosDirCorners_2' 'FlattenedButteflyDirCorners' 'FlattenedButteflyDirCorners_2' 'OmegaDirCorners' 'OmegaDirCorners_2' 'BenesDirCorners' 'BenesDirCorners_2' 'MultiPathDirCorners' 'MultiPathDirCorners_2')
num_cpus=('8' '16' '32')
synthetics=('uniform_random' 'tornado' 'neighbor')
injections=('0.02' '0.04' '0.06' '0.08' '0.1' '0.12'  '0.14' '0.16' '0.18' '0.2' '0.22' '0.24' '0.26' '0.28' '0.3')

for (( t=0; t<${#topologies[@]}; t++ )); do
    topology=${topologies[${t}]}
    mkdir $OUT_DIR/$topology


    for (( s=0; s<${#synthetics[@]}; s++ )); do
      synthetic=${synthetics[${s}]}
      mkdir $OUT_DIR/$topology/$synthetic

      for (( n=0; n<${#num_cpus[@]}; n++ )); do
        num_cpu=${num_cpus[${n}]}
        mkdir $OUT_DIR/$topology/$synthetic/$num_cpu

            for (( i=0; i<${#injections[@]}; i++ )); do
                inj=${injections[${i}]}

                ./../../build/Garnet_standalone/gem5.opt ./../../configs/example/garnet_synth_traffic.py --network=garnet2.0 --num-cpus=$num_cpu --num-dirs=4 --topology=$topology --sim-cycles=50000 --inj-vnet=0 --injectionrate=$inj --synthetic=$synthetic --link-width-bits=32

                mv m5out/ $OUT_DIR/$topology/$synthetic/$num_cpu/m5out.$inj

            done
        done
    done
done

echo "fim"
