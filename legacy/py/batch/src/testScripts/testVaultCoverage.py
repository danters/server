#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HBook


HBook.clearVaultCoverage()

j={}
j["latitude"] = 40.759184
j["longitude"] = -73.971763

print "requesting a valid location"
ret = HBook.readVaultCoverage(j)
print str(ret)


print "requesting a invalid location"
j["longitude"] = -79.971763
ret2 = HBook.readVaultCoverage(j)
print str(ret2)