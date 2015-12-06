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
url_download="https://scihub.esa.int/apihub/"
#user="hagolle"
#pwd="seriestemporelles"

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
            help="latitude in decimal degrees")
    parser.add_option("--lon", dest="lon", action="store", type="float", \
            help="longitude in decimal degrees")
    parser.add_option("-d", "--start_date", dest="start_date", action="store", type="string", \
            help="start date, fmt('2015-12-222')",default=None)
    parser.add_option("-f","--end_date", dest="end_date", action="store", type="string", \
            help="end date, fmt('2015-12-23')",default=None)
    parser.add_option("-o","--orbit", dest="orbit", action="store", type="int", \
            help="Orbit Number", default=None)			
    parser.add_option("-a","--apihub_passwd", dest="apihub", action="store", type="string", \
            help="ESA apihub account and password file")
    parser.add_option("-p","--proxy_passwd", dest="proxy", action="store", type="string", \
            help="Proxy account and password file",default=None)


    (options, args) = parser.parse_args()
    parser.check_required("--lat")
    parser.check_required("--lon")        
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


if options.orbit==None:
    query='footprint:\\"Intersects(%f,%f)\\" filename:S2A*'%(options.lat,options.lon)
else :
    query='footprint:\\"Intersects(%f,%f)\\" filename:S2A*R%03d*'%(options.lat,options.lon,options.orbit)


if options.start_date!=None:    
    start_date=options.start_date+"T00:00:00.000Z"
    if options.end_date!=None:
        end_date=options.end_date+"T00:00:00.000Z"
    else:
        end_date="NOW"

    query_date=" ingestiondate:[%s TO %s]"%(start_date,start_date)
    query=query+query_date

commande_wget='%s %s %s "%s%s"'%(wg,auth,search_output,url_search,query)
print commande_wget
os.system(commande_wget)


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
            cloud=str(node.toxml()).split('>')[1].split('<')[0]

    print "==============================================="
    print filename        
    print link
    print "cloud percentage = %5.2f %%",cloud
    print "date de prise de vue",datatakeid
    print "==============================================="
  

    #==================================download product
    commande_wget='%s %s --continue --output-document=%s "%s"'%(wg,auth,filename+".zip",link)
    print commande_wget
    os.system(commande_wget)


"""
  

https://scihub.esa.int/dhus/odata/v1/Products?$format=xml
https://scihub.esa.int/apihub/odata/v1/Products?$format=xml

https://scihub.esa.int/apihub/odata/v1/Products?$format=xml

https://scihub.copernicus.eu/s2/odata/v1/Products(%27ca9c4480-55ef-4df1-b400-fa58fae08927%27)/$value

https://scihub.esa.int/apihub/odata/v1/Products?$orderby=IngestionDate%20desc&$top=100

https://scihub.esa.int/apihub/odata/v1/Products?$filter=year(ContentDate/Start) eq 2015 and month(ContentDate/Start) eq 12 and day(ContentDate/Start) eq 03

https://scihub.esa.int/apihun/search?q=S2 AND orbitnumber:051

https://scihub.esa.int/apihub/search?q=filename:S2A*20151203*R051*
https://scihub.esa.int/apihub/search?q=footprint:"Intersects(43.6000, 1.44)" filename:S2A*

https://scihub.esa.int/apihub/odata/v1/Products(%27c90770da-dba6-4129-89dc-1abb1d873bee%27)/$metadata


"""
