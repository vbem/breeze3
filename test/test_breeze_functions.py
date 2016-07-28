#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Test cases for breeze_functions.

Update: 2014-12-16 18:07:00
Author: lilei@ink-flower.com
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import os, sys, pprint, urllib.request

DIR_THIS = os.path.dirname(os.path.abspath(__file__))
DIR_HOME = os.path.dirname(DIR_THIS)
DIR_SERVER = os.path.join(DIR_HOME, 'server')
DIR_CLIENT = os.path.join(DIR_HOME, 'client')
sys.path.extend([DIR_SERVER, DIR_CLIENT])

import breeze_client, breeze_server

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# configurations

HOSTPORT = 'localhost:{}'.format(breeze_server.SERVER_PORT)
TIMEOUT = 3

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# common functions

def _requestByRaw(sHostPort, sPost, sNote):
    print('-'*80)
    print('{} {}'.format(sys._getframe().f_code.co_name, sys._getframe().f_locals))
    try:
        oResponse = urllib.request.urlopen(url='http://'+sHostPort, data=sPost.encode(), timeout=TIMEOUT)
        print('response code: {}\nresponse data:\n{}'.format(oResponse.status, oResponse.read().decode()))
    except Exception as e:
        print(repr(e))

def _requestByClient(sNote, sHostPort, sFunction, dArguments):
    print('-'*80)
    print('{} {}'.format(sys._getframe().f_code.co_name, sys._getframe().f_locals))
    print(breeze_client.getResponse(sHostPort, sFunction, dArguments))
        
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main

def _test():
    r"""Test.
    """
    _requestByRaw(HOSTPORT, 'asdf', 'JSON格式错误')
    _requestByRaw(HOSTPORT, '{"function":null}', '没有arguments')
    _requestByRaw(HOSTPORT, '{"arguments":null}', '没有function')
    _requestByRaw(HOSTPORT, '{"function":"getUserInfo", "arguments":[1,2,3]}', 'arguments不合法')
    _requestByRaw(HOSTPORT, '{"function":"os.path.dirname", "arguments":{"sId" : "test_user_1"}}', 'function不合法')
    _requestByRaw(HOSTPORT, '{"function":"getUserInfo", "arguments":{"sId" : "test_user_0"}}', '找不到用户')
    _requestByRaw(HOSTPORT, '{"function":"getUserInfo", "arguments":{"sId" : "test_user_1"}}', '找到用户')
    
    _requestByClient('链接错误地址', 'www.ink-flower2.com', 'os.path.dirname', {"sId" : "test_user_1"})
    _requestByClient('链接错误路径', HOSTPORT+'/asdf', 'os.path.dirname', {"sId" : "test_user_1"})
    _requestByClient('传非法function', HOSTPORT, _test, {"sIdxx" : "test_user_1"})
    _requestByClient('传非法arguments', HOSTPORT, 'getUserInfo2', ValueError)
    _requestByClient('触发server异常', HOSTPORT, 'getUserInfo2', {"sIdxx" : "test_user_1"})
    _requestByClient('触发functions异常', HOSTPORT, 'getUserInfo', {"sId" : "test_user_0"})
    _requestByClient('正常', HOSTPORT, 'getUserInfo', {"sId" : "test_user_1"})
    
    
if __name__ == "__main__":
    exit(_test())

        
