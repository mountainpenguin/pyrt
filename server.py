#!/usr/bin/python2.5

import BaseHTTPServer
import CGIHTTPServer

class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
	cgi_directories = ["/web"]
server = BaseHTTPServer.HTTPServer(("mountainpenguin.org.uk",8000), Handler)
server.serve_forever()
