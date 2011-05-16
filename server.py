#!/usr/bin/python2.5

import BaseHTTPServer
import CGIHTTPServer
import os
import sys

sys.path.append("server/web")
import config
Config = config.Config()
Config.loadconfig()
os.remove(".user.pickle")

os.chdir("server")
class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
	cgi_directories = ["/web"]
server = BaseHTTPServer.HTTPServer((Config.get("host"),Config.get("port")), Handler)
server.serve_forever()
