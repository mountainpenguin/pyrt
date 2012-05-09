#!/usr/bin/env python

from __future__ import print_function
from modules import config, login                    #'real' modules
from modules import indexPage, detailPage, ajaxPage  # pages
from modules import optionsPage, rssPage             # pages

import tornado.ioloop as ioloop
import tornado.web as web
import tornado.httpserver as httpserver
import os

c = config.Config()
c.loadconfig()

global_config = {
    "server.socket_host" : str(c.get("host")),
    "server.socket_port" : c.get("port"),
}

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
            
            Hard-codes in multiple ajax requests and calls the
            equivalent ajaxPage.Ajax() function:
              get_torrent_info
              get_info_multi
              get_torrent_row
              pause_torrent
              stop_torrent
              start_torrent
              remove_torrent
              delete_torrent
              hash_torrent
              get_file
              upload_torrent
              get_feeds
              start_batch
              pause_batch
              stop_batch
              remove_batch
              delete_batch
    """
    def get(self):
        request = self.get_argument("request")
        
        client_cookie = self.cookies
        Lcheck = self.application._pyrtL.checkLogin(client_cookie)
        if not Lcheck and request == "verify_conf_value":
            self.write("Session Ended")
            return
        elif not Lcheck:
            return
        
        torrent_id = self.get_argument("torrent_id", None)
        filepath = self.get_argument("filepath", None)
        torrent = self.get_argument("torrent", None)
        start = self.get_argument("start", None)
        view = self.get_argument("view", None)
        sortby = self.get_argument("sortby", None)
        reverse = self.get_argument("reverse", None)
        html = self.get_argument("html", None)
        torrentIDs = self.get_argument("torrentIDs", None)
        drop_down_ids = self.get_argument("drop_down_ids", None)
        key = self.get_argument("key", None)
        value = self.get_argument("value", None)
        keys = self.get_argument("keys", None)
        values = self.get_argument("values", None)
        
        if request == "get_torrent_info" and torrent_id:
            return self.application._pyrtAJAX.get_torrent_info(torrent_id, html)
        elif request == "get_info_multi" and view:
            return self.application._pyrtAJAX.get_info_multi(view, sortby, reverse, drop_down_ids)
        elif request == "get_torrent_row" and torrent_id:
            return self.application._pyrtAJAX.get_torrent_row(torrent_id)
        elif request == "pause_torrent" and torrent_id:
            return self.application._pyrtAJAX.pause_torrent(torrent_id)
        elif request == "stop_torrent" and torrent_id:
            return self.application._pyrtAJAX.stop_torrent(torrent_id)
        elif request == "start_torrent" and torrent_id:
            return self.application._pyrtAJAX.start_torrent(torrent_id)
        elif request == "remove_torrent" and torrent_id:
            return self.application._pyrtAJAX.remove_torrent(torrent_id)
        elif request == "delete_torrent" and torrent_id:
            return self.application._pyrtAJAX.delete_torrent(torrent_id)
        elif request == "hash_torrent" and torrent_id:
            return self.application._pyrtAJAX.hash_torrent(torrent_id)
        elif request == "get_file" and torrent_id and filepath:
            return self.application._pyrtAJAX.get_file(torrent_id, filepath)
        elif request == "upload_torrent" and torrent is not None:
            return self.application._pyrtAJAX.upload_torrent(torrent, start)
        elif request == "get_feeds":
            return self.application._pyrtAJAX.get_feeds()
        elif request == "start_batch" and torrentIDs is not None:
            return self.application._pyrtAJAX.start_batch(torrentIDs)
        elif request == "pause_batch" and torrentIDs is not None:
            return self.application._pyrtAJAX.pause_batch(torrentIDs)
        elif request == "stop_batch" and torrentIDs is not None:
            return self.application._pyrtAJAX.stop_batch(torrentIDs)
        elif request == "remove_batch" and torrentIDs is not None:
            return self.application._pyrtAJAX.remove_batch(torrentIDs)
        elif request == "delete_batch" and torrentIDs is not None:
            return self.application._pyrtAJAX.delete_batch(torrentIDs)
        elif request == "get_tracker_favicon" and torrent_id is not None:
            return self.application._pyrtAJAX.get_tracker_favicon(torrent_id)
        elif request == "verify_conf_value" and key is not None and value is not None:
            return self.application._pyrtAJAX.verify_conf_value(key, value)
        elif request == "set_config_multiple" and keys is not None and values is not None:
            return self.application._pyrtAJAX.set_config_multiple(keys, values)
        else:
            raise web.HTTPError(400, log_message="Ajax Error Invalid Method")
        
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
        
class test(web.RequestHandler):
    def get(self):
        self.write(repr(self.application._pyrtGLOBALS["config"].get("port")))
        return

if __name__ == "__main__":
    if os.path.exists(".user.pickle"):
        os.remove(".user.pickle")
    print(os.path.join(os.getcwd(), "static/favicon.ico"))
    print(os.path.exists(os.path.join(os.getcwd(), "static/favicon.ico")))
    settings = {
        "static_path" : os.path.join(os.getcwd(), "static")
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
    
    http_server = httpserver.HTTPServer(application)
    http_server.listen(global_config["server.socket_port"], global_config["server.socket_host"])
    
    ioloop.IOLoop.instance().start()