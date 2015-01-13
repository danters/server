#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HCommon
import memcache
import time

f = open("testResult.txt","w")
f.write("Content-Type: text/plain;charset=utf-8\n")

f.write("\n==========\n==========\n")
f.write("\nEnvironment: " + HCommon.ENV + ", isDev=" + str(HCommon.isDev()))
mc = HCommon.getMemCache()
useKey = "testingKey"
value = "testValue"

t0 = time.time()

mc.set(useKey, value, time=1209600)

retValue = mc.get(useKey)

t1 = time.time()
total = t1-t0

print retValue + ", " + str(total)


t0 = time.time()
HCommon.setCacheValue("testAgain", "oh boy")
t1 = time.time()
total = t1-t0
retValue = HCommon.getCacheValue("testAgain")
print retValue + ", " + str(total)
