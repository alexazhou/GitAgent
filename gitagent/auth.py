#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2016-07-24 
# @Author  : Alexa (AlexaZhou@163.com)
# @Link    : 
# @Disc    : 

import time
import hashlib

def sign( method, uri, args, password, time_stamp = None ):
    if time_stamp == None:
        time_stamp = str(int(time.time()))

    args['time'] = time_stamp
    args_keys = list(args.keys())
    args_keys.sort()

    args_str = ''
    for key in args_keys:
        if len(args_str) != 0:
            args_str += '&'

        args_str += key + '=' + str(args[key])

    str_to_sign = method + uri + '?' + args_str +password
    #print('str_to_sign:',str_to_sign)

    m = hashlib.md5()
    m.update(str_to_sign.encode('utf-8'))

    #print('md5:%s'%m.hexdigest())
    args['sign'] = m.hexdigest()
    return args
