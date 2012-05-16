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

import time
import random
import string
import logging

class Message(object):
    """Class to contain a message"""
    def __init__(self, msg_id, text, level=2, level_name="INFO"):
        self.msg_id = msg_id
        self.text = text
        self.level = level
        self.level_name = level_name

class Logger(object):
    """Class defining a globally shared logging module for 'public' log messages

        Should be handled by the /log path of the server
    """
    INFO = 2
    WARNING = 3
    ERROR = 1
    DEBUG = 4
    def __init__(self):
        self.RECORDS = [] # contains id tags sorted by time (most recent first)
        self.RECORD = {} # log information with key `id`

    def id_gen(self):
        return "".join([random.choice(string.letters+string.digits) for x in range(20)])

    def info(self, msg, *args, **kwargs):
        """Log an "info" level message"""
        _id = self.id_gen()

        #create message
        if "%" in msg:
            msg_ = msg % tuple(args)
        else:
            msg_ = msg
        message = self.fmt(Message(_id, msg_))

        self.RECORDS += [_id]
        self.RECORD[_id] = message

    def error(self, msg, *args, **kwargs):
        """Log an "error" level message"""
        _id = self.id_gen()
        if "%" in msg:
            msg_ = msg % args
        else:
            msg_ = msg
        message = self.fmt(Message(_id, msg_, level=self.ERROR, level_name="ERROR"))
        self.RECORDS += [_id]
        self.RECORD[_id] = message

    def warning(self, msg, *args, **kwargs):
        """Log a "warning" level message"""
        _id = self.id_gen()
        if "%" in msg:
            msg_ = msg % args
        else:
            msg_ = msg
        message = self.fmt(Message(_id, msg_, level=self.WARNING, level_name="WARNING"))
        self.RECORDS += [_id]
        self.RECORD[_id] = message

    def debug(self, msg, *args, **kwargs):
        """Log a "debug" level message"""
        _id = self.id_gen()
        if "%" in msg:
            msg_ = msg % args
        else:
            msg_ = msg
        message = self.fmt(Message(_id, msg_, level=self.DEBUG, level_name="DEBUG"))
        self.RECORDS += [_id]
        self.RECORD[_id] = message

    def fmt(self, msg):
        if msg.level == self.ERROR:
            colour = "#FF0000" #red
        elif msg.level == self.INFO:
            colour = "#00CC33" #green
        elif msg.level == self.WARNING:
            colour = "#0000CC" #blue
        elif msg.level == self.DEBUG:
            colour = "#585858" #grey
        timestamp = time.strftime("%d %b %Y %H:%M:%S")
        fmt = "(%s) %s" % (timestamp, msg.text)
        msg.colour = colour
        msg.fmt = fmt
        return msg

    def html_format(self, msg, addnewflag=False):
        if addnewflag:
            msg.new = " new_message"
        else:
            msg.new = ""
        return """
                        <tr class='log_row log_message level_%(level)s%(new)s' id='%(msg_id)s'>
                            <td class='log_level level_%(level)s'>%(level_name)s</td>
                            <td class='log_message'>%(fmt)s</td>
                        </tr>""" % msg.__dict__

    def html(self):
        construct = ""
        for _id in reversed(self.RECORDS):
            construct += self.html_format(self.RECORD[_id])
        return construct

    def returnNew(self, lastID):
        try:
            idx = self.RECORDS.index(lastID)
        except ValueError:
            idx = 0
        new = self.RECORDS[idx+1:]
        construct = ""
        for _id in reversed(new):
            construct += self.html_format(self.RECORD[_id], addnewflag=True)
        return construct
