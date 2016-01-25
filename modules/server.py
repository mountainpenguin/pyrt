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
from modules import rpchandler
from modules import autohandler
from modules import remotes
from modules import create
from modules import rss
from modules import misc
from modules import aliases
from modules import downloadHandler
from modules import xmlrpc2scgi

from modules import ajaxPage
from modules import statsPage

from modules import system

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.websocket
import tornado.options
import tornado.netutil
import tornado.process
import tornado.httputil
import tornado.template

import os
import sys
import urlparse
import json
import base64
import hashlib
import logging
import signal
import traceback
import random
import string
import socket
import time


class null(object):
    @staticmethod
    def func(*args, **kwargs):
        return None


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def get_current_user(self):
        if self.application._pyrtL.checkLogin(self.get_secure_cookie("sess_id"), self.request.remote_ip):
            return True

    def check_origin(self, origin):
        parsed_origin = urlparse.urlparse(origin)
        origin = parsed_origin.netloc
        origin = origin.lower()
        if not origin:
            return True

        host = self.request.headers.get("Host")
        return origin == host

    def check_ping(self, message):
        if message == "ping":
            self.write_message("pong")
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
        self.AUTO = {}
        self.RPC = {}
        self.CREATE = {}
        self.WORKER = {}
        self.lookup = {
            "logSocket": self.LOG,
            "ajaxSocket": self.AJAX,
            "fileSocket": self.FILE,
            "statSocket": self.STAT,
            "autoSocket": self.AUTO,
            "rpcSocket": self.RPC,
            "createSocket": self.CREATE,
            "workerSocket": self.WORKER,
        }

    def add(self, socketType, socketObject, session=None, callback=null.func):
        if socketType in self.lookup:
            socketID = "".join([random.choice(string.letters) for x in range(10)])
            self.lookup[socketType][socketID] = Socket(socketID, socketType, socketObject, session, callback)
            return socketID

    def remove(self, socketType, socketID):
        if socketType in self.lookup and socketID in self.lookup[socketType]:
            del self.lookup[socketType][socketID]

    def getType(self, socketType, session=None):
        if session:
            if socketType in self.lookup:
                return filter(lambda x: x.session == session, self.lookup[socketType].values())
        else:
            if socketType in self.lookup:
                return self.lookup[socketType].values()

    def getSession(self, session):
        allSocks = []
        for x in self.lookup.values():
            allSocks.extend(x.values())
        return filter(lambda x: x.session == session, allSocks)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        if self.application._pyrtL.checkLogin(self.get_secure_cookie("sess_id"), self.request.remote_ip):
            return True


class loginHandler(BaseHandler):
    def get(self):
        if self.current_user:
            if self.get_argument("next"):
                self.redirect(".{0}".format(self.get_argument("next")))
            else:
                self.redirect("./")
        else:
            lookup = {
                "PERM_SALT": self.application._pyrtL.PERM_SALT,
                "msg": "",
                "css": [
                    "main.css",
                ],
                "javascript": [
                    "login-combined.min.js",
                ]
            }
            self.render("login.html", **lookup)

    def post(self):
        passw = self.get_argument("password", None)
        pCheck = self.application._pyrtL.checkPassword(passw, self.request.remote_ip)
        if pCheck:
            # set cookie
            self.set_secure_cookie("sess_id", self.application._pyrtL.sendCookie(self.request.remote_ip))
            if self.get_argument("next"):
                self.redirect(".{0}".format(self.get_argument("next")))
            else:
                self.redirect("./")
        else:
            lookup = {
                "PERM_SALT": self.application._pyrtL.PERM_SALT,
                "msg": "Incorrect Password",
                "css": [
                    "main.css",
                ],
                "javascript": [
                    "login-combined.min.js",
                ]
            }
            self.render("login.html", **lookup)


class index(BaseHandler):
    """Default page handler for /

    """
    @tornado.web.authenticated
    def get(self):
        view = self.get_argument("view", None)
        sortby = self.get_argument("sortby", None)
        reverse = self.get_argument("reverse", None)

        if not view or view not in ["main", "started", "stopped", "complete", "incomplete", "hashing", "seeding", "active"]:
            view = "main"
        if not sortby:
            sortby = "none"

        torrentList = self.application._pyrtRT.getTorrentList2(view)

        sorted_list = misc.sortTorrents(torrentList, sortby, reverse)
        processed_list = misc.process_list(sorted_list)
        lookup = {
            "global_stats": system.get_global(),
            "torrent_list": processed_list,
            "this_view": view,
            "this_sort": sortby,
            "this_reverse": reverse,
            "css": [
                "main.css",
                "liteAccordion/liteaccordion.css",
                "jquery.treeview.css"
            ],
            "javascript": [
                "jquery-ui-1.8.17.custom.min.js",
                "jquery.contextmenu.r2.js",
                "jquery-sliderow.js",
                "liteaccordion.jquery.min.js",
                "jquery.treeview.js",
                "jquery.cookie.js",
                "main.min.js"
            ]
        }
        self.render("index.html", **lookup)

    post = get


class createHandler(BaseHandler):
    """Page handler for creating torrents"""
    @tornado.web.authenticated
    def get(self):
        lookup = {
            "ROOT_DIR": self.application._pyrtRT.getGlobalRootPath(),
            "css": [
                "main.css",
                "jquery.treeview.css",
                "create.css",
            ],
            "javascript": [
                "jquery-ui-1.8.17.custom.min.js",
                "jquery.treeview.js",
                "create.min.js",
            ],
        }
        self.render("create.html", **lookup)

    post = get


class downloadCreation(BaseHandler):
    """Page handler for downloading temp torrents"""
    @tornado.web.authenticated
    def get(self):
        filename = self.get_argument("filename", None)
        if not filename:
            raise tornado.web.HTTPError(400, log_message="Error, no filename specified")
        elif not os.path.exists(os.path.join("tmp", os.path.basename(filename))):
            raise tornado.web.HTTPError(400, log_message="Error, no such file")
        else:
            filename = os.path.basename(filename)
            contents = open(os.path.join("tmp", filename)).read()
            self.set_header("Content-Type", "application/x-bittorrent")
            self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
            self.write(contents)

    post = get


class ajax(BaseHandler):
    """Handler for ajax queries (/ajax)

    """
    def get(self):
        if not self.current_user:
            self.write("Session Ended")
            return

        qs = self.request.arguments
        request = qs.get("request", [None])[0]
        if not request:
            raise tornado.web.HTTPError(400, log_message="Error, no request specified")

        if not self.application._pyrtAJAX.has_command(request):
            raise tornado.web.HTTPError(400, log_message="Error Invalid Method")
        if not self.application._pyrtAJAX.validate_command(request, qs):
            raise tornado.web.HTTPError(400, log_message="Error need more args")
        if request == "upload_torrent":
            try:
                qs["torrent"] = self.request.files["torrent"]
            except:
                raise tornado.web.HTTPError(400, log_message="No torrent specified for upload")

        resp = self.application._pyrtAJAX.handle(request, qs)
        if resp:
            self.write(resp)

    post = get


class options(BaseHandler):
    """Handler for options page view (/options)
    """
    @tornado.web.authenticated
    def get(self):
        RT = self.application._pyrtRT
        aliases = self.application._pyrtAliasStorage.STORE
        portrange = RT.getGlobalPortRange()
        maxpeers = RT.getGlobalMaxPeers()
        maxpeersseed = RT.getGlobalMaxPeersSeed()
        if maxpeersseed == -1:
            maxpeersseed = maxpeers

        try:
            performancereadahead = int(float(RT.getGlobalHashReadAhead()))
        except:
            performancereadahead = None

        gmc_bool, gmc_value = RT.getGlobalMoveTo()
        gmc_enabled = gmc_bool and "checked" or ""
        if gmc_bool:
            gmc_hidden = ""
        else:
            gmc_hidden = "hidden"
        gmc_value = gmc_value and gmc_value or ""

        conf = self.application._pyrtGLOBALS["config"]

        definitions = {
            "config": conf.CONFIG,
            "throttleup": int(float(RT.getGlobalUpThrottle()) / 1024),
            "throttledown": int(float(RT.getGlobalDownThrottle()) / 1024),
            "generaldir": RT.getGlobalRootPath(),
            "generalmovecheckbool": gmc_enabled,
            "generalmovecheckvalue": gmc_value,
            "generalmovecheckhidden": gmc_hidden,
            "networkportfrom": portrange.split("-")[0],
            "networkportto": portrange.split("-")[1],
            "aliases": aliases,
            "performancemaxmemory": int(float(RT.getGlobalMaxMemoryUsage())/1024/1024),
            "performancereceivebuffer": int(float(RT.getGlobalReceiveBufferSize())/1024),
            "performancesendbuffer": int(float(RT.getGlobalSendBufferSize())/1024),
            "performancemaxopenfiles": RT.getGlobalMaxOpenFiles(),
            "performancemaxfilesize": int(float(RT.getGlobalMaxFileSize())/1024/1024),
            "performancereadahead": performancereadahead,
            "networksimuluploads": RT.getGlobalMaxUploads(),
            "networksimuldownloads": RT.getGlobalMaxDownloads(),
            "networkmaxpeers": maxpeers,
            "networkmaxpeersseed": maxpeersseed,
            "networkmaxopensockets": RT.getGlobalMaxOpenSockets(),
            "networkmaxopenhttp": RT.getGlobalMaxOpenHttp(),
            "css": [
                "options.css",
            ],
            "javascript": [
                "jquery-ui-1.8.17.custom.min.js",
                "options.min.js",
            ]
        }

        self.render("options.html", **definitions)

    post = get


class logHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        records = self.application._pyrtLog.records()
        lookup = {
            "RECORDS": records,
            "css": [
                "main.css",
                "log.css",
            ],
            "javascript": [
                "jquery-ui-1.8.17.custom.min.js",
                "log.min.js",
            ],
        }
        self.render("log.html", **lookup)

    post = get


class stats(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        lookup = {
            "css": [
                "stats.css",
                "main.css",
                "smoothness/jquery-ui-1.8.13.custom.css",
            ],
            "javascript": [
                "jquery-ui-1.8.17.custom.min.js",
                "kinetic-v3.9.5.min.js",
                "stats.min.js"
            ]
        }
        self.render("stats.html", **lookup)

    post = get


class download(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        auth = self.get_argument("auth", None)
        if not auth:
            raise tornado.web.HTTPError(400, log_message="Error: No auth defined")

        try:
            path = self.application._pyrtDownloadHandler.getPath(auth)
        except downloadHandler.NoSuchToken:
            raise tornado.web.HTTPError(404, log_message="Error: No such token")
        except downloadHandler.TokenExpired:
            raise tornado.web.HTTPError(410, log_message="Error: Token expired")
        else:
            if os.path.exists(path):
                self.set_header("Content-Disposition", "attachment; filename=%s" % os.path.basename(path))
                with open(path) as fd:
                    self.write(fd.read())
            else:
                raise tornado.web.HTTPError(404, log_message="Error: No such file")

    @tornado.web.authenticated
    def post(self):
        raise tornado.web.HTTPError(405, log_message="Error: POST when GET expected")


class autoHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        which = self.get_argument("which", None)
        lookup = {
            "PERM_SALT": self.application._pyrtL.getPermSalt(),
            "css": [
                "main.css",
                "auto.css",
                "smoothness/jquery-ui-1.8.13.custom.css"
            ],
            "javascript": [
                "jquery-ui-1.8.17.custom.min.js",
                None,
                "auto-combined.min.js"
            ]
        }
        if not which or which.upper() == "IRC":
            lookup["javascript"][1] = "auto-irc.min.js"
            self.render("auto-irc.html", **lookup)
        else:
            lookup["javascript"][1] = "auto-rss.min.js"
            self.render("auto-rss.html", **lookup)

    post = get


class SCGIHandler(tornado.web.RequestHandler):
    def post(self):
        c = self.application._pyrtGLOBALS["config"]
        # authenticate
        authenticated = False
        if "Authorization" in self.request.headers:
            authorization = self.request.headers.get("Authorization")
            if c.get("scgi_method") == "Basic":
                encoded = authorization.split("Basic ")[1]
                decoded = base64.b64decode(encoded)
                username, passwd = decoded.split(":")
                if username != c.get("scgi_username") or passwd != c.get("scgi_password"):
                    self.set_status(401)
                    self.set_header("WWW-Authenticate", "Basic realm=\"%s\"" % c.get("host"))
                    authenticated = False
                else:
                    authenticated = True
            else:
                # use Digest method
                params = authorization.split("Digest ")[1].split(",")

                def op(x): x.strip().replace("\"", "").split("=")

                params = dict([op(y) for y in params])
#                client_username = params["username"]
                client_response = params["response"]
                client_nonce = params["nonce"]
                client_nc = params["nc"]
                client_cnonce = params["cnonce"]
                client_qop = params["qop"]

                digest_user = c.get("scgi_username")
                digest_pass = c.get("scgi_password")
                digest_realm = c.get("host")

                digest_A1 = "%s:%s@%s:%s" % (
                    digest_user, digest_user, digest_realm, digest_pass
                )

                digest_A2 = "%s:%s" % (
                    self.request.method,
                    self.request.uri
                )

                digest_KD = hashlib.md5("%s:%s" % (
                    hashlib.md5(digest_A1).hexdigest(),
                    "%s:%s:%s:%s:%s" % (
                        client_nonce,
                        client_nc,
                        client_cnonce,
                        client_qop,
                        hashlib.md5(digest_A2).hexdigest()
                    )
                )).hexdigest()

                if digest_KD == client_response:
                    authenticated = True

        if authenticated:
            xml = self.request.body
            req = xmlrpc2scgi.SCGIRequest(c.get("rtorrent_socket"))
            resp = req.send(xml)
            if not self._finished:
                self.finish(resp)
        else:
            self.set_status(401)
            if c.get("scgi_method") == "Basic":
                self.set_header("WWW-Authenticate", "Basic realm=\"%s\"" % c.get("host"))
            else:
                digest_realm = c.get("host")
                digest_user = c.get("scgi_username")

                digest_nonce = hashlib.md5(
                    "%d:%s" % (time.time(), digest_realm)
                ).hexdigest()
                digest_opaque = hashlib.md5(
                    "".join([random.choice(string.letters) for x in range(20)])
                ).hexdigest()

                digest_header = (
                    "Digest realm=\"%(user)s@%(realm)s\", "
                    "nonce=\"%(nonce)s\", "
                    "algorithm=\"MD5\", "
                    "qop=\"auth\", "
                    "opaque=\"%(opaque)s\""
                ) % {
                    "user": digest_user,
                    "realm": digest_realm,
                    "nonce": digest_nonce,
                    "opaque": digest_opaque,
                }
                self.set_header("WWW-Authenticate", digest_header)

    get = post


class manifest(BaseHandler):
    """Fake static file handler for serving static/cache.manifest"""
    @tornado.web.authenticated
    def get(self):
        if os.path.exists(".uncache"):
            manifest = "CACHE MANIFEST"
            if hasattr(self.application, "_UNCACHE") and self.application._UNCACHE:
                os.remove(".uncache")
            else:
                self.application._UNCACHE = True
        else:
            manifest = open("static/cache.manifest").read()
        self.write(manifest)
        self.set_header("Content-Type", "text/cache-manifest")
        self.set_status(200)


class manifesthack(BaseHandler):
    """Prevent dynamic index from being cached"""
    @tornado.web.authenticated
    def get(self):
        html = """
        <!DOCTYPE html>
        <html manifest="cache.manifest">
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                <script type="text/javascript" src="javascript/jquery-1.7.min.js"></script>
                <script type="text/javascript" src="javascript/startup.min.js"></script>
            </head>
            <body></body>
        </html>
        """
        self.write(html)


class ajaxSocket(WebSocketHandler):
    socketID = None

    @tornado.web.authenticated
    def open(self):
        self.socketID = self.application._pyrtSockets.add("ajaxSocket", self, self.get_secure_cookie("sess_id"))
        logging.info("%d %s (%s)", self.get_status(), "ajaxSocket opened", self.request.remote_ip)

    def _respond(self, request, response, error=None, **kwargs):
        resp = {
            "request": request,
            "response": response,
            "error": error,
        }
        resp.update(kwargs)
        self.write_message(json.dumps(resp))

    @tornado.web.authenticated
    def on_message(self, message):
        if self.check_ping(message):
            return

#        parse out get query
#        q = urlparse.parse_qs(message)
#        request = q.get("request", [None])[0]
#        view = q.get("view", [None])[0]
#        sortby = q.get("sortby", [None])[0]
#        reverse = q.get("reverse", [None])[0]
#        drop_down_ids = q.get("drop_down_ids", [None])[0]
#        if request == "get_info_multi" and view:
#            self.write_message(self.application._pyrtAJAX.get_info_multi(view, sortby, reverse, drop_down_ids))

        qs = urlparse.parse_qs(message)
        request = qs.get("request", [None])[0]
        if request != "get_info_multi":
            logging.info("%d %s (%s)", self.get_status(), "ajaxSocket request %s" % request, self.request.remote_ip)
        if not request:
            logging.error("%d %s (%s)", self.get_status(), "ajaxSocket error - no request specified", self.request.remote_ip)
#            self.write_message("ERROR/No request specified")
            self._respond(None, "ERROR", "No request specified")
            return

        if not self.application._pyrtAJAX.has_command(request):
            logging.error("%d %s (%s)", self.get_status(), "ajaxSocket error - no such command `%s`" % request, self.request.remote_ip)
            self._respond(request, "ERROR", "No such command")
            return
        if not self.application._pyrtAJAX.validate_command(request, qs):
            logging.error("%d %s (%s)", self.get_status(), "ajaxSocket error - not enough args", self.request.remote_ip)
            self._respond(request, "ERROR", "Need more arguments")
            return
        if request == "upload_torrent":
            logging.warning("%d %s (%s)", self.get_status(), "ajaxSocket upload_torrent not supported, use POST or fileSocket method instead", self.request.remote_ip)
            self._respond(request, "ERROR", "You should use POST or fileSocket methods for file uploads")
            return

        try:
            resp = self.application._pyrtAJAX.handle(request, qs)
        except:
            tb = traceback.format_exc()
            logging.error(tb)
            self.application._pyrtLog.error("AJAX: error in command %s - %s", request, tb.strip().split("\n")[-1])
            self._respond(request, "ERROR", "AJAX function returned nothing")
        else:
            if resp:
                self._respond(request, resp)
            else:
                logging.error("%d %s (%s)", self.get_status(), "ajaxSocket error - function returned nothing", self.request.remote_ip)
                self._respond(request, "ERROR", "AJAX function returned nothing")

    def on_close(self):
        self.application._pyrtSockets.remove("ajaxSocket", self.socketID)
        logging.info("%d %s (%s)", self.get_status(), "ajaxSocket closed", self.request.remote_ip)


class logSocket(WebSocketHandler):
    socketID = None

    @tornado.web.authenticated
    def open(self):
        self.socketID = self.application._pyrtSockets.add(
            "logSocket",
            self, self.get_secure_cookie("sess_id")
        )
        logging.info("%d %s (%s)", self.get_status(), "logSocket opened", self.request.remote_ip)

    @tornado.web.authenticated
    def on_message(self, message):
        if self.check_ping(message):
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
        self.application._pyrtSockets.remove("logSocket", self.socketID)
        logging.info("%d %s (%s)", self.get_status(), "logSocket closed", self.request.remote_ip)


class fileSocket(WebSocketHandler):
    socketID = None

    @tornado.web.authenticated
    def open(self):
        self.socketID = self.application._pyrtSockets.add("fileSocket", self, self.get_secure_cookie("sess_id"))
        logging.info("%d %s (%s)", self.get_status(), "fileSocket opened", self.request.remote_ip)

    @tornado.web.authenticated
    def on_message(self, message):
        if self.check_ping(message):
            return

        # parse message
        # FILENAME@@@<filename>:::CONTENT@@@<content>
        try:
            filename_ = message.split(":::")[0]
            id__ = message.split(":::")[1]
            content_ = message.split(":::", 2)[2]
        except:
            logging.error("%d %s (%s)", self.get_status(), "fileSocket error - invalid message format", self.request.remote_ip)
            self.write_message("ERROR/invalid message format")
        else:
            filename = filename_.split("@@@", 1)[1]
            id_ = id__.split("@@@", 1)[1]
            content = base64.b64decode(content_.split("@@@", 1)[1].split("base64,", 1)[1])

            logging.info("%d %s (%s)", self.get_status(), "fileSocket message - id: %s, filename: %s, size: %i" % (id_, filename, len(content)), self.request.remote_ip)
            obj = {"torrent": [{"filename": filename, "content": content}]}
            resp = self.application._pyrtAJAX.handle("upload_torrent_socket", obj)
            response = {
                "filename": filename,
                "id": id_,
                "response": resp,
            }

            self.write_message(json.dumps(response))

    def on_close(self):
        self.application._pyrtSockets.remove("fileSocket", self.socketID)
        logging.info("%d %s (%s)", self.get_status(), "fileSocket closed", self.request.remote_ip)


class statSocket(WebSocketHandler):
    socketID = None

    @tornado.web.authenticated
    def open(self):
        self.socketID = self.application._pyrtSockets.add("statSocket", self, self.get_secure_cookie("sess_id"))
        logging.info("%d %s (%s)", self.get_status(), "statSocket opened", self.request.remote_ip)

    @tornado.web.authenticated
    def on_message(self, message):
        if self.check_ping(message):
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
        self.application._pyrtSockets.remove("statSocket", self.socketID)
        logging.info("%d %s (%s)", self.get_status(), "statSocket closed", self.request.remote_ip)


class createSocket(WebSocketHandler):
    socketID = None

    @tornado.web.authenticated
    def open(self):
        self.socketID = self.application._pyrtSockets.add("createSocket", self, self.get_secure_cookie("sess_id"))

    @tornado.web.authenticated
    def on_message(self, message):
        if self.check_ping(message):
            return

        logging.info("createSocket message: %s", message)
        resp = create.handle_message(message, writeback=self)
        if resp:
            jsonResp = {
                "request": resp[0],
                "response": resp[1],
            }
            if len(resp) > 2:
                jsonResp["output"] = resp[2]
            self.write_message(json.dumps(jsonResp))
        else:
            self.write_message("ERROR/No Response")

    def on_close(self):
        self.application._pyrtSockets.remove("createSocket", self.socketID)
        logging.info("%d createSocket closed (%s)", self.get_status(), self.request.remote_ip)


class autoSocket(WebSocketHandler):
    socketID = None

    @tornado.web.authenticated
    def open(self):
        self.socketID = self.application._pyrtSockets.add("autoSocket", self, self.get_secure_cookie("sess_id"))
        self._autoHandler = autohandler.AutoHandler(self.application)
        logging.info("%d autoSocket opened (%s)", self.get_status(), self.request.remote_ip)

    @tornado.web.authenticated
    def on_message(self, message):
        if self.check_ping(message):
            return

        logging.info("autoSocket message: %s", message)
        resp = self._autoHandler.handle_message(message)
        if resp:
            self.write_message(resp)
        else:
            self.write_message(json.dumps({
                "name": None,
                "request": message,
                "response": "ERROR",
                "error": "No response",
            }))

    def on_close(self):
        self.application._pyrtSockets.remove("autoSocket", self.socketID)
        logging.info("%d autoSocket closed (%s)", self.get_status(), self.request.remote_ip)


class RPCSocket(WebSocketHandler):
    socketID = None

    def open(self):
        logging.info("RPCsocket successfully opened")
        self.socketID = self.application._pyrtSockets.add("rpcSocket", self)
        self._RPChandler = rpchandler.RPCHandler(self.application)

    def on_message(self, message):
#        logging.info("RPCsocket message: %s", message)

        if self.check_ping(message):
            return

        auth = self._RPChandler.get_auth(message)
        if not self.application._pyrtL.checkRPCAuth(auth):
            self.application._pyrtLog.error("RPC: message denied - invalid auth key")
            logging.error("rpcSocket message denied - invalid auth key")
            self.write_message(json.dumps({"response": None, "error": "Invalid Auth"}))
            try:
                msg = json.loads(message)
                _pid = msg["PID"]
                _name = msg["name"]
                if _name != "RSS":
                    _autohandler = autohandler.AutoHandler(self.application)
                    self.application._pyrtLog.debug("RPC: got pid %d and name %s", _pid, _name)
                    _autohandler.stop_bot(_name)
                    self.application._pyrtLog.debug("RPC: stopping bot")
                    time.sleep(2)
                    self.application._pyrtLog.debug("RPC: restarting '%s' bot", _name)
                    _autohandler.start_bot(_name)
            except:
                pass

            return
        resp = self._RPChandler.handle_message(message)
        self.write_message(resp, binary=True)

    def on_close(self):
        self.application._pyrtSockets.remove("rpcSocket", self.socketID)
        logging.info("RPCsocket closed")


class Main(object):
    def __init__(self):
        pass

    def shutdown(self, *args, **kwargs):
        if self._pyrtPID != os.getpid():
            return
        logging.info("SIGTERM received, shutting down")
        self.instance.stop()

    def main(self, c):
        signal.signal(signal.SIGTERM, self.shutdown)

        global_config = {
            "server.socket_host": str(c.get("host")),
            "server.socket_port": c.get("port"),
        }

        ssl_certificate = c.get("ssl_certificate")
        ssl_keyfile = c.get("ssl_private_key")
        ssl_ca_certs = c.get("ssl_ca_certs")
        if ssl_certificate and ssl_keyfile:
            ssl_options = {
                "certfile": ssl_certificate,
                "keyfile": ssl_keyfile,
                "ca_certs": ssl_ca_certs,
            }
        else:
            ssl_options = None

        tornado.options.parse_command_line(["--logging=debug"])

        if os.path.exists(".user.pickle"):
            os.remove(".user.pickle")
        settings = {
            "static_path": os.path.join(os.getcwd(), "static"),
            "gzip": True,
            "cookie_secret": "".join([
                random.choice(string.printable) for x in range(50)
            ]),
            "login_url": "./login",
            "template_path": "htdocs",
        }
        application = tornado.web.Application([
            (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.getcwd(), "static/css/")}),
            (r"/javascript/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.getcwd(), "static/javascript/")}),
            (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.getcwd(), "static/images/")}),
            (r"/favicons/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.getcwd(), "static/favicons/")}),

            (r"/login", loginHandler),
            (r"/", index),
            (r"/index", index),
            (r"/create", createHandler),
            (r"/downloadcreation", downloadCreation),
            (r"/ajax", ajax),
            (r"/options", options),
            (r"/log", logHandler),
            (r"/stats", stats),
            (r"/download", download),
            (r"/auto", autoHandler),
            (r"/scgi", SCGIHandler),
            (r"/cache\.manifest", manifest),
            (r"/manifest-hack", manifesthack),

            (r"/ajaxsocket", ajaxSocket),
            (r"/logsocket", logSocket),
            (r"/filesocket", fileSocket),
            (r"/statsocket", statSocket),
            (r"/createsocket", createSocket),
            (r"/autosocket", autoSocket),
            (r"/RPCSocket", RPCSocket),
        ], **settings)

        application._pyrtConfig = c
        application._pyrtTemplate = tornado.template.Loader("htdocs")
        application._pyrtSockets = SocketStorage()
        application._pyrtLog = weblog.Logger(application)
        application._pyrtRT = rtorrent.rtorrent(c.get("rtorrent_socket"))
        application._pyrtL = login.Login(application)
        application._pyrtAliasStorage = aliases.AliasStore(application)
        application._pyrtDownloadHandler = downloadHandler.downloadHandler(application)
        application._pyrtAJAX = ajaxPage.Ajax(application)
        application._pyrtSTATS = statsPage.Stats(application)
        application._pyrtRemoteStorage = remotes.RemoteStorage(application)

        application._pyrtGLOBALS = {
            "config": c,
            "template": application._pyrtTemplate,
            "sockets": application._pyrtSockets,
            "log": application._pyrtLog,
            "RT": application._pyrtRT,
            "login": application._pyrtL,
            "aliasStorage": application._pyrtAliasStorage,
            "downloadHandler": application._pyrtDownloadHandler,
            "ajax": application._pyrtAJAX,
            "stats": application._pyrtSTATS,
            "remoteStorage": application._pyrtRemoteStorage,
        }

        http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_options, xheaders=True)
        logging.info("Starting webserver on http%s://%s:%i with PID %d", (ssl_options and "s" or ""), global_config["server.socket_host"], global_config["server.socket_port"], os.getpid())
        self._pyrtPID = os.getpid()

        # start listening on 10 UNIX sockets + the dedicated RSS socket
        s_rss = tornado.netutil.bind_unix_socket(".sockets/rss.interface")
        logging.info("Starting UNIX websocket on .sockets/rss.interface")
        http_server.add_socket(s_rss)
        logging.info("Starting UNIX websockets")
        for i in range(10):
            s = tornado.netutil.bind_unix_socket(".sockets/rpc%i.interface" % i)
            http_server.add_socket(s)
        try:
            http_server.listen(global_config["server.socket_port"], global_config["server.socket_host"])
        except socket.error:
            logging.error("Address already in use, aborting")
            if os.path.exists("proc/pyrt.pid"):
                os.remove("proc/pyrt.pid")

            if os.path.exists(".sockets/rss.interface"):
                os.remove(".sockets/rss.interface")
            for i in range(10):
                try:
                    os.remove(".sockets/rpc%i.interface" % i)
                except:
                    pass

            sys.exit(0)

        logging.info("Starting RSS listener")
        application._pyrtRSS = rss.RSS(application)
        self._pyrtRSSPID = application._pyrtRSS.start()

        self.instance = tornado.ioloop.IOLoop.instance()
        self.instance.start()
