# S2-download
Tool to download Sentinel-2 L1C data from ESA (through wget)
(http://olivierhagolle.github.io/Sentinel-2-download)

This module searches the ESA apihub catalog and downloads the products which fit the criteria defined in the command line.
You can select by :
- coordinates of a point (soon a rectangle)
- path number (sometimes, a point can be observed from several paths
- date, of course

Here are a few examples :
- To download all the products over Toulouse

`python  %s --lat 43.6 --lon 1.44 -a apihub.txt (scene)"%sys.argv[0]`

- To download all products over Toulouse taken from Path 51

`python  S2_download.py --lat 41.6 --lon 1.44 -a apihub.txt -o 51 `

- To see all products over Toulouse taken from Path 51, but without downloading, thanks to -n option

`python  S2_download.py --lat 41.6 --lon 1.44 -a apihub.txt -o 51 -n `

- To see all products in a rectangle and download only those with a small percentage of clouds :

`python  S2_download.py --latmin 43 --latmax 46 --lonmin -1 --lonmax 2 -a apihub.txt -o 94 -m 23 -d 2015-12-06 -n`

- to download al products above Toulouse downlaoded after 2015-12-06

`python  S2_download.py --lat 46.6 --lon 1.44 -a apihub.txt -o 94 -d 2015-12-06`



If your download stops for a network issue, you can restart S2-download, as wget knows how to resume without havind to download everything again.
