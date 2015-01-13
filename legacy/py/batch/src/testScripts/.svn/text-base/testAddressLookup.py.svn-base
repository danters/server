#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import urllib
import json
#from unidecode import unidecode

googleGeocodeUrl = "https://maps.googleapis.com/maps/api/geocode/json?latlng=45.46909063358765,-73.58929943293333&sensor=true_or_false"
res = urllib.urlopen(googleGeocodeUrl)
print str(res)

j = json.load(res)
jAddr = j["results"][0]
addr = jAddr["formatted_address"]

bla = "THIS IS A #VANY# test"

print addr

#sVar = addr.decode("utf8")
sVar = addr.encode('ascii', 'xmlcharrefreplace')
txt = bla.replace("#VANY#", sVar, 1)
print txt
