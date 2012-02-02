#!/usr/bin/env python

from modules import config, login                    #'real' modules
from modules import indexPage, detailPage, ajaxPage  # pages
from modules import optionsPage, rssPage             # pages

import cherrypy
import os

c = config.Config()
c.loadconfig()

global_config = {
    "server.socket_host" : str(c.get("host")),
    "server.socket_port" : c.get("port"),
    "server.ssl_certificate" : c.get("ssl_certificate"),
    "server.ssl_private_key" : c.get("ssl_private_key"),
    "tools.encode.on" : True,
    "tools.encode.encoding" : "utf-8",
}
app_config = {
    "/css" : {
        "tools.staticdir.on" : True,
        "tools.staticdir.root" : os.getcwd(),
        "tools.staticdir.dir" : "static/css/",
    },
    "/javascript" : {
        "tools.staticdir.on" : True,
        "tools.staticdir.root" : os.getcwd(),
        "tools.staticdir.dir" : "static/javascript",
    },
    "/images" : {
        "tools.staticdir.on" : True,
        "tools.staticdir.root" : os.getcwd(),
        "tools.staticdir.dir" : "static/images",
    },
    "/favicon.ico" : {
        "tools.staticfile.on" : True,
        "tools.staticfile.root" : os.getcwd(),
        "tools.staticfile.filename" : "static/favicon.ico",
    },
    "/favicons" : {
        "tools.staticdir.on" : True,
        "tools.staticdir.root" : os.getcwd(),
        "tools.staticdir.dir" : "static/favicons",
    }
}

class mainHandler:
    """
        Defines the web server options
    """
    def __init__(self):
        """
            Initialisation function for mainHandler
            
            Initialises modules/:
            self.L --> login.Login()
            self.INDEX --> indexPage.Index()
            self.AJAX --> ajaxPage.Ajax()
            self.OPTIONS --> optionsPage.Options()
            self.RSS_PAGE --> rssPage.Index()
        """
        self.L = login.Login(conf=c)
        self.INDEX = indexPage.Index(conf=c)
        self.AJAX = ajaxPage.Ajax(conf=c)
        self.OPTIONS = optionsPage.Options(conf=c)
        self.RSS_PAGE = rssPage.Index(conf=c)
        self.GLOBALS = {
            "login" : self.L,
            "indexPage" : self.INDEX,
            "ajaxPage" : self.AJAX,
            "optionsPage" : self.OPTIONS,
            "rssPage" : self.RSS_PAGE,
            "config" : c,
            #"config" : config.Config(),
        }
        
    def index(self, password=None, view=None, sortby=None, reverse=None, **kwargs):
        """
            Default page handler (/)
            
            Returns indexPage.Index.index() is user is logged in
        """
        #check cookies
        client_cookie = cherrypy.request.cookie
        Lcheck = self.L.checkLogin(client_cookie)
        if not Lcheck and not password:
            return self.L.loginHTML()
        elif not Lcheck and password:
            #check password
            Pcheck = self.L.checkPassword(password)
            if Pcheck:
                #set a cookie
                cherrypy.response.cookie = self.L.sendCookie()
            else:
                return self.L.loginHTML("Incorrect Password")
        
        return self.INDEX.index(password, view, sortby, reverse)
        
    index.exposed = True
    
    def detail(self, view=None, torrent_id=None, password=None, **kwargs):
        """
            Detailed page view handler (/detail)
            
            Retrieves detailPage.Detail() passing the torrent_id argument.
            This has attribute HTML, which is returned.
        """
        #check cookies
        client_cookie = cherrypy.request.cookie
        Lcheck = self.L.checkLogin(client_cookie)
        if not Lcheck and not password:
            return self.L.loginHTML()
        elif not Lcheck and password:
            #check password
            Pcheck = self.L.checkPassword(password)
            if Pcheck:
                #set a cookie
                cherrypy.response.cookie = self.L.sendCookie()
            else:
                return self.L.loginHTML("Incorrect Password")
        
        Detail = detailPage.Detail(torrent_id, conf=self.GLOBALS["config"])
        return Detail.HTML
    detail.exposed = True
    
    def ajax(self, request=None, torrent_id=None, filepath=None, torrent=None, start=None, view=None, sortby=None, reverse=None, html=None, torrentIDs=None):
        """
            Handler for ajax queries (/ajax)
            
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
        #check cookies
        client_cookie = cherrypy.request.cookie
        Lcheck = self.L.checkLogin(client_cookie)
        if not Lcheck:
            return
        #request=get_torrent_row&torrent_id=
        if request == "get_torrent_info" and torrent_id:
            return self.AJAX.get_torrent_info(torrent_id, html)
        elif request == "get_info_multi" and view:
            return self.AJAX.get_info_multi(view, sortby, reverse)
        elif request == "get_torrent_row" and torrent_id:
            return self.AJAX.get_torrent_row(torrent_id)
        elif request == "pause_torrent" and torrent_id:
            return self.AJAX.pause_torrent(torrent_id)
        elif request == "stop_torrent" and torrent_id:
            return self.AJAX.stop_torrent(torrent_id)
        elif request == "start_torrent" and torrent_id:
            return self.AJAX.start_torrent(torrent_id)
        elif request == "remove_torrent" and torrent_id:
            return self.AJAX.remove_torrent(torrent_id)
        elif request == "delete_torrent" and torrent_id:
            return self.AJAX.delete_torrent(torrent_id)
        elif request == "hash_torrent" and torrent_id:
            return self.AJAX.hash_torrent(torrent_id)
        elif request == "get_file" and torrent_id and filepath:
            return self.AJAX.get_file(torrent_id, filepath)
        elif request == "upload_torrent" and torrent is not None:
            return self.AJAX.upload_torrent(torrent, start)
        elif request == "get_feeds":
            return self.AJAX.get_feeds()
        elif request == "start_batch" and torrentIDs is not None:
            return self.AJAX.start_batch(torrentIDs)
        elif request == "pause_batch" and torrentIDs is not None:
            return self.AJAX.pause_batch(torrentIDs)
        elif request == "stop_batch" and torrentIDs is not None:
            return self.AJAX.stop_batch(torrentIDs)
        elif request == "remove_batch" and torrentIDs is not None:
            return self.AJAX.remove_batch(torrentIDs)
        elif request == "delete_batch" and torrentIDs is not None:
            return self.AJAX.delete_batch(torrentIDs)
        elif request == "get_tracker_favicon" and torrent_id is not None:
            return self.AJAX.get_tracker_favicon(torrent_id)
            
        else:
            raise cherrypy.HTTPError(message="Ajax Error Invalid Method")
    ajax.exposed = True
    
    def options(self, test=False, password=None):
        """
            Handler for options page view (/options)
            
            *** Currently a work in progress ***
            Can only be viewed if "test" is passed as an argument.
            If it is, returns optionsPage.Options.index()
        """
        client_cookie = cherrypy.request.cookie
        Lcheck = self.L.checkLogin(client_cookie)
        if not Lcheck and not password:
            return self.L.loginHTML()
        elif not Lcheck and password:
            #check password
            Pcheck = self.L.checkPassword(password)
            if Pcheck:
                #set a cookie
                cherrypy.response.cookie = self.L.sendCookie()
            else:
                return self.L.loginHTML("Incorrect Password")
                
        if not test:
            try:
                link = cherrypy.request.headers["Referer"]
            except KeyError:
                link = "/index"
            return """
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
            """ % {"link" : link}
        else:
            return self.OPTIONS.index()
    options.exposed = True

    def RSS(self):
        return self.RSS_PAGE.index()
    RSS.exposed = True
    
    def test(self):
        return repr(self.GLOBALS["config"].get("port"))
    #test.exposed = True
        
if __name__ == "__main__":
    if os.path.exists(".user.pickle"):
        os.remove(".user.pickle")
    cherrypy.config.update(global_config)
    cherrypy.quickstart(mainHandler(), config=app_config)
