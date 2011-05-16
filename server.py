#!/usr/bin/env python

from modules import config, indexPage

import cherrypy

c = config.Config()
c.loadconfig()

app_config = {
    "server.socket_host" : c.get("host"),
    "server.socket_port" : c.get("port"),
}

class mainHandler:
    @cherrypy.exposed
    def index(self, password=None, view=None, sortby=None, reverse=None):
        #call indexPage
        return indexPage.Index(password, view, sortby, reverse)
        
cherrypy.root = mainHandler()

if __name__ == "__main__":
    cherrypy.config.update(app_config)
    cherrypy.server.start()