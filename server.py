#!/usr/bin/env python

from __future__ import print_function
from modules import config, login                    #'real' modules
from modules import indexPage, detailPage, ajaxPage  # pages
from modules import optionsPage, rssPage             # pages

import tornado.ioloop as ioloop
import tornado.web as web
import tornado.httpserver as httpserver
import tornado.websocket as websocket
import os
import urlparse
import json

c = config.Config()
c.loadconfig()

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

class index(web.RequestHandler):
    """Default page handler for /
    
        Writes indexPage.Index.index() if user is logged in
        else writes login page
    """
    def get(self):
        password = self.get_argument("password", None)
        view = self.get_argument("view", None)
        sortby = self.get_argument("sortby", None)
        reverse = self.get_argument("reverse", None)
        
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck and not password:
            self.write(self.application._pyrtL.loginHTML())
            return
        elif not Lcheck and password:
            Pcheck = self.application._pyrtL.checkPassword(password)
            if Pcheck:
                #set cookie
                self.set_cookie("sess_id", self.application._pyrtL.sendCookie(True))
            else:
                self.write(self.application._pyrtL.loginHTML("Incorrect Password"))
                return
            
        self.write(self.application._pyrtINDEX.index(password, view, sortby, reverse))
        
    post = get
    
class detail(web.RequestHandler):
    """Detailed page view handler (/detail)
            
        Retrieves detailPage.Detail() passing the torrent_id argument.
        This has attribute HTML, which is written.
    """
    def get(self):
        view = self.get_argument("view", None)
        torrent_id = self.get_argument("torrend_id", None)
        password = self.get_argument("password", None)
        
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck and not password:
            self.write(self.application._pyrtL.loginHTML())
            return
        elif not Lcheck and password:
            Pcheck = self.application._pyrtL.checkPassword(password)
            if Pcheck:
                #set cookie
                self.set_cookie("sess_id", self.application._pyrtL.sendCookie(True))
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
        print(">>> got ajax request %s" % request)
        if not request:
            raise web.HTTPError(400, log_message="Error, no request specified")
        
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck and request == "verify_conf_value":
            self.write("Session Ended")
            return
        elif not Lcheck:
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
        test = self.get_argument("test", False)
        password = self.get_argument("password", None)
    
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck and not password:
            self.write(self.application._pyrtL.loginHTML())
            return
        elif not Lcheck and password:
            Pcheck = self.application._pyrtL.checkPassword(password)
            if Pcheck:
                #set cookie
                self.set_cookie("sess_id", self.application._pyrtL.sendCookie(True))
            else:
                self.write(self.application._pyrtL.loginHTML("Incorrect Password"))
                return
            
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
    
class RSS(web.RequestHandler):
    def get(self):
        password = self.get_argument("password", None)
    
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck and not password:
            self.write(self.application._pyrtL.loginHTML())
            return
        elif not Lcheck and password:
            Pcheck = self.application._pyrtL.checkPassword(password)
            if Pcheck:
                #set cookie
                self.set_cookie("sess_id", self.application._pyrtL.sendCookie(True))
            else:
                self.write(self.application._pyrtL.loginHTML("Incorrect Password"))
                return
            
        self.write(self.application._pyrtRSS_PAGE.index())
        
class ajaxSocket(websocket.WebSocketHandler):
    def open(self):
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck:
            print(">>> ajaxSocket denied")
            self.close()
            return
        print(">>> ajaxSocket opened")
        

    def on_message(self, message):
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
        print("<<< got ajaxSocket request %s" % request)
        if not request:
            self.write_message("ERROR/No request specified")
            return
        
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck:
            return
        
        if not self.application._pyrtAJAX.has_command(request):
            self.write_message("ERROR/No such command")
            return
        if not self.application._pyrtAJAX.validate_command(request, qs):
            self.write_message("ERROR/need more args")
            return
        if request == "upload_torrent":
            self.write_message("ERROR/you should use POST or fileSocket method for file uploads")
            return
                
        resp = self.application._pyrtAJAX.handle(request, qs)
        if resp:
            self.write_message(resp)
        else:
            self.write_message("ERROR/ajax function returned nothing")
            
    def on_close(self):
        print(">>> ajaxSocket closed")

class fileSocket(websocket.WebSocketHandler):
    def open(self):
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck:
            print(">>> fileSocket denied")
            self.write_message("ERROR/Permission denied")
            self.close()
            return
        print(">>> fileSocket opened")
        
    def on_message(self, message):
        #parse message
        #FILENAME@@@<filename>:::CONTENT@@@<content>
        print("<<< fileSocket message %s" % message)
        try:
            filename_ = message.split(":::")[0]
            id__ = message.split(":::")[1]
            content_ = message.split(":::",2)[2]
        except:
            self.write_message("ERROR/invalid message format")
        else:
            filename = filename_.split("@@@",1)[1]
            id_ = id__.split("@@@",1)[1]
            content = content_.split("@@@",1)[1]
            print("<<< fileSocket id %s, filename %s, size %i" % (id_, filename, len(content)))
            obj = {"torrent" : [{"filename" : filename, "content" : content}]}
            resp = self.application._pyrtAJAX.handle("upload_torrent_socket", obj)
            response = {
                "filename" : filename,
                "id" : id_,
                "response" : resp,
            }
            
            self.write_message(json.dumps(response))
        
    def on_close(self):
        print(">>> fileSocket closed")
        

class test(web.RequestHandler):
    def get(self):
        with open("htdocs/testing.html.tmpl") as doc:
            self.write(doc.read())
    
    post=get
    
if __name__ == "__main__":
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
        (r"/ajaxsocket", ajaxSocket),
        (r"/filesocket", fileSocket),
    ], **settings)
    
    application._pyrtL = login.Login(conf=c)
    application._pyrtINDEX = indexPage.Index(conf=c)
    application._pyrtAJAX = ajaxPage.Ajax(conf=c)
    application._pyrtOPTIONS = optionsPage.Options(conf=c)
    application._pyrtRSS_PAGE = rssPage.Index(conf=c)
    application._pyrtGLOBALS = {
        "login" : application._pyrtL,
        "indexPage" : application._pyrtINDEX,
        "ajaxPage" : application._pyrtAJAX,
        "optionsPage" : application._pyrtOPTIONS,
        "rssPage" : application._pyrtRSS_PAGE,
        "config" : c,
    }
    
    http_server = httpserver.HTTPServer(application, ssl_options=ssl_options)
    http_server.listen(global_config["server.socket_port"], global_config["server.socket_host"])
    
    ioloop.IOLoop.instance().start()
