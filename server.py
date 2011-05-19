#!/usr/bin/env python

from modules import config, login                    # 'real' modules
from modules import indexPage, detailPage, ajaxPage  # pages

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
    
    def ajax(self, request=None, torrent_id=None, filepath=None, torrent=None, start=None):
        #check cookies
        L = login.Login()
        client_cookie = cherrypy.request.cookie
        Lcheck = L.checkLogin(client_cookie)
        if not Lcheck:
            return
                
        if not request:
            return "ERROR/No method specified"
        if not torrent_id:
            return "ERROR/No torrent_id specified"
        
        Ajax = ajaxPage.Ajax()
        if request == "get_torrent_info":
            return Ajax.get_torrent_info(torrent_id)
        elif request == "pause_torrent":
            return Ajax.pause_torrent(torrent_id)
        elif request == "stop_torrent":
            return Ajax.stop_torrent(torrent_id)
        elif request == "start_torrent":
            return Ajax.start_torrent(torrent_id)
        elif request == "remove_torrent":
            return Ajax.remove_torrent(torrent_id)
        elif request == "delete_torrent":
            return Ajax.delete_torrent(torrent_id)
        elif request == "hash_torrent":
            return Ajax.hash_torrent(torrent_id)
        elif request == "get_file":
            return Ajax.get_file(torrent_id, filepath)
        elif request == "upload_torrent":
            return Ajax.upload_torrent(torrent, start)
        else:
            return "ERROR/Invalid method"
    ajax.exposed = True

if __name__ == "__main__":
    cherrypy.config.update(global_config)
    cherrypy.quickstart(mainHandler(), config=app_config)