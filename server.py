#!/usr/bin/env python

import BaseHTTPServer
import CGIHTTPServer

server = BaseHTTPServer.HTTPServer(("mountainpenguin.org.uk",8000), CGIHTTPServer.CGIHTTPRequestHandler)
server.serve_forever()
