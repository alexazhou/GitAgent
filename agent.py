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
import tornado.web
import time
import json
import git
import threading
import logging


#import config

CONFIG_JSON = './config.json'

settings = {
    'debug' : True,
	"static_path": os.path.join(os.path.dirname(__file__), "static")
}

repo_lock = {}

def load_config():
    config = None
    with open( CONFIG_JSON, 'r' ) as f:
        config = json.load(f)
    
    return config


class git_work_progress( git.RemoteProgress ):
    def update(self,cur_count,max_count=None,message=""):
        print( '-->',cur_count,max_count,message )


class GitWorker():
    def __init__(self,repo_path,git_branch,git_hash):
        self.repo_path = repo_path
        self.git_branch = git_branch
        self.git_hash = git_hash

        self.progress_delegate = git_work_progress()
        self.finish_ret = None
        self.output = ''
        self.err_msg = None 
    def worker(self):
        print( "-"*20 + "git checkout " + "-"*20 )
        print( "branch:" + self.git_branch )
        print( "hash:" + str(self.git_hash))

        try:
            repo=git.Repo( self.repo_path )
            if self.git_branch in repo.branches:
                #checkout branch
                repo.branches[self.git_branch].checkout()
                #pull
                repo.remotes['origin'].pull( progress=self.progress_delegate )
            else:
                #if the target branch is not existed in local, checkout out it at first
                origin = repo.remotes['origin']
                origin.update(  )
                origin.refs[self.git_branch].checkout( b=self.git_branch )
            
            if self.git_hash != None:
                git_exec = repo.git
                git_exec.checkout( self.git_hash )
            
            self.finish_ret = 'success'
        except git.exc.GitCommandError as e:
            print('Exception:',e)
            self.err_msg = str(e)
            self.finish_ret = 'failed'
        
        print( "-"*20 + "git checkout finish:" + self.finish_ret + "-"*20 )

    def start(self):
        t = threading.Thread( target = self.worker )
        t.start()


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
       
        repo = git.Repo( repo_path )
        commit = repo.commit("HEAD")
        
        info = {}
        info['hash'] = commit.hexsha
        info['author'] = str(commit.author)
        info['message'] = commit.message
        info['busy'] = repo in repo_lock
        info['dirty'] = repo.is_dirty()
        
        return info

class PullHandle(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self,repo):
        self.set_header("Content-Type", "application/json; charset=UTF-8") 
        
        block = False
        branch = 'master'
        commit_hash = None

        ret = {}
        ret['ret'] = 'success'
        ret['err_msg'] = None

        if repo in repo_lock:
            ret['ret'] = 'fail'
            self.write( json.dumps( ret, sort_keys=True, indent=4, ensure_ascii=False ))
            self.finish()
        else:
            repo_lock[repo] = True
            
        config = load_config()
        repo_path = config['repo'][ repo ]['repo_path']

        block = self.get_argument( 'block', '0')
        git_branch = self.get_argument( 'branch', None)
        git_hash = self.get_argument( 'hash', None)

        git_worker = GitWorker( repo_path, git_branch, git_hash )
        git_worker.start()
        
        if block == '0':#no block
            ret['ret'] = 'success'
        else:#block until git worker finish
            while git_worker.finish_ret == None:
                yield tornado.gen.sleep(0.01)
            
            ret['ret'] = git_worker.finish_ret
            ret['err_msg'] = git_worker.err_msg
        
        self.write( json.dumps( ret ,sort_keys=True,indent=4,ensure_ascii=False ))
        self.finish()
        del repo_lock[repo]

application = tornado.web.Application([
    ("/repo/([^/]+)/pull", PullHandle),
    ("/repo/([^/]+)", StatusHandler),
    ("/repo", RepoHandler ),
    ("/", MainHandler),
],**settings)


if __name__ == "__main__":
    
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    
    config = load_config()
    application.listen( config['port'], address=config['bind_ip'] )
    tornado.ioloop.IOLoop.instance().start()
