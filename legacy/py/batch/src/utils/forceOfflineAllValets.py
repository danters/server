#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.insert(0, "/srv/www/devweb/batch")
import HValet
import HCommon
import json

def makeValetOffline(cityBlockId):
    valets=HCommon.execProcManyRow("call ReadCityBlockValet(%s)",(str(cityBlockId)))

    if valets is None:
        print "No valets"
        return
    
    for lPersonId in valets:
        personId = lPersonId[0]
        print "processing valet " + str(personId)
        
        v = HValet.getValet(personId)
        print str(v)
        if v is not None:
            if v['state']== HValet.VALET_STATE_READY:
                v['state']= HValet.VALET_STATE_NOT_READY
                sValet = json.dumps(v)
                HValet.setValet(personId, sValet)
                
cityBlockId = 4

makeValetOffline(cityBlockId)
print "Valets are forced offline"
