#!/bin/bash	

# This is a modified version by TACC on Sep 1 2017
# Si Liu, Cyrus Proctor, Niall Gaffney, Xing Zheng

source /work/projects/TexasFlood/scripts/setenv.bash


timenow=`ls -tr ../data/para | tail -1`
timeonly=`echo $timenow | cut -d "." -f 2`

search_dir=${base}/WorstQ/${timeonly}/short_range
#search_dir=${base}/WorstQ/Test


echo ${search_dir}
mkdir -p ${base}/WorstH/${timeonly}/short_range

for entry in "$search_dir/"* 
do
echo $entry 
python /work/projects/TexasFlood/scripts/forecast-table.py /work/projects/TexasFlood/data/HUC6-new $entry ${base}/WorstH/${timeonly}/short_range
done
