#!/usr/bin/env python

from modules import config, login                    #'real' modules
from modules import indexPage, detailPage, ajaxPage  # pages
from modules import optionsPage                      # pages

import cherrypy
import os

c = config.Config()
c.loadconfig()

global_config = {
    "server.socket_host" : str(c.get("host")),
    "server.socket_port" : c.get("port"),
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
    def index(self, password=None, view=None, sortby=None, reverse=None, **kwargs):
            
        #check cookies
        L = login.Login()
        client_cookie = cherrypy.request.cookie
        Lcheck = L.checkLogin(client_cookie)
        if not Lcheck and not password:
            return L.loginHTML()
        elif not Lcheck and password:
            #check password
            Pcheck = L.checkPassword(password)
            if Pcheck:
                #set a cookie
                cherrypy.response.cookie = L.sendCookie()
            else:
                return L.loginHTML("Incorrect Password")
        
        if view == "option":
            Options = optionPage.Options()
            return Options.index()
        else:
            Index = indexPage.Index()
            return Index.index(password, view, sortby, reverse)
        
    index.exposed = True
    
    def detail(self, view=None, torrent_id=None, password=None, **kwargs):
        #check cookies
        L = login.Login()
        client_cookie = cherrypy.request.cookie
        Lcheck = L.checkLogin(client_cookie)
        if not Lcheck and not password:
            return L.loginHTML()
        elif not Lcheck and password:
            #check password
            Pcheck = L.checkPassword(password)
            if Pcheck:
                #set a cookie
                cherrypy.response.cookie = L.sendCookie()
            else:
                return L.loginHTML("Incorrect Password")
        
        Detail = detailPage.Detail()
        if not torrent_id:
            return "ERROR/Not Implemented"
        elif not view or view == "info":
            return Detail.main(torrent_id)
        elif view == "peers":
            return Detail.peers(torrent_id)
        elif view == "files":
            return Detail.files(torrent_id)
        elif view == "trackers":
            return Detail.trackers(torrent_id)
    detail.exposed = True
    
    def ajax(self, request=None, torrent_id=None, filepath=None, torrent=None, start=None, view=None, sortby=None, reverse=None):
        #check cookies
        L = login.Login()
        client_cookie = cherrypy.request.cookie
        Lcheck = L.checkLogin(client_cookie)
        if not Lcheck:
            return
        
        Ajax = ajaxPage.Ajax()
        if request == "get_torrent_info" and torrent_id:
            return Ajax.get_torrent_info(torrent_id)
        elif request == "get_info_multi" and view:
            return Ajax.get_info_multi(view, sortby, reverse)
        elif request == "pause_torrent" and torrent_id:
            return Ajax.pause_torrent(torrent_id)
        elif request == "stop_torrent" and torrent_id:
            return Ajax.stop_torrent(torrent_id)
        elif request == "start_torrent" and torrent_id:
            return Ajax.start_torrent(torrent_id)
        elif request == "remove_torrent" and torrent_id:
            return Ajax.remove_torrent(torrent_id)
        elif request == "delete_torrent" and torrent_id:
            return Ajax.delete_torrent(torrent_id)
        elif request == "hash_torrent" and torrent_id:
            return Ajax.hash_torrent(torrent_id)
        elif request == "get_file" and torrent_id and filepath:
            return Ajax.get_file(torrent_id, filepath)
        elif request == "upload_torrent" and torrent is not none:
            return Ajax.upload_torrent(torrent, start)
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
            Options = optionsPage.Options()
            return Options.index()
    options.exposed = True

if __name__ == "__main__":
    cherrypy.config.update(global_config)
    cherrypy.quickstart(mainHandler(), config=app_config)