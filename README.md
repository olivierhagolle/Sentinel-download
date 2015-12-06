# S2-download
Tool to download Sentinel-2 L1C data from ESA (through wget)

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

- To see all products over Toulouse taken from Path 51, but without downloading, annd -n option
`python  S2_download.py --lat 41.6 --lon 1.44 -a apihub.txt -o 51 -n `

- 



If your download stops for a network issue, you can restart S2-download, as wget knows how to resume without havind to download everything again.
