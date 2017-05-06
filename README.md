# Sentinel-download
### Description
Tool to download Sentinel data from ESA (using the wget or aria2 downloaders). This tool can download whole products or only one tile per product, with the -t option (http://olivierhagolle.github.io/Sentinel-download). It should work both on windows and linux.

The ESA Sentinel distribution website allows you to perform catalog searches through http requests. This blog post shows [a few examples](http://www.cesbio.ups-tlse.fr/multitemp/?p=6419). 

Sentinel-download searches the ESA apihub catalog and downloads the products which fit the criteria defined in the command line. You can select products by :
- coordinates of a point, or of a rectangle
- path number (sometimes, a point can be observed from several paths
- date, of course

This tool was written thanks to ESA well documented scihub API : https://scihub.copernicus.eu/userguide/5APIsAndBatchScripting.

To use this tool, you need a scihub account obtained a long time in advance (see below). If you do not have such an account, or if you want to try a faster access, you might consider downloading the products from the [French collaborative ground segment PEPS](https://github.com/olivierhagolle/peps_download).

### wget /aria2
To use it, you need either to have *wget* or *aria2* installed. I guess it goes with any linux distribution. For windows users, first install aria2 (https://aria2.github.io).
If your download stops for a network issue, you can restart S2-download, as wget knows how to resume without havind to download everything again. Wget doesnot download the products already fully downloaded (unlesss you have unzipped them).

wget is the downloader by default, If you want to use aria2, add `--downloader aria2` in your command line

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

`python  Sentinel_download.py --lat 43.6 --lon 1.44 -a apihub.txt -o 51 -s S2`

- To download all L2A products over Toulouse 

`python  Sentinel_download.py --lat 43.6 --lon 1.44 -a apihub.txt -l L2A -s S2`

- To download all products over Toulouse taken from Path 51 with aria2 for windows

`python  Sentinel_download.py --downloader aria2 --lat 43.6 --lon 1.44 -a apihub.txt -o 51 -s S2`

- To see all products over Toulouse taken from Path 51, but without downloading, thanks to -n option

`python  Sentinel_download.py --lat 43.6 --lon 1.44 -a apihub.txt -o 51 -n -s S2`

- To see all products in a rectangle and download only those with a small percentage of clouds :

`python  Sentinel_download.py --latmin 43 --latmax 46 --lonmin -1 --lonmax 2 -a apihub.txt -o 94 -m 23 -d 2015-12-06 -n -s S2`

- to download all products above Toulouse acquired after 2015-12-26 (December 26th) and before 2016-01-01

`python  Sentinel_download.py --lat 43.6 --lon 1.44 -a apihub.txt -d 20151226 -f 20160101 -s S2`

- to download all products above Toulouse ingested in November 2016 (note thedate format is different)

`python  Sentinel_download.py --lat 43.6 --lon 1.44 -a apihub.txt --id 2016-11-01 --if 2016-12-01 -s S2`

- to download all products above Toulouse acquired after 2015-12-26 (December 26th)

`python  Sentinel_download.py --lat 43.6 --lon 1.44 -a apihub.txt -o 51 -d 20151226 -s S2`

- you may also change the output directory with the -w option

`python  Sentinel_download.py --lat 43.6 --lon 1.44 -a apihub.txt -o 51 -d 20151226 -w /mnt/data/Sentinel-2/ -s S2`

- and finally, you may download only one tile from the product (the one which contains Toulouse for instance)
`python  Sentinel_download.py --lat 43.6 --lon 1.44 -a apihub.txt -o 51 -t 31TCJ`

#### S1 examples :
- To download Sentinel-1 SLC products above a rectangle in France 


`python  Sentinel_download.py --latmin 43 --latmax 46 --lonmin -1 --lonmax 2 -a apihub.txt    -s S1A*SLC`

- for other examples see Sentinel-2 examples

#### authentification
The scihub site accepts the "guest" account and "guest" password, as provided in the `apihub.txt` file. But only two downloads at the same time are allowed worldwide on the same account. So do not forget to enter your own account and password in the password file provided in the -a option.


However, please also note that ESA has currently limited the acces to users registered some time ago.

In December :
`The API Hub Access is currently available only for users registered before the 20th of November 12:00 UTC, the user credentials as of the 20th November are valid to access this site.`
        
In January :
` The API Hub Access is currently available only for users registered on SciHub before the 21st of December 16:46 UTC. The same user credentials are valid to access this site.`

If you do not have such an account, you might consider downloading the products from the [French collaborative ground segment PEPS](https://github.com/olivierhagolle/peps_download).

#### Issues

##### Maximum of concurrent flows
- One of my accounts always yields the same message :
`wget --no-check-certificate --user="hagolle" --password="very_secret" --continue --output-document=./S2A_OPER_PRD_MSIL1C_PDMC_20160119T202641_R008_V20160119T105107_20160119T105107.SAFE.zip "https://scihub.copernicus.eu/apihub/odata/v1/Products('bcf1f9a1-c43d-4e2d-8924-f90662acdc49')/\$value"
> 2016-01-30 17:09:02 ERREUR 500: Internal Server Error. `

If I use the URL in firefox, I get the following message, which is not true, I have no other download on-going.

`<error><code/><message xml:lang="en">An exception occured while creating a stream : Maximum number of 2 concurrent flows achieved by the user "hagolle"</message></error>`

I have found a workaround with the --dhus option.


