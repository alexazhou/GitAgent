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
    [-c filename] [--type=simple/full] write: write default config format into a file
    [-c filename] run: run with config 
    '''

example_config = {
    "bind_ip":"0.0.0.0",
	"port":10000,
	"repo":{
		"self":{
			"repo_path":"./",
		}
	},
}

example_config_full = {
    "bind_ip":"0.0.0.0",
	"port":10000,
	"repo":{
		"self":{
			"repo_path":"./",
            "command":{
                "cmd1":"the command 1",
                "cmd2":"the command 2",
            }
		}
	},
    "password":"123456"
}

def write_example_config( config_name, config_type='simple' ):
    print(' write_example_config ')

    if os.path.exists( config_name ):
        print('the file already exists')
        sys.exit(1)

    if config_type == 'simple':
        config_dict = example_config
    elif config_type == 'full':
        config_dict = example_config_full
    else:
        raise Exception("Unknown config type")

    with open( config_name,'w' ) as f:
        f.write( json.dumps( config_dict, sort_keys=True, indent=4, ensure_ascii=False ) )
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
    opts, args = getopt.getopt(sys.argv[1:], 'c:', ['type=']) 
        
    if len(args) != 1:
        exit_with_message('args error') 

    cmd = args[0]
    if cmd not in ['write','run']:
        exit_with_message('args error')

    config_name = './config.json'
    config_type = 'simple'
    for option, value in opts: 
        #print("option:%s --> value:%s"%(option, value))
        if option == '-c':
            config_name = value
        elif option == '--type':
            config_type = value
    
    if cmd == 'write':
        write_example_config( config_name, config_type )
    else:
        config = load_config( config_name )
        agent.set_config( config )
        agent.start_server( )
    
    sys.exit(0)

