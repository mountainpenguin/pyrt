#!/usr/bin/env python

from modules import config, indexPage

import cherrypy

c = config.Config()
c.loadconfig()

app_config = {
    "server.socket_host" : str(c.get("host")),
    "server.socket_port" : c.get("port"),
    "/css" : {
        "tools.static_filter.on" : True,
        "tools.static_filter.dir" : "static/css/",
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
    cherrypy.config.update(app_config)
    cherrypy.quickstart(mainHandler())