#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2016-07-14 14:35
# @Author  : Alexa (AlexaZhou@163.com)
# @Link    : 
# @Disc    : 

import os
import fcntl
import subprocess
import tornado.ioloop
import tornado.websocket
import tornado.web
import tornado.httpclient
import tornado.httputil
import urllib.parse
import time
import json
import git

#import config

CONFIG_JSON = './config.json'

settings = {
    'debug' : True,
	"static_path": os.path.join(os.path.dirname(__file__), "static")
}

def load_config():
    config = None
    with open( CONFIG_JSON, 'r' ) as f:
        config = json.load(f)
    
    return config


def return_json(fn):
    def wrapper( self, *args, **kwargs ):
        self.set_header("Content-Type", "application/json; charset=UTF-8") 
        ret = fn( self, *args, **kwargs )
        if ret != None:
            self.write( json.dumps( ret,sort_keys=True,indent=4,ensure_ascii=False ))
    return wrapper


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, GitAgent~")


class RepoHandler(tornado.web.RequestHandler):
    @return_json
    def get(self):
        config = load_config()
        ret = list(config['repo'].keys())
        return ret

class StatusHandler(tornado.web.RequestHandler):
    @return_json
    def get(self,repo):
        config = load_config()
        repo_path = config['repo'][ repo ]['repo_path']
        
        repo_obj = git.Repo( repo_path )
        commit = repo_obj.commit("HEAD")
        info  ={ "hash":commit.hexsha,"author":str(commit.author),"message":commit.message}

        return info


application = tornado.web.Application([
    ("/repo/([^/]+)/pull", StatusHandler),
    ("/repo/([^/]+)", StatusHandler),
    ("/repo", RepoHandler ),
    ("/", MainHandler),
],**settings)


if __name__ == "__main__":
    config = load_config()
    application.listen( config['port'], address=config['bind_ip'] )
    tornado.ioloop.IOLoop.instance().start()
