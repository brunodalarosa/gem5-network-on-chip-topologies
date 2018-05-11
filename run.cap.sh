M5PATH_DIR=/home/gem5/gem5-simulator/fullsystem
GEM5_DIR=/home/gem5/gem5-simulator/gem5
CKPT_DIR=/home/gem5/gem5-simulator/ckpts
CKPT_NUM=1

protocols=('MOESI_hammer')
disks=('debian')
cpus=(32)
memorysizes=('1GB')
networks=('garnet2.0')
topologies=('MeshDirCorners_XY')
benchs=('fast' 'fn' 'gf' 'is' 'km' 'lu' 'tsp')
inputsets=('small')

for (( p=0; p<${#protocols[@]}; p++ )); do

        protocol=${protocols[${p}]}

	for (( d=0; d<${#disks[@]}; d++ )); do

        	disk=${disks[${d}]}

		export M5_PATH=$M5PATH_DIR/$disk

	        for (( c=0; c<${#cpus[@]}; c++ )); do

 		       ncpus=${cpus[${c}]}

			case $ncpus in
				2 | 4 | 8)
					nrows=2
				;;
				16 | 32)
					nrows=4
				;;
				64)
					nrows=8
				;;
			esac

			for (( m=0; m<${#memorysizes[@]}; m++ )); do

				memorysize=${memorysizes[${m}]}

				for (( n=0; n<${#networks[@]}; n++ )); do

					network=${networks[${n}]}

					for (( t=0; t<${#topologies[@]}; t++ )); do

						topology=${topologies[${t}]}

						for (( b=0; b<${#benchs[@]}; b++ )); do

							bench=${benchs[${b}]}

							for (( i=0; i<${#inputsets[@]}; i++ )); do

								inputset=${inputsets[${i}]}

								rm -rf X86_$protocol.$ncpus.$memorysize.$network.$topology.$disk.$bench.$inputset

								/usr/bin/time -v -o X86_$protocol.$ncpus.$memorysize.$network.$topology.$disk.$bench.$inputset.time $GEM5_DIR/build/X86_$protocol/gem5.fast --outdir=X86_$protocol.$ncpus.$memorysize.$network.$topology.$disk.$bench.$inputset --listener-mode=off $GEM5_DIR/configs/example/fs.py --checkpoint-restore=$CKPT_NUM --checkpoint-dir=$CKPT_DIR/X86_$protocol.$ncpus.$memorysize.$network.$topology.$disk --ruby --ruby-clock=2.5GHz --restore-with-cpu=TimingSimpleCPU --cpu-clock=2.5GHz --num-cpus=$ncpus --num-dirs=4 --mem-size=$memorysize --num-l2caches=$ncpus --l1d_size=32kB --l1i_size=32kB --l1d_assoc=4 --l1i_assoc=4 --l2_size=128kB --l2_assoc=8 --network=$network --topology=$topology --vcs-per-vnet=8 --router-latency=1 --script=/home/gem5/gem5-simulator/benchmarks/cap/scripts.rcS/$bench.$ncpus.$inputset.rcS &> X86_$protocol.$ncpus.$memorysize.$network.$topology.$disk.$bench.$inputset.out &

							done

						done

					done

				done

			done

		done

	done

done
