#!/usr/bin/python2.5

import BaseHTTPServer
import CGIHTTPServer
import os
import sys
os.chdir("server")
import web.config as config
Config = config.Config()
Config.loadconfig()

Config.test()
class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
	cgi_directories = ["/web"]
server = BaseHTTPServer.HTTPServer(("mountainpenguin.org.uk",Config.get("port")), Handler)
server.serve_forever()
