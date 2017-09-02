# harveyflood

W. Cyrus Proctor
2017-09-01



Directories:
  filegdb
  freexl
  gdal
  modulefiles
  nfie
  proj4
  spatialite
  sqlite
  taudem-kornholi
  taudem-official
  taudem-yan


filegdb:
  URL: https://github.com/Esri/file-geodatabase-api
  version: FileGDB_API_1.5.1/FileGDB_API_1_5_1-64gcc51.tar.gz
  build script: /work/projects/TexasFlood/apps/filegdb/filegdb.st2.build
  install location: /work/projects/TexasFlood/apps/filegdb/file-geodatabase-api/FileGDB_API_1.5.1/FileGDB_API-64gcc51/samples/bin/
  modulefile: /work/projects/TexasFlood/apps/modulefiles/filegdb


freexl:
  URL: https://www.gaia-gis.it/fossil/freexl/index
  version: 1.0.3
  build script: /work/projects/TexasFlood/apps/freexl/freexl.st2.build
  install location: /work/projects/TexasFlood/apps/freexl/install
  modulefile: /work/projects/TexasFlood/apps/modulefiles/freexl


gdal:
  URL: http://www.gdal.org
  version: 2.2.1
  build script: /work/projects/TexasFlood/apps/gdal/gdal.st2.build
  install location: /work/projects/TexasFlood/apps/gdal/install
  modulefile: /work/projects/TexasFlood/apps/modulefiles/gdal


nfie:
  URL: https://github.com/cybergis/nfie-floodmap
  version: none -- straight from git repo
  build script: /work/projects/TexasFlood/apps/nfie/nfie.st2.build
  install location: /work/projects/TexasFlood/apps/nfie/install
  modulefile: /work/projects/TexasFlood/apps/modulefiles/nfie-floodmap


proj4:
  URL: https://github.com/OSGeo/proj.4
  version: master branch version
  build script: /work/projects/TexasFlood/apps/proj4/proj4.st2.build
  install location: /work/projects/TexasFlood/apps/proj4/install
  modulefile: /work/projects/TexasFlood/apps/modulefiles/proj4


spatialite:
  URL: https://www.gaia-gis.it/fossil/libspatialite/index
  version: 4.3.0a
  build script: /work/projects/TexasFlood/apps/spatialite/spatialite.st2.build
  install location: /work/projects/TexasFlood/apps/spatialite/install
  modulefile: /work/projects/TexasFlood/apps/modulefiles/spatialite


sqlite:
  URL: https://www.sqlite.org
  version: 3.21.0
  build script: /work/projects/TexasFlood/apps/sqlite/sqlite.st2.build
  install location: /work/projects/TexasFlood/apps/sqlite/install
  modulefile: /work/projects/TexasFlood/apps/modulefiles/sqlite


taudem-kornholi:
  URL: https://github.com/kornholi/TauDEM
  version: version 5.3.8 master branch (presumably)
  build script: /work/projects/TexasFlood/apps/taudem-kornholi/taudem-kornholi.st2.build
  install location: /work/projects/TexasFlood/apps/taudem-kornholi/install
  modulefile: /work/projects/TexasFlood/apps/modulefiles/taudem-kornholi


taudem-official:
  URL: https://github.com/dtarb/TauDEM
  version: tag v5.3.8
  build script: /work/projects/TexasFlood/apps/taudem-official/taudem-official.st2.build
  install location: /work/projects/TexasFlood/apps/taudem-official/install
  modulefile: /work/projects/TexasFlood/apps/modulefiles/taudem-official


taudem-yan:
  URL: https://github.com/yanliu-chn/TauDEM/tree/CatchHydroGeo
  version: version 5.3.8 branch CatchHydroGeo
  build script: /work/projects/TexasFlood/apps/taudem-yan/taudem-yan.st2.build
  install location: /work/projects/TexasFlood/apps/taudem-yan/TauDEM  <--- due to makefile
  modulefile: /work/projects/TexasFlood/apps/modulefiles/taudem-yan

