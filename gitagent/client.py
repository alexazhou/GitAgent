#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2016-07-24 
# @Author  : Alexa (AlexaZhou@163.com)
# @Link    : 
# @Disc    : 

import requests

class AgentClient():
    def __init__(self, ip, port):
        self.base_url = ip + ':' + port
   
    def repo_list():
        r = requests.get( self.base_url + '/repo'  , timeout=10 )
        return r.json()

    def repo_status(self, repo):
        r = requests.get( self.base_url + '/repo/' + repo , timeout=10 )
   
    def pull(self):
        pass



