#!/bin/bash

set -e 

if [ -f /tmp/nwm_xfer.lock ]; then
    echo lock file still found at /tmp/nwm_xfer.lock
    exit 1
fi

echo $$ > /tmp/nwm_xfer.lock

NOW=`date -u +%Y%m%d`

THEN=`date -u -d yesterday +%Y%m%d`

directories=( "analysis_assim" "medium_range" "short_range" )

cd /work/projects/TexasFlood/data/para/nwm.${THEN}
for i in "${directories[@]}" 
do
    cd $i 
    wget -c ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/nwm.${THEN}/${i}/\*channel_rt\*
    cd ..
done

mkdir -p  /work/projects/TexasFlood/data/para/nwm.${NOW}
cd /work/projects/TexasFlood/data/para/nwm.${NOW}

for i in "${directories[@]}" 
do
    mkdir -p $i 
    cd $i
    set +e
    wget -c ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/nwm.${NOW}/${i}/\*channel_rt\*
    set -e
    cd ..
done

rm /tmp/nwm_xfer.lock
