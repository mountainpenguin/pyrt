#!/usr/bin/env python

""" Copyright (C) 2012 mountainpenguin (pinguino.de.montana@googlemail.com)
    <http://github.com/mountainpenguin/pyrt>
    
    This file is part of pyRT.

    pyRT is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pyRT is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pyRT.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
from modules import login
from modules import rtorrent
from modules import weblog 
from modules import indexPage, detailPage, ajaxPage  # pages
from modules import optionsPage, rssPage, statsPage

import tornado.ioloop as ioloop
import tornado.web as web
import tornado.httpserver as httpserver
import tornado.websocket as websocket
import tornado.options
import os
import urlparse
import json
import base64
import logging
import signal
import traceback

class null(object):
    @staticmethod
    def func(*args, **kwargs):
        return None
    
class _check(object):
    @staticmethod
    def web(obj):
        passw = obj.get_argument("password", None)
        cookie = obj.cookies
        cCheck = obj.application._pyrtL.checkLogin(cookie, obj.request.remote_ip)
        if not cCheck and not passw:
            return (False, "")
        elif not cCheck and passw:
            pCheck = obj.application._pyrtL.checkPassword(passw, obj.request.remote_ip)
            if pCheck:
                return (True, True) # set cookie
            else:
                return (False, "Incorrect Password")
        else:
            return (True, False)

    @staticmethod
    def socket(obj):
        cookie = obj.cookies
        cCheck = obj.application._pyrtL.checkLogin(cookie, obj.request.remote_ip)
        if not cCheck:
            return False
        else:
            return True

class Socket(object):
    def __init__(self, socketID, socketType, socketObject, session, callback):
        self.socketID = socketID
        self.socketType = socketType
        self.socketObject = socketObject
        self.session = session
        self.callback = callback
    
class SocketStorage(object):
    def __init__(self):
        self.LOG = {}
        self.AJAX = {}
        self.FILE = {}
        self.STAT = {}
    
    def add(self, socketID, socketType, socketObject, session, callback=null.func):
        if socketType == "logSocket":
            self.LOG[socketID] = Socket(socketID, socketType, socketObject, session, callback)
            
    def remove(self, socketID):
        if socketType == "logSocket" and socketID in self.LOG:
            del self.LOG[socketID]
            
    def get_type(self, socketType, session=None):
        if session:
            if socketType == "logSocket":
                return filter(lambda x: x.session==session, self.LOG.values())
        else:
            if socketType == "logSocket":
                return self.LOG.values()
                
    def get_session(self, session):
        return filter(lambda x: x.session==session, self.LOG.values() + self.AJAX.values() + self.FILE.values() + self.STAT.values())

class index(web.RequestHandler):
    """Default page handler for /
    
        Writes indexPage.Index.index() if user is logged in
        else writes login page
    """
    def get(self):
        chk = _check.web(self)
        if not chk[0]:
            self.write(self.application._pyrtL.loginHTML(chk[1]))
            return
        elif chk[0] and chk[1]:
            self.set_cookie("sess_id", self.application._pyrtL.sendCookie(self.request.remote_ip))

        view = self.get_argument("view", None)
        sortby = self.get_argument("sortby", None)
        reverse = self.get_argument("reverse", None)

        self.write(self.application._pyrtINDEX.index(view, sortby, reverse))

        
    post = get
    
class detail(web.RequestHandler):
    """ *** DEPRECATED DO NOT USE *** Detailed page view handler (/detail)
        
        Retrieves detailPage.Detail() passing the torrent_id argument.
        This has attribute HTML, which is written.
    """
    def get(self):
        view = self.get_argument("view", None)
        torrent_id = self.get_argument("torrent_id", None)
        password = self.get_argument("password", None)
        
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck and not password:
            self.write(self.application._pyrtL.loginHTML())
            return
        elif not Lcheck and password:
            Pcheck = self.application._pyrtL.checkPassword(password, self.request.remote_ip)
            if Pcheck:
                #set cookie
                self.set_cookie("sess_id", self.application._pyrtL.sendCookie(self.request.remote_ip))
            else:
                self.write(self.application._pyrtL.loginHTML("Incorrect Password"))
                return
            
        Detail = detailPage.Detail(torrent_id, conf=self.application._pyrtGLOBALS["config"])
        self.write(Detail.HTML)
        
    post = get
    
class ajax(web.RequestHandler):
    """Handler for ajax queries (/ajax)
            
    """
    def get(self):
        qs = self.request.arguments
        request = qs.get("request", [None])[0]
        if not request:
            raise web.HTTPError(400, log_message="Error, no request specified")

        chk = _check.web(self)
        if not chk[0]:
            self.write("Session Ended")
            return

                
        if not self.application._pyrtAJAX.has_command(request):
            raise web.HTTPError(400, log_message="Error Invalid Method")
        if not self.application._pyrtAJAX.validate_command(request, qs):
            raise web.HTTPError(400, log_message="Error need more args")
        if request == "upload_torrent":
            try:
                qs["torrent"] = self.request.files["torrent"]
            except:
                raise web.HTTPError(400, log_message="No torrent specified for upload")
                
        resp = self.application._pyrtAJAX.handle(request, qs)
        if resp:
            self.write(resp)
        
    post = get
    
class options(web.RequestHandler):
    """Handler for options page view (/options)
            
            *** Currently a work in progress ***
            Can only be viewed if "test" is passed as an argument.
            If it is, writes optionsPage.Options.index()
    """
    def get(self):
        chk = _check.web(self)
        if not chk[0]:
            self.write(self.application._pyrtL.loginHTML(chk[1]))
            return
        elif chk[0] and chk[1]:
            self.set_cookie("sess_id", self.application._pyrtL.sendCookie(self.request.remote_ip))

        test = self.get_argument("test", False)
        if not test:
            try:
                link = self.request.headers["Referer"]
            except KeyError:
                link = "/index"
            self.write("""
                        <html>
                            <head>
                                <title>Options</title>
                                <link rel="stylesheet" type="text/css" href="/css/main.css">
                            </head>
                            <body>
                                <div style="background-color : white; padding : 2em;">
                                    <div>Nothing here yet</div>
                                    Go back to <a style="color:black;" href="%(link)s">%(link)s</a>
                                </div>
                            </body>
                        </html>
                       """ % {"link" : link})
            return
        else:
            self.write(self.application._pyrtOPTIONS.index())

    post = get
   
class logHandler(web.RequestHandler):
    def get(self):
        chk = _check.web(self)
        if not chk[0]:
            self.write(self.application._pyrtL.loginHTML(chk[1]))
            return
        elif chk[0] and chk[1]:
            self.set_cookie("sess_id", self.application._pyrtL.sendCookie(self.request.remote_ip))

        logHTML = self.application._pyrtLog.html()
        with open("htdocs/logHTML.tmpl") as template:
            self.write(template.read() % {"logHTML":logHTML})

    post = get

class RSS(web.RequestHandler):
    def get(self):
        chk = _check.web(self)
        if not chk[0]:
            self.write(self.application._pyrtL.loginHTML(chk[1]))
            return
        elif chk[0] and chk[1]:
            self.set_cookie("sess_id", self.application._pyrtL.sendCookie(self.request.remote_ip))

        self.write(self.application._pyrtRSS_PAGE.index())
        
class ajaxSocket(websocket.WebSocketHandler):
    def open(self):
        if not _check.socket(self):
            logging.error("%d %s %.2fms", self.get_status(), "ajaxSocket denied", 1000*self.request.request_time())
            self.close()
            return
        logging.info("%d %s (%s)", self.get_status(), "ajaxSocket opened", self.request.remote_ip)

    def on_message(self, message):
        if not _check.socket(self):
            logging.error("%d %s %.2fms", self.get_status(), "ajaxSocket message denied", 1000*self.request.request_time())
            self.close()
            return

        #parse out get query
        #q = urlparse.parse_qs(message)
        #request = q.get("request", [None])[0]
        #view = q.get("view", [None])[0]
        #sortby = q.get("sortby", [None])[0]
        #reverse = q.get("reverse", [None])[0]
        #drop_down_ids = q.get("drop_down_ids", [None])[0]
        #if request == "get_info_multi" and view:
        #    self.write_message(self.application._pyrtAJAX.get_info_multi(view, sortby, reverse, drop_down_ids))

        qs = urlparse.parse_qs(message)
        request = qs.get("request", [None])[0]
        if request != "get_info_multi":
            logging.info("%d %s (%s)", self.get_status(), "ajaxSocket request %s" % request, self.request.remote_ip)
        if not request:
            logging.error("%d %s (%s)", self.get_status(), "ajaxSocket error - no request specified", self.request.remote_ip)
            self.write_message("ERROR/No request specified")
            return
        
        if not self.application._pyrtAJAX.has_command(request):
            logging.error("%d %s (%s)", self.get_status(), "ajaxSocket error - no such command `%s`" % request, self.request.remote_ip)
            self.write_message("ERROR/No such command")
            return
        if not self.application._pyrtAJAX.validate_command(request, qs):
            logging.error("%d %s (%s)", self.get_status(), "ajaxSocket error - not enough args", self.request.remote_ip)
            self.write_message("ERROR/need more args")
            return
        if request == "upload_torrent":
            logging.warning("%d %s (%s)", self.get_status(), "ajaxSocket upload_torrent not supported, use POST of fileSocket method instead", self.request.remote_ip)
            self.write_message("ERROR/you should use POST or fileSocket method for file uploads")
            return
                
        resp = self.application._pyrtAJAX.handle(request, qs)
        if resp:
            self.write_message(resp)
        else:
            logging.error("%d %s (%s)", self.get_status(), "ajaxSocket error - function returned nothing", self.request.remote_ip)
            self.write_message("ERROR/ajax function returned nothing")
            
    def on_close(self):
        logging.info("%d %s (%s)", self.get_status(), "ajaxSocket closed", self.request.remote_ip)
   
class logSocket(websocket.WebSocketHandler):
    def open(self):
        if not _check.socket(self):
            logging.error("%d %s (%s)", self.get_status(), "logSocket denied", self.request.remote_ip)
            self.write_message("ERROR/Permission denied")
            self.close()
            return
        logging.info("%d %s (%s)", self.get_status(), "logSocket opened", self.request.remote_ip)

    def on_message(self, message):
        if not _check.socket(self):
            logging.error("%d %s (%s)", self.get_status(), "logSocket message denied", self.request.remote_ip)
            self.write_message("ERROR/Permission denied")
            self.close()
            return
    
        try:
            args = urlparse.parse_qs(message)
            request = args["request"][0]
        except:
            logging.error("%d %s (%s)", self.get_status(), "logSocket error - no request specified", self.request.remote_ip)
            self.write_message("ERROR/No request specified")
            return
        else:
            if request == "checknew":
                lastID = args.get("lastID", [None])[0]
                new = self.application._pyrtLog.returnNew(lastID)
                if new:
                    self.write_message(new)
            else:
                logging.error("%d %s (%s)", self.get_status(), "logSocket error - unknown request '%s'" % (request), self.request.remote_ip)
                self.write_message("ERROR/Unknown request")
                return

    def on_close(self):
        logging.info("%d %s (%s)", self.get_status(), "logSocket closed", self.request.remote_ip)

class fileSocket(websocket.WebSocketHandler):
    def open(self):
        if not _check.socket(self):
            logging.error("%d %s (%s)", self.get_status(), "fileSocket denied", self.request.remote_ip)
            self.write_message("ERROR/Permission denied")
            self.close()
            return
        logging.info("%d %s (%s)", self.get_status(), "fileSocket opened", self.request.remote_ip)
        
    def on_message(self, message):
        if not _check.socket(self):
            logging.error("%d %s (%s)", self.get_status(), "fileSocket message denied", self.request.remote_ip)
            self.write_message("ERROR/Permission denied")
            self.close()
            return

        #parse message
        #FILENAME@@@<filename>:::CONTENT@@@<content>
        try:
            filename_ = message.split(":::")[0]
            id__ = message.split(":::")[1]
            content_ = message.split(":::",2)[2]
        except:
            logging.error("%d %s (%s)", self.get_status(), "fileSocket error - invalid message format", self.request.remote_ip)
            self.write_message("ERROR/invalid message format")
        else:
            filename = filename_.split("@@@",1)[1]
            id_ = id__.split("@@@",1)[1]
            content = base64.b64decode(content_.split("@@@",1)[1].split("base64,",1)[1])
            
            logging.info("%d %s (%s)", self.get_status(), "fileSocket message - id: %s, filename: %s, size: %i" % (id_, filename, len(content)), self.request.remote_ip)
            obj = {"torrent" : [{"filename" : filename, "content" : content}]}
            resp = self.application._pyrtAJAX.handle("upload_torrent_socket", obj)
            response = {
                "filename" : filename,
                "id" : id_,
                "response" : resp,
            }
            
            self.write_message(json.dumps(response))
        
    def on_close(self):
        logging.info("%d %s (%s)", self.get_status(), "fileSocket closed", self.request.remote_ip)

class statSocket(websocket.WebSocketHandler):
    def open(self):
        if not _check.socket(self):
            logging.error("%d %s (%s)", self.get_status(), "statSocket denied", self.request.remote_ip)
            self.write_message("ERROR/Permission denied")
            self.close()
            return
        logging.info("%d %s (%s)", self.get_status(), "statSocket opened", self.request.remote_ip) 

    def on_message(self, message):
        if not _check.socket(self):
            logging.error("%d %s (%s)", self.get_status(), "statSocket message denied", self.request.remote_ip)

            self.write_message("ERROR/Permission denied")
            self.close()
            return

        try:
            request = urlparse.parse_qs(message).get("request")[0]
        except:
            logging.error("%d %s (%s)", self.get_status(), "statSocket error - invalid request", self.request.remote_ip)
            self.write_message("ERROR/Invalid request")
            return
        else:
            resp = self.application._pyrtSTATS.handle_request(request)
            self.write_message(resp)
        
        
    def on_close(self):
        logging.info("%d %s (%s)", self.get_status(), "statSocket closed", self.request.remote_ip) 

class stats(web.RequestHandler):
    def get(self):
        chk = _check.web(self)
        if not chk[0]:
            self.write(self.application._pyrtL.loginHTML(chk[1]))
            return
        elif chk[0] and chk[1]:
            self.set_cookie("sess_id", self.application._pyrtL.sendCookie(self.request.remote_ip))
            
        with open("htdocs/statHTML.tmpl") as doc:
            self.write(doc.read())
    post=get

class Main(object):
    def __init__(self):
        pass
    
    def shutdown(self, *args, **kwargs):
        logging.info("SIGTERM received, shutting down")
        self.instance.stop()
        
    def main(self, c):
        signal.signal(signal.SIGTERM, self.shutdown)
        
        global_config = {
            "server.socket_host" : str(c.get("host")),
            "server.socket_port" : c.get("port"),
        }
        
        ssl_certificate = c.get("ssl_certificate")
        ssl_keyfile = c.get("ssl_private_key")
        ssl_ca_certs = c.get("ssl_ca_certs")
        if ssl_certificate and ssl_keyfile:
            ssl_options = {
                "certfile" : ssl_certificate,
                "keyfile" : ssl_keyfile,
                "ca_certs" : ssl_ca_certs,
            }
        else:
            ssl_options = None
        
        tornado.options.parse_command_line(["--logging=debug"])
    
        if os.path.exists(".user.pickle"):
            os.remove(".user.pickle")
        settings = {
            "static_path" : os.path.join(os.getcwd(), "static"),
        }
        application = web.Application([
            (r"/css/(.*)", web.StaticFileHandler, {"path" : os.path.join(os.getcwd(), "static/css/")}),
            (r"/javascript/(.*)", web.StaticFileHandler, {"path" : os.path.join(os.getcwd(), "static/javascript/")}),
            (r"/images/(.*)", web.StaticFileHandler, {"path" : os.path.join(os.getcwd(), "static/images/") }),
            (r"/favicons/(.*)", web.StaticFileHandler, {"path" : os.path.join(os.getcwd(), "static/favicons/") }),
            (r"/", index),
            (r"/index", index),
            (r"/detail", detail),
            (r"/ajax", ajax),
            (r"/options", options),
            (r"/RSS", RSS),
            (r"/stats", stats),
            (r"/log", logHandler),
            (r"/ajaxsocket", ajaxSocket),
            (r"/filesocket", fileSocket),
            (r"/statsocket", statSocket),
            (r"/logsocket", logSocket),
        ], **settings)
    
        logger = weblog.Logger()
        application._pyrtRT = rtorrent.rtorrent(c.get("rtorrent_socket"))    
        application._pyrtL = login.Login(conf=c, log=logger)
        application._pyrtINDEX = indexPage.Index(conf=c, RT=application._pyrtRT)
        application._pyrtAJAX = ajaxPage.Ajax(conf=c, RT=application._pyrtRT, Log=logger)
        application._pyrtOPTIONS = optionsPage.Options(conf=c, RT=application._pyrtRT)
        application._pyrtRSS_PAGE = rssPage.Index(conf=c, RT=application._pyrtRT)
        application._pyrtSTATS = statsPage.Index(conf=c, RT=application._pyrtRT)
        application._pyrtLog = logger
        application._pyrtGLOBALS = {
            "login" : application._pyrtL,
            "indexPage" : application._pyrtINDEX,
            "ajaxPage" : application._pyrtAJAX,
            "optionsPage" : application._pyrtOPTIONS,
            "rssPage" : application._pyrtRSS_PAGE,
            "statsPage" : application._pyrtSTATS,
            "log" : application._pyrtLog,
            "RT" : application._pyrtRT,
            "config" : c,
        }
        
        http_server = httpserver.HTTPServer(application, ssl_options=ssl_options)
        logging.info("Starting webserver on http%s://%s:%i" % ((ssl_options and "s" or ""), global_config["server.socket_host"], global_config["server.socket_port"]))
        http_server.listen(global_config["server.socket_port"], global_config["server.socket_host"])
        
        self.instance = ioloop.IOLoop.instance()
        self.instance.start()


