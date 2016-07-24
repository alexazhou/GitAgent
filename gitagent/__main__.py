#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2016-07-23 
# @Author  : Alexa (AlexaZhou@163.com)
# @Link    : 
# @Disc    : 

import sys
import os
import json
import getopt
import gitagent.agent as agent

help_doc = '''usage: [options] cmd
    [-f filename] write: write default config into a file
    [-f filename] run: run with config 
    '''

example_config = {
    "bind_ip":"0.0.0.0",
	"port":10000,
	"repo":{
		"self":{
			"repo_path":"./",
		}
	}
}

def write_example_config( config_name ):
    print(' write_example_config ')

    if os.path.exists( config_name ):
        print('the file already exists')
        sys.exit(1)

    with open( config_name,'w' ) as f:
        f.write( json.dumps( example_config,sort_keys=True,indent=4,ensure_ascii=False ) )
        print('write config to %s successed'%config_name)
    

def load_config( config_name ):
    print(' load_config:',config_name)
    config = None
    with open( config_name, 'r' ) as f:
        config = json.load(f)
    
    return config

def exit_with_message( message ):
    print( message )
    print(help_doc) 
    sys.exit(1)


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'w:c:', []) 
        
    if len(args) != 1:
        exit_with_message('args error') 

    cmd = args[0]
    if cmd not in ['write','run']:
        exit_with_message('args error')

    config_name = './config.json' 
    for option, value in opts: 
        #print("option:%s --> value:%s"%(option, value))
        if option == '-c':
            config_name = value
    
    if cmd == 'write':
        write_example_config( config_name )
    else:
        config = load_config( config_name )
        agent.set_config( config )
        agent.start_server( )
    
    sys.exit(0)

