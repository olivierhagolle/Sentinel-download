# Sentinel-download
### Description
Tool to download Sentinel data from ESA (through wget)
(http://olivierhagolle.github.io/Sentinel-2-download)

The ESA Sentinel distribution website allows you to perform catalog searches through http requests. This blog post shows [a few examples](http://www.cesbio.ups-tlse.fr/multitemp/?p=6419). 

This module searches the ESA apihub catalog and downloads the products which fit the criteria defined in the command line.
You can select by :
- coordinates of a point, or of a rectangle
- path number (sometimes, a point can be observed from several paths
- date, of course

This tool was written thanks to ESA well documented scihub API : https://scihub.esa.int/userguide/5APIsAndBatchScripting

### wget
To use it, you need *wget* installed. I guess it goes with any linux distribution. For windows, I don't know, but maybe someone can tell.
If your download stops for a network issue, you can restart S2-download, as wget knows how to resume without havind to download everything again. Wget doesnot download the products already fully downloaded (unlesss you have unzipped them).

### Proxy
In case your download must be done through a proxy, you have to setup the https_proxy variable in your.bashrc file or in your .profile.

Proxy with password :

`export https_proxy = http://uname:passwd@proxy.truc.fr:8080`

Proxy without password :

`export https_proxy = http://proxy.truc.fr:8080`

### Examples
#### S2 examples
Here are a few examples for Sentinel-2
- To download all the products over Toulouse

`python  %s --lat 43.6 --lon 1.44 -a apihub.txt (scene)"%sys.argv[0]`

- To download all products over Toulouse taken from Path 51

`python  Sentinel_download.py --lat 41.6 --lon 1.44 -a apihub.txt -o 51 -s S2`

- To see all products over Toulouse taken from Path 51, but without downloading, thanks to -n option

`python  Sentinel_download.py --lat 41.6 --lon 1.44 -a apihub.txt -o 51 -n -s S2`

- To see all products in a rectangle and download only those with a small percentage of clouds :

`python  Sentinel_download.py --latmin 43 --latmax 46 --lonmin -1 --lonmax 2 -a apihub.txt -o 94 -m 23 -d 2015-12-06 -n -s S2`

- to download al products above Toulouse downlaoded after 2015-12-06

`python  Sentinel_download.py --lat 46.6 --lon 1.44 -a apihub.txt -o 94 -d 2015-12-06 -s S2`

- you may also change the output directory with the -w option

`python  Sentinel_download.py --lat 46.6 --lon 1.44 -a apihub.txt -o 94 -d 2015-12-06 -w /mnt/data/Sentinel-2/ -s S2`

#### S1 examples :
- To download Sentinel-1 SLC products above a rectangle in France 


`python  Sentinel_download.py --latmin 43 --latmax 46 --lonmin -1 --lonmax 2 -a apihub.txt   -n -s S1A*SLC`

- for other examples see Sentinel-2 examples

#### authentification
The scihub site accepts the "guest" account and "guest" password, as provided in the `apihub.txt` file. But only two downloads at the same time are allowed worldwide on the same account. So do not forget to enter your own account and password in the password file provided in the -a option.


However, please also note that ESA has currently limited the acces to the early registrated users : 

        The API Hub Access is currently available only for users registered before the 20th of November 12:00 UTC, the user credentials as of the 20th November are valid to access this site.
