#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

import os,sys
import optparse
from xml.dom import minidom

###########################################################################
class OptionParser (optparse.OptionParser):
 
    def check_required (self, opt):
      option = self.get_option(opt)
 
      # Assumes the option's 'default' is set to None!
      if getattr(self.values, option.dest) is None:
          self.error("%s option not supplied" % option)
 
###########################################################################

url_search="https://scihub.esa.int/apihub/search?q="

#==================
#parse command line
#==================
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print '      '+sys.argv[0]+' [options]'
    print "     Aide : ", prog, " --help"
    print "        ou : ", prog, " -h"
    print "example python  %s --lat 43.6 --lon 1.44 -a apihub.txt (scene)"%sys.argv[0]
    sys.exit(-1)
else:
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)
    parser.add_option("--lat", dest="lat", action="store", type="float", \
            help="latitude in decimal degrees",default=None)
    parser.add_option("--lon", dest="lon", action="store", type="float", \
            help="longitude in decimal degrees",default=None)
    parser.add_option("--latmin", dest="latmin", action="store", type="float", \
            help="min latitude in decimal degrees",default=None)
    parser.add_option("--latmax", dest="latmax", action="store", type="float", \
            help="max latitude in decimal degrees",default=None)
    parser.add_option("--lonmin", dest="lonmin", action="store", type="float", \
            help="min longitude in decimal degrees",default=None)
    parser.add_option("--lonmax", dest="lonmax", action="store", type="float", \
            help="max longitude in decimal degrees",default=None)

    parser.add_option("-d", "--start_date", dest="start_date", action="store", type="string", \
            help="start date, fmt('2015-12-22')",default=None)
    parser.add_option("-f","--end_date", dest="end_date", action="store", type="string", \
            help="end date, fmt('2015-12-23')",default=None)
    parser.add_option("-o","--orbit", dest="orbit", action="store", type="int", \
            help="Orbit Number", default=None)			
    parser.add_option("-a","--apihub_passwd", dest="apihub", action="store", type="string", \
            help="ESA apihub account and password file")
    parser.add_option("-p","--proxy_passwd", dest="proxy", action="store", type="string", \
            help="Proxy account and password file",default=None)
    parser.add_option("-n","--no_download", dest="no_download", action="store_true",  \
            help="Do not download products, just print wget command",default=False)
    parser.add_option("-m","--max_cloud", dest="max_cloud", action="store",type="float",  \
            help="Do not download products with more cloud percentage ",default=110)
    parser.add_option("-w","--write_dir", dest="write_dir", action="store",type="string",  \
            help="Path where the products should be downloaded",default='.')


    (options, args) = parser.parse_args()
    if options.lat==None or options.lon==None:
        if options.latmin==None or options.lonmin==None or options.latmax==None or options.lonmax==None:
            print "provide at least a point or  rectangle"
            sys.exit(-1)
        else:
            geom='rectangle'
    else:
        if options.latmin==None and options.lonmin==None and options.latmax==None and options.lonmax==None:
            geom='point'
        else:
            print "please choose between point and rectance, but not both"
            sys.exit(-1)
            
    parser.check_required("-a")        

#====================
# read password file
#====================
try:
    f=file(options.apihub)
    (account,passwd)=f.readline().split(' ')
    if passwd.endswith('\n'):
        passwd=passwd[:-1]
    f.close()
except :
    print "error with usgs password file"
    sys.exit(-2)

			

#==================================================
#      prepare wget command line to search catalog
#==================================================

wg="wget --no-check-certificate"
auth='--user="%s" --password="%s"'%(account,passwd)
search_output="--output-document=query_results.xml"



if geom=='point':
    query_geom='footprint:\\"Intersects(%f,%f)\\"'%(options.lat,options.lon)
elif geom=='rectangle':
    query_geom='footprint:\\"Intersects(POLYGON(({lonmin} {latmin}, {lonmax} {latmin}, {lonmax} {latmax}, {lonmin} {latmax},{lonmin} {latmin})))\\"'.format(latmin=options.latmin,latmax=options.latmax,lonmin=options.lonmin,lonmax=options.lonmax)
    

if options.orbit==None:
    query='%s filename:S2A*'%(query_geom)
else :
    query='%s filename:S2A*R%03d*'%(query_geom,options.orbit)


if options.start_date!=None:    
    start_date=options.start_date+"T00:00:00.000Z"
    if options.end_date!=None:
        end_date=options.end_date+"T23:59:50.000Z"
    else:
        end_date="NOW"

    query_date=" ingestiondate:[%s TO %s]"%(start_date,end_date)
    query=query+query_date

commande_wget='%s %s %s "%s%s"'%(wg,auth,search_output,url_search,query)
print commande_wget
os.system(commande_wget)

"Intersects(POLYGON((-4.53 29.85, 26.75 29.85, 26.75 46.80,-4.53 46.80,-4.53 29.85)))"

#=======================
# parse catalog output
#=======================
xml=minidom.parse("query_results.xml")
products=xml.getElementsByTagName("entry")
for prod in products:
    ident=prod.getElementsByTagName("id")[0].firstChild.data
    print ident
    link=prod.getElementsByTagName("link")[0].attributes.items()[0][1] 
    #to avoid wget to remove $ special character
    link=link.replace('$','\\$')


    for node in prod.getElementsByTagName("str"):
        (name,value)=node.attributes.items()[0]
        if value=="filename":
            filename= str(node.toxml()).split('>')[1].split('<')[0]   #ugly, but minidom is not straightforward
        elif value=="s2datatakeid":
            datatakeid=str(node.toxml()).split('>')[1].split('<')[0]

    for node in prod.getElementsByTagName("double"):
        (name,value)=node.attributes.items()[0]
        if value=="cloudcoverpercentage":
            cloud=float((node.toxml()).split('>')[1].split('<')[0])

    print "==============================================="
    print filename        
    print link
    print "cloud percentage = %5.2f %%"%cloud
    print "date de prise de vue",datatakeid
    print "==============================================="
  

    #==================================download product
    if cloud<options.max_cloud :
        commande_wget='%s %s --continue --output-document=%s/%s "%s"'%(wg,auth,options.write_dir,filename+".zip",link)
        #do not download the product if it was already downloaded and unzipped, or if no_download option was selected.
        unzipped_file_exists= os.path.exists(("%s/%s")%(options.write_dir,filename))
        if unzipped_file_exists==False and options.no_download==False:
            os.system(commande_wget)

    else :
        print "too many clouds to download this product" 
