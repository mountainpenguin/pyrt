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
    }
}

class mainHandler:
    def __init__(self):
        self.L = login.Login()
        self.INDEX = indexPage.Index()
        self.AJAX = ajaxPage.Ajax()
        self.OPTIONS = optionsPage.Options()
        self.RSS = rssPage.Index()
        
    def index(self, password=None, view=None, sortby=None, reverse=None, **kwargs):
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
        
        Detail = detailPage.Detail(torrent_id)
        return Detail.HTML
    detail.exposed = True
    
    def ajax(self, request=None, torrent_id=None, filepath=None, torrent=None, start=None, view=None, sortby=None, reverse=None, html=None):
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
            
        else:
            raise cherrypy.HTTPError(message="Ajax Error Invalid Method")
    ajax.exposed = True
    
    def options(self, test=False):
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
        return self.RSS.index()
    RSS.exposed = True
    
if __name__ == "__main__":
    if os.path.exists(".user.pickle"):
        os.remove(".user.pickle")
    cherrypy.config.update(global_config)
    cherrypy.quickstart(mainHandler(), config=app_config)