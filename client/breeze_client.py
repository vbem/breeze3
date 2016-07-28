#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Breeze client module.

Update: 2014-12-01 17:40:18
Author: vbem@163.com
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import json, urllib.request, os

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# configurations

# default timeout
DFT_TIMEOUT = urllib.request.socket._GLOBAL_DEFAULT_TIMEOUT

# request and response JSON keys and values
KEY_FUNCTION    = 'function'
KEY_ARGUMENTS   = 'arguments'
KEY_RETURN      = 'return'
KEY_EXCEPTION   = 'exception'
KEY_EXCEPTION_PLACE = 'place'
KEY_EXCEPTION_NAME  = 'name'
KEY_EXCEPTION_STR   = 'str'
VALUE_EXCEPTION_PLACE_CLIENT = os.path.splitext(os.path.basename(__file__))[0]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# common functions

def getResponse(sHostPort, sFunction, dArguments, nTimeout=DFT_TIMEOUT):
    r"""Call breeze server.
    Return breeze response dictionary.
    """
    dResponsePretty = {
        KEY_EXCEPTION   : None,
        KEY_RETURN      : None,
    }
    try:
        bRequestJson    = json.dumps(obj={KEY_FUNCTION:sFunction, KEY_ARGUMENTS:dArguments}, ensure_ascii=False).encode() # encode request JSON may fail
        oResponse       = urllib.request.urlopen(url='http://'+sHostPort, data=bRequestJson, timeout=nTimeout) # HTTP request may fail
        dResponse       = json.loads(s=oResponse.read().decode()) # decode response JSON may fail
        dResponsePretty[KEY_RETURN] = dResponse[KEY_RETURN] # 'return' may not exists
        if dResponse[KEY_EXCEPTION] is not None: # 'exception' may not exists
            dResponsePretty[KEY_EXCEPTION] = { # exception keys may not exists
                KEY_EXCEPTION_PLACE : dResponse[KEY_EXCEPTION][KEY_EXCEPTION_PLACE],
                KEY_EXCEPTION_NAME  : dResponse[KEY_EXCEPTION][KEY_EXCEPTION_NAME],
                KEY_EXCEPTION_STR   : dResponse[KEY_EXCEPTION][KEY_EXCEPTION_STR],
            }
    except Exception as oException:
        dResponsePretty[KEY_EXCEPTION] = {
            KEY_EXCEPTION_PLACE : VALUE_EXCEPTION_PLACE_CLIENT,
            KEY_EXCEPTION_NAME  : oException.__class__.__name__,
            KEY_EXCEPTION_STR   : str(oException),
        }
    return dResponsePretty
    
def getReturn(*lOther, **dOther):
    r"""Call breeze server.
    Return breeze functions' return object on success.
    Raise RuntimeError(exception_place, exception_name, exception_message) on failure.
    """
    dResponse = getResponse(*lOther, **dOther)
    if dResponse[KEY_EXCEPTION] is not None:
        raise RuntimeError(
            dResponse[KEY_EXCEPTION][KEY_EXCEPTION_PLACE],
            dResponse[KEY_EXCEPTION][KEY_EXCEPTION_NAME],
            dResponse[KEY_EXCEPTION][KEY_EXCEPTION_STR],
        )
    return dResponse[KEY_RETURN]
