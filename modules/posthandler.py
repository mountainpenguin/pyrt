#!/usr/bin/env python

import os
import glob
import re
import UnRAR2 

class PostHandler(object):
    def __init__(self):
        self.PATHS = {
            #regex: ( [ process chain ], path )
            #e.g.
            #blah.blah\d+\.720p: (["unrar","link"], "/var/www/localhost/blah.blah")
        }

    def checkNewFile(self, filepath):
        for regex, instructions in self.PATHS.iteritems():
            if re.search(regex, os.path.basename(filepath), re.I):
                #match!
                logme = self.process(filepath, instructions[0], instructions[1])
                return logme
    
    def process(self, filepath, processes, path):
        logMe = "Processed %s" % os.path.basename(filepath)
        for proc in processes:
            if proc == "unrar":
                response = self.unrar(filepath)
                logMe += ", unrar-ed to %s" % os.path.basename(response)
            elif proc == "link":
                path = self.link(response, path) 
                logMe += ", linked to %s" % path
        return logMe

    def unrar(self, filepath):
        """must return the filepath of the extracted file"""
        potentials = glob.glob(os.path.join(filepath, "*r*"))
        arcpath = potentials[0]
        for p in potentials:
            ext = p.split(".")[-1]
            if ext == "rar":
                arcpath = p
        archive = UnRAR2.RarFile(arcpath)
        fn = archive.infolist()[0].filename
        renameTo = "%s.%s" % (os.path.basename(filepath), fn.split(".")[-1])
        archive.extract([0], filepath)
        os.rename(os.path.join(filepath, fn), os.path.join(filepath, renameTo))
        return os.path.join(filepath, renameTo)

    def link(self, filepath, path):
        """symbolically link <filepath> to <path>/<filepath basename>"""
        lnpth = os.path.join(path, os.path.basename(filepath))
        os.symlink(filepath, lnpth)
        return lnpth
