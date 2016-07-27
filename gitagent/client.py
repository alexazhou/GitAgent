#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2016-07-24 
# @Author  : Alexa (AlexaZhou@163.com)
# @Link    : 
# @Disc    : 

import requests
import threading
import time
import json
from ws4py.client.threadedclient import WebSocketClient


class WebSocketConsole(WebSocketClient):
    def __init__(self, ip, port, console_receiver):
        self.websocket_id = None
        self.console_receiver = console_receiver
        url = "ws://%s:%s/console"%(ip, port)
        WebSocketClient.__init__(self, url, protocols=['http-only', 'chat'])

    def opened(self):
        self.console_output('websocket console connected')
    
    def closed(self, code, reason=None):
        self.console_output("websocket console disconnected") 

    def received_message(self, m):
        #print('console ->',m)
        data = json.loads( m.data.decode('utf-8') )
        if data['type'] == 'sys':
            self.websocket_id = data['id']
        elif data['type'] == 'output':
            self.console_output( data['content'] )

    def console_output(self,s):
        self.console_receiver( s )


class AgentClient():
    def __init__(self, ip, port, console_receiver = print):
        self.web_console = None
        self.ip = ip
        self.port = port
        self.base_url = ip + ':' + port
        self.console_receiver = console_receiver
        
    def repo_list(self):
        r = requests.get( 'http://' + self.base_url + '/repo'  , timeout=10 )
        if r.status_code != 200:
            raise Exception('Request failed with status_code:%s response:%s'%(r.status_code, r.content))
        return r.json()

    def repo_status(self, repo):
        r = requests.get( 'http://' + self.base_url + '/repo/' + repo , timeout=10 )
        if r.status_code != 200:
            raise Exception('Request failed with status_code:%s response:%s'%(r.status_code, r.content))
        return r.json()
   
    def pull(self, repo, git_branch='master', git_hash=None, block = 1):
        data ={ 'git_branch':git_branch, 'block':block }
        if git_hash != None:
            data['git_hash'] = git_hash

        if self.web_console != None:
            data['console_id'] = self.web_console.websocket_id
            
        #print( 'connect GitAgent to deploy...' )   
        r = requests.post( 'http://' + self.base_url + '/repo/' + repo + '/pull' , data=data, timeout=600 )
        if r.status_code != 200:
            raise Exception('Request failed with status_code:%s response:%s'%(r.status_code, r.content))
        r_json = r.json()
        return r_json

    def connect_websocket(self):
        self.web_console = WebSocketConsole( self.ip, self.port, self.console_receiver )
        def console_worker():
            self.web_console.connect()
            self.web_console.run_forever()

        t = threading.Thread( target=console_worker )
        t.setDaemon( True )
        t.start()

        time_begin = time.time()
        while time.time() - time_begin < 5:
            if self.web_console.websocket_id != None:
                break
            time.sleep(0.1)
        else:
            raise Exception('WebSocket Connect Error')

