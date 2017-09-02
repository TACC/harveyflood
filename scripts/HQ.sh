#!/bin/bash	

# This is a modified version by TACC on Sep 1 2017
# Si Liu, Cyrus Proctor, Niall Gaffney, Xing Zheng

source /work/projects/TexasFlood/scripts/setenv.bash

search_dir=/work/projects/TexasFlood/WorstQ
for entry in "$search_dir/"* 
do
echo $entry 
python /work/projects/TexasFlood/scripts/forecast-table.py /work/projects/TexasFlood/data/HUC6 $entry /work/projects/TexasFlood/WorstH
done
