#!/bin/bash
# Test a single topology using Garnet standalone build for synth traffic simulation.
# Author: Bruno Cesar, bcesar.g6@gmail.com 2018
# base command: ./build/Garnet_standalone/gem5.debug configs/example/garnet_synth_traffic.py --network=garnet2.0 --num-cpus=16 --num-dirs=16 --topology=Mesh_XY --mesh-rows=4 --sim-cycles=50000 --inj-vnet=0 --injectionrate=0.02 --synthetic=uniform_random --link-width-bits=32

user=$(whoami)
OUT_DIR=/home/$user/gem5saidas
echo "Script de teste - Rodando como $user"

while getopts "t:n:" opt; do
  case $opt in
    t)
     TOPOLOGY=${OPTARG};;

    n)
     NUM_CPUS=${OPTARG};;

    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

./../../build/Garnet_standalone/gem5.opt ./../../configs/example/garnet_synth_traffic.py --network=garnet2.0 --num-cpus=$NUM_CPUS --num-dirs=4 --topology=$TOPOLOGY --mesh-rows=4 --sim-cycles=50000 --inj-vnet=0 --injectionrate=0.02 --synthetic=uniform_random --link-width-bits=32

mv m5out/ $OUT_DIR/$TOPOLOGY
echo "fim"
