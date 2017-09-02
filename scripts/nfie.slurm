#!/bin/bash

#SBATCH -J NFIE            # Job name
#SBATCH -o NFIE.o%j        # Name of stdout output file
#SBATCH -e NFIE.e%j        # Name of stderr error file
#SBATCH -p test1           # Queue (partition) name
#SBATCH -N 1               # Total # of nodes (must be 1 for serial)
#SBATCH -n 1               # Total # of mpi tasks (should be 1 for serial)
#SBATCH -t 02:00:00        # Run time (hh:mm:ss)
#SBATCH -A harveyflood     # Allocation name (req'd if you have more than 1)

export base=/work/projects/TexasFlood

module reset
source ${base}/scripts/setenv.bash

pwd
date
module list

echo "Job script here:"
echo "----------------------------------------------"
cat nfie.slurm
echo "----------------------------------------------"


echo "Data synchronization"
${base}/data/update_today_nwm.sh

echo "Generate Peak Flow..."
python ${base}/scripts/forecast-nwm-worst.py  ${base}/data/para/nwm.20170901/short_range    "nwm.t16z.short_range.channel_rt.f016.conus.nc nwm.t16z.short_range.channel_rt.f017.conus.nc nwm.t16z.short_range.channel_rt.f018.conus.nc" ${base}/outputs-1/firsttry.nc

sleep 5

echo "Convert discharge to water level ..."
${base}/scripts/HQ.sh

sleep 5
echo "Mapping ..."
${base}/scripts/Mapping.sh
