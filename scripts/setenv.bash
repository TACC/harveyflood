#!/bin/bash

#Run this script before your run your script


module use /work/projects/TexasFlood/apps/modulefiles
export LD_LIBRARY_PATH=/work/projects/TexasFlood/apps/filegdb/file-geodatabase-api/FileGDB_API_1.5.1/FileGDB_API-64gcc51/lib:$LD_LIBRARY_PATH

module load gdal  
module load nfie-floodmap 
#module load taudem-kornholi  
module load taudem-yan
