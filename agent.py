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
import threading

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


class GitWorker():
    def __init__(self,repo_path,git_branch,git_hash):
        self.repo_path = repo_path
        self.git_branch = git_branch
        self.git_hash = git_hash
        self.finish_ret = None

    def worker(self):

        print( "-"*20 + "git checkout " + self.git_branch + "-"*20 )
        p_gitpull = subprocess.Popen( ["git", "checkout", self.git_branch ] )
        p_gitpull.wait()
        
        ret = p_gitpull.returncode
        if ret != 0:
            self.finish_ret = False
            print("git checkout failed")
            return
        
        print( "-"*20 + "git pull" + "-"*20 )
        p_gitpull = subprocess.Popen( ["git","pull"] )
        p_gitpull.wait()

        ret = p_gitpull.returncode
        if ret != 0:
            self.finish_ret = False
            print("git pull failed")
            return

        if self.git_hash != None:
            print( "-"*20 + "git checkout " + self.git_hash +  "-"*20 )
            p_gitcheckout = subprocess.Popen( ["git","checkout", self.git_hash ] )
            p_gitcheckout.wait()

            ret = p_gitcheckout.returncode
            if ret != 0:
                self.finish_ret = False
                print("git checkout failed")
                return
        
        self.finish_ret = True

    def start(self):
        t = threading.Thread( target = self.worker )
        t.start()

    def non_block_read(self,output):
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        try:
            ret = output.read()
            if ret == None:
                ret = "".encode("utf8")

            return ret
        except:
            return "".encode("utf8")


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

class PullHandle(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self,repo):
        self.set_header("Content-Type", "application/json; charset=UTF-8") 
        
        block = False
        branch = 'master'
        commit_hash = None
            
        config = load_config()
        repo_path = config['repo'][ repo ]['repo_path']

        block = self.get_argument( 'block', '0')
        git_branch = self.get_argument( 'branch', None)
        git_hash = self.get_argument( 'hash', None)

        git_worker = GitWorker( repo_path, git_branch, git_hash )
        git_worker.start()
        
        if block == '0':#no block
            ret = 'success'
            self.write( json.dumps( { 'ret':ret },sort_keys=True,indent=4,ensure_ascii=False ))
            self.finish()
        else:#block until git worker finish
            while git_worker.finish_ret == None:
                yield tornado.gen.sleep(0.01)
            
            ret = 'success'
            self.write( json.dumps( { 'ret':ret },sort_keys=True,indent=4,ensure_ascii=False ))
            self.finish()



application = tornado.web.Application([
    ("/repo/([^/]+)/pull", PullHandle),
    ("/repo/([^/]+)", StatusHandler),
    ("/repo", RepoHandler ),
    ("/", MainHandler),
],**settings)


if __name__ == "__main__":
    config = load_config()
    application.listen( config['port'], address=config['bind_ip'] )
    tornado.ioloop.IOLoop.instance().start()
