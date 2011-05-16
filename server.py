#!/usr/bin/env python

from modules import config, indexPage

import cherrypy
import os

c = config.Config()
c.loadconfig()

global_config = {
    "server.socket_host" : str(c.get("host")),
    "server.socket_port" : c.get("port"),
}
app_config = {
    "/css" : {
        "tools.staticdir.on" : True,
        "tools.staticdir.root" : os.getcwd(),
        "tools.staticdir.dir" : "static/css/",
    }
}

class mainHandler:
    def index(self, password=None, view=None, sortby=None, reverse=None):
        print "index called"
        #call indexPage
        Index = indexPage.Index()
        return Index.index(password, view, sortby, reverse)
        
    index.exposed = True

if __name__ == "__main__":
    cherrypy.config.update(global_config)
    cherrypy.quickstart(mainHandler(), config=app_config)