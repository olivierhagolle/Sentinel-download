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


#get URL, name and type within xml file from Scihub
def get_elements(xml_file):
    urls=[]
    contentType=[]
    name=[]
    with open(xml_file) as fic:
        line=fic.readlines()[0].split('<entry>')
        for fragment in line[1:]:
            urls.append(fragment.split('<id>')[1].split('</id>')[0])
            contentType.append(fragment.split('<d:ContentType>')[1].split('</d:ContentType>')[0])
            name.append(fragment.split('<title type="text">')[1].split('</title>')[0])
            #print name
    os.remove(xml_file)
    return urls,contentType,name

# recursively download file tree of a Granule
def download_tree(rep,xml_file,wg,auth):
    urls,types,names=get_elements(xml_file)
    for i in range(len(urls)):
        if types[i]=='Item':
            nom_rep="%s/%s"%(rep,names[i])
            if not(os.path.exists(nom_rep)):
                os.mkdir(nom_rep)
            commande_wget='%s %s --continue --output-document=%s "%s"'%(wg,auth,'files.xml',urls[i]+"/Nodes")
            print commande_wget
            os.system(commande_wget)
            download_tree(nom_rep,'files.xml',wg,auth)
        else:                       
            commande_wget='%s %s --continue --output-document=%s "%s"'%(wg,auth,rep+'/'+names[i],urls[i]+'/\\$value')
            os.system(commande_wget)           


##########################################################################




url_search="https://scihub.copernicus.eu/apihub/search?q="

#==================
#parse command line
#==================
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print '      '+sys.argv[0]+' [options]'
    print "     Aide : ", prog, " --help"
    print "        ou : ", prog, " -h"
    print "example python  %s --lat 43.6 --lon 1.44 -a apihub.txt "%sys.argv[0]
    print "example python  %s --lat 43.6 --lon 1.44 -a apihub.txt -t 31TCJ "%sys.argv[0]
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
    parser.add_option("-s","--sentinel", dest="sentinel", action="store",type="string",  \
            help="Sentinel mission considered",default='S2')
    parser.add_option("-t","--tile", dest="tile", action="store",type="string",  \
            help="Sentinel-2 Tile number",default=None)
    parser.add_option("--dhus",dest="dhus",action="store_true",  \
            help="Try dhus interface when apihub is not working",default=False)
    parser.add_option("-r",dest="MaxRecords",action="store",type="int",  \
            help="maximum number of records to download (default=100)",default=100)


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
    if options.tile!=None and options.sentinel!='S2':
        print "The tile option (-t) can only be used for Sentinel-2"
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
    print "error with password file"
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
    query='%s filename:%s*'%(query_geom,options.sentinel)
else :
    query='%s filename:%s*R%03d*'%(query_geom,options.sentinel,options.orbit)


if options.start_date!=None:    
    start_date=options.start_date+"T00:00:00.000Z"
    if options.end_date!=None:
        end_date=options.end_date+"T23:59:50.000Z"
    else:
        end_date="NOW"

    query_date=" ingestiondate:[%s TO %s]"%(start_date,end_date)
    query=query+query_date

commande_wget='%s %s %s "%s%s&rows=%d"'%(wg,auth,search_output,url_search,query,options.MaxRecords)
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

    #print what has been found
    print "\n==============================================="
    print filename        
    print link
    if options.dhus==True:
        link=link.replace("apihub","dhus")

    if options.sentinel.find("S2") >=0 :
        for node in prod.getElementsByTagName("double"):
            (name,value)=node.attributes.items()[0]
            if value=="cloudcoverpercentage":
                cloud=float((node.toxml()).split('>')[1].split('<')[0])
            print "cloud percentage = %5.2f %%"%cloud
    else:
        cloud=0
    print "===============================================\n"

  

    #==================================download product
    if( cloud<options.max_cloud or (options.sentinel.find("S1")>=0)) and options.tile==None:
        commande_wget='%s %s --continue --output-document=%s/%s "%s"'%(wg,auth,options.write_dir,filename+".zip",link)
        #do not download the product if it was already downloaded and unzipped, or if no_download option was selected.
        unzipped_file_exists= os.path.exists(("%s/%s")%(options.write_dir,filename))
        print commande_wget
        if unzipped_file_exists==False and options.no_download==False:
            os.system(commande_wget)

    # download only one tile, file by file.        
    elif options.tile!=None:
        #find URL of header file
        url_file_dir=link.replace('\$value',"Nodes('%s')/Nodes"%(filename))
        commande_wget='%s %s --continue --output-document=%s "%s"'%(wg,auth,'file_dir.xml',url_file_dir)
        os.system(commande_wget)
        urls,types,names=get_elements('file_dir.xml')
        #search for the xml file
        for i in range(len(urls)):
            if names[i].find('SAFL1C')>0:
                xml=names[i]
                url_header=urls[i]
        
        #retrieve list of granules
        url_granule_dir=link.replace('\$value',"Nodes('%s')/Nodes('GRANULE')/Nodes"%(filename))
        print url_granule_dir
        commande_wget='%s %s --continue --output-document=%s "%s"'%(wg,auth,'granule_dir.xml',url_granule_dir)
        os.system(commande_wget)
        urls,types,names=get_elements('granule_dir.xml')
        granule=None
        #search the tile
        for i in range(len(urls)):
            if names[i].find(options.tile)>0:
                granule=names[i]
        if granule==None:
	    print "========================================"
            print "Tile %s is not available within product"%options.tile
	    print "========================================"	    
	else :
	    #create tile directory
	    nom_rep_tuile=("%s/%s"%(options.write_dir,granule))
	    if not(os.path.exists(nom_rep_tuile)) :
		os.mkdir(nom_rep_tuile)
	    # download product header file
	    commande_wget='%s %s --continue --output-document=%s "%s"'%(wg,auth,nom_rep_tuile+'/'+xml,url_header+"/\\$value")
	    os.system(commande_wget)

	    # granule files
	    url_granule="%s('%s')/Nodes"%(url_granule_dir,granule)
	    commande_wget='%s %s --continue --output-document=%s "%s"'%(wg,auth,'granule.xml',url_granule)
	    print commande_wget
	    os.system(commande_wget)
	    download_tree(options.write_dir+'/'+granule,"granule.xml",wg,auth)
        
    else :
        print "too many clouds to download this product" 
