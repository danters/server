#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")

import HCommon
import HBook
import json
import HValet

HBook.clearCityBlocksData()

key = "CITY_BLOCKS"
useKey = "DEV_" + key if HCommon.isDev() else key
cb2 = HCommon.getCacheValueJson(key)
print json.dumps(cb2)
print "/n/n----------/n"


key = "CITY_BLOCK_VALETS_2"
cb1 = HCommon.getCacheValueJson(key)
print json.dumps(cb1)
print "/n/n----------/n"

#HBook.displayCityBlocksValet()

#{"dropoffLatitude":40.7590251,"dropoffLongitude":-73.97198070000002}

#NYC
#dropoffLatitude= 40.7590251	
#dropoffLongitude= -73.97198070000002

#Monmouth
#dropoffLatitude=40.36869988987455
#dropoffLongitude=-74.55325484275818

#Monmouth
dropoffLatitude=40.36877345778832
dropoffLongitude=-74.55341577529907


print "City Blocks  -------"
cb = HBook.findCityBlock(dropoffLatitude, dropoffLongitude)
print json.dumps(cb)

print "City Blocks from Cache -------"
cb = HBook.findCityBlockFromCache(dropoffLatitude, dropoffLongitude)
print json.dumps(cb)




print "Free Valets From City Blocks Cache -------"
print HBook.findFreeValetsFromCache(dropoffLatitude, dropoffLongitude)


print "Free Valets From City Blocks  -------"
print HBook.getCityBlockValets(2)

loc = HValet.getValet(4)
print str(loc)