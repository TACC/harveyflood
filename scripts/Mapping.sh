#!/bin/bash

# This is a modified version by TACC on Sep 1 2017
# Si Liu, Cyrus Proctor, Niall Gaffney, Xing Zheng

source /work/projects/TexasFlood/scripts/setenv.bash

taudem2=${TACC_TAUDEMYAN_BIN}
np=1

### This is where the data locates at TACC
wrootdir=/work/projects/TexasFlood/data/HUC6-new
hucidlist="120401 120402"

#hucidlist="121003 121002 121004 121001 120903 120904 120701 120401 120402 120302 120200 120301 120602"

hq_dir=/work/projects/TexasFlood/WorstH/Test
for hucid in $hucidlist; do
n=$hucid
wdir=$wrootdir/$hucid
mapdir=/work/projects/TexasFlood/WorstMap/Test
for entry in "$hq_dir/"*; do
if  [[ $entry == *nc ]];
then
name=$(basename "$entry" ".nc")
mapfile=${n}${name}inunmap.tif
#ibrun -np $np
${TACC_TAUDEMYAN_BIN}/inunmap -hand $wdir/${n}hand.tif -catch $wdir/${n}catchhuc.tif -mask $wdir/${n}waterbodymask.tif -forecast $entry -mapfile $mapdir/$mapfile
fi
done
done
