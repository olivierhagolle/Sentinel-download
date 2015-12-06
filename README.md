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

If your download stops for a network issue, you can restart S2-download, as wget knows how to resume without havind to download everything again.
