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
import tornado.websocket
import time
import json
import git
import threading
import logging


CONFIG_JSON = './config.json'

settings = {
    'debug' : True,
	"static_path": os.path.join(os.path.dirname(__file__), "static")
}

repo_lock = {}
client_sockets = {}

pretty_json_dump = lambda x:json.dumps( x,sort_keys=True,indent=4,ensure_ascii=False )

config = None

def get_config(  ):
    return config

def set_config( value ):
    global config
    config = value

class git_work_progress( git.RemoteProgress ):
    def __init__(self,delegate):
        self.delegate = delegate

    def update(self,op_code,cur_count,max_count=None,message=""):
        print( '-->',op_code,cur_count,max_count,message )
        delegate.console_output( 'gagaga' )


class GitWorker():
    def __init__(self,repo_path,git_branch,git_hash,console_id = None):
        self.repo_path = repo_path
        self.git_branch = git_branch
        self.git_hash = git_hash
        self.console_id = console_id  
        self.finish_ret = None
        self.output = ''
        self.err_msg = None

    def console_output(self,s):
        print('console %s >>'%self.console_id,s )
        if self.console_id != None:
            try:
                ws_cocket = client_sockets[ self.console_id ]
                msg = {}
                msg['type'] = 'output'
                msg['content'] = s
                ws_cocket.write_message( msg )
            except:
                print('write to websocket failed')

    def worker(self):
        print( "-"*20 + "git checkout " + "-"*20 )
        print( "branch:" + self.git_branch )
        print( "hash:" + str(self.git_hash))
        
        progress_delegate = git_work_progress( self )
        

        try:
            repo=git.Repo( self.repo_path )
            print( 'Now repo is on branch:',repo.active_branch.name )
            
            if self.git_branch in repo.branches:
                #make sure on right branch
                if repo.active_branch.name != self.git_branch:
                    self.console_output( 'checkout %s...'%self.git_branch )
                    repo.branches[self.git_branch].checkout()
                #pull
                self.console_output( 'pull...' )
                repo.remotes['origin'].pull( progress= progress_delegate )
            else:
                #if the target branch is not existed in local, checkout out it at first
                self.console_output( 'branch %s not existed local. update remote branches...'%self.git_branch )
                origin = repo.remotes['origin']
                origin.update(  )
                self.console_output( 'checkout branch %s...'%self.git_branch )
                origin.refs[self.git_branch].checkout( b=self.git_branch )
            
            if self.git_hash != None:
                self.console_output( 'git checkout %s...'%self.git_hash )
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
            self.write( pretty_json_dump(ret) )
    return wrapper


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, GitAgent~")


class RepoHandler(tornado.web.RequestHandler):
    @return_json
    def get(self):
        config = get_config()
        ret = list(config['repo'].keys())
        return ret

class StatusHandler(tornado.web.RequestHandler):
    @return_json
    def get(self,repo):
        config = get_config()
        repo_path = config['repo'][ repo ]['repo_path']
       
        repo = git.Repo( repo_path )
        commit = repo.commit("HEAD")
        
        info = {}
        info['branch'] = repo.active_branch.name
        info['hash'] = commit.hexsha
        info['author'] = str(commit.author)
        info['message'] = commit.message
        info['busy'] = repo in repo_lock
        info['dirty'] = repo.is_dirty()
        info['untracked_files'] = repo.untracked_files
        info['changed_files'] = {}

        change = info['changed_files']
        diff = repo.index.diff(None)

        name_getter = lambda diff:diff.a_path
        for change_type in "ADRM":
            print( 'change_type:',change_type )
            change[change_type] = list(map( name_getter, diff.iter_change_type( change_type )))

        return info

class PullHandle(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self,repo):
        self.set_header("Content-Type", "application/json; charset=UTF-8") 
        
        block = self.get_argument( 'block', '0')
        git_branch = self.get_argument( 'git_branch', 'master')
        git_hash = self.get_argument( 'git_hash', None)
        console_id = self.get_argument( 'console_id', None)
        
        ret = {}
        ret['ret'] = 'success'
        ret['err_msg'] = None

        if repo in repo_lock:
            ret['ret'] = 'failure'
            ret['err_msg'] = 'repo is busying'
            self.write( pretty_json_dump(ret))
            self.finish()
            return
        else:
            repo_lock[repo] = True
            
        config = get_config()
        repo_path = config['repo'][ repo ]['repo_path']

        git_worker = GitWorker( repo_path, git_branch, git_hash, console_id )
        git_worker.start()
        
        if block == '0':#no block
            ret['ret'] = 'success'
        else:#block until git worker finish
            while git_worker.finish_ret == None:
                yield tornado.gen.sleep(0.01)
            
            ret['ret'] = git_worker.finish_ret
            ret['err_msg'] = git_worker.err_msg
        
        self.write( pretty_json_dump(ret))
        self.finish()
        del repo_lock[repo]

        
class ConsoleHandler(tornado.websocket.WebSocketHandler):
    """docstring for ConsoleHandler"""

    def check_origin(self, origin):
        return True

    def open(self):
        print("websocket open")
        self.write_message(json.dumps({
          'type': 'sys',
          'message': 'Welcome to WebSocket',
          'id': str(id(self)),
        }))
        client_sockets[ str(id(self)) ] = self

    def on_close(self):
        print("websocket close")
        del client_sockets[ str(id(self)) ]


application = tornado.web.Application([
    ("/repo/([^/]+)/pull", PullHandle),
    ("/repo/([^/]+)", StatusHandler),
    ("/repo", RepoHandler ),
    ("/console", ConsoleHandler ),
    ("/", MainHandler),
],**settings)

def start_server():

    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    
    config = get_config()
    application.listen( config['port'], address=config['bind_ip'] )
    tornado.ioloop.IOLoop.instance().start()
