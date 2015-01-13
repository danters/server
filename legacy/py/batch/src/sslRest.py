#!/usr/bin/python
# -*- coding: UTF-8 -*-
import tornado.ioloop
import tornado.httpserver
import tornado.web
import os

settings = dict(
    ssl_options = {
        "certfile": os.path.join("/srv/www/devweb/sslcerts/277335a132190b.crt"),
        "keyfile": os.path.join("/srv/www/devweb/sslcerts/valetanywhere.pem"),
    }
)

class RestHandler(tornado.web.RequestHandler):
    #@tornado.web.asynchronous
    def post(self):
        """Post new data to our rest service as a JSON"""
        function=self.get_argument("function", None, True)
        app=self.get_argument("app", None, True)
        
        print "receiving...." + str(self.request)
        
        j = self.json_args
        
        headers = self.request.headers
        referer = ""
        if "Referer" in headers:
            referer = headers["Referer"]
        
        #writeLog(app + ", " + function + ": " + str(self.json_args) +  ", " + referer)
        print str(self.json_args)
        
        ret = {}
        ret = j
        

        sRet="Request for " + function + " unsupported"
        #if len(ret) > 0:
        #    sRet = json.dumps(ret)
    
        self.set_header("Content-Type", "text/plain; charset=utf-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Headers', 'accept, origin, x-requested-with, x-csrftoken, content-type, email, personId, authToken')
        
        self.set_status(200)
        self.write(sRet)

    def options(self):
        print "options hit"
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Headers', 'accept, origin, x-requested-with, x-csrftoken, content-type, email, personId, authToken')
        
        self.set_status(200)
        
    def prepare(self):
        try:
            print "body=" + str(self.request.body)
            self.json_args = json.loads(self.request.body)
        
        except:
            self.json_args = None
            
    get = post


http_server = tornado.httpserver.HTTPServer(tornado.web.Application([(r"/rest", RestHandler), ]), settings)
#http_server = tornado.httpserver.HTTPServer(tornado.web.Application([(r"/rest", RestHandler), ]))
#http_server = tornado.httpserver.HTTPServer(tornado.web.Application(handlers), settings)

print "starting server"
http_server.listen(8787)
tornado.ioloop.IOLoop.instance().start()
print "server started"
    