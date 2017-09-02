#!/bin/bash

# This is a modified version by TACC on Sep 1 2017
# Si Liu, Cyrus Proctor, Niall Gaffney, Xing Zheng

source /work/projects/TexasFlood/scripts/setenv.bash

taudem2=${TACC_TAUDEMYAN_BIN}
np=1

timenow=`ls -tr ../data/para | tail -1`
timeonly=`echo $timenow | cut -d "." -f 2`
mkdir -p ${base}/WorstH/${timeonly}/short_range

### This is where the data locates at TACC
wrootdir=/work/projects/TexasFlood/data/HUC6-new

hucidlist="120401 120402"
#hucidlist="120100 120200 120301 120302 120401 120402 120500 120601 120602 120701 120702 120800 120901 120902 120903 120904 121001  121002 121003 121004 121101 121102"

hq_dir=${base}/WorstH/${timeonly}/short_range

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
