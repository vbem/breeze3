#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Breeze functions module for IFCFD.

Update: 2015-04-23 21:30:00
Author: lilei@ink-flower.com
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import os, sys, datetime, logging
import vbem_jsonfile

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# configurations

# path
DIR_THIS                = os.path.dirname(os.path.abspath(__file__))
PATH_IFCFD_USERS        = os.path.join(DIR_THIS, 'ifcfd_users.json')
JSONFILE_IFCFD_USERS    = vbem_jsonfile.JsonFile(PATH_IFCFD_USERS)

KEY_ID              = 'id'
KEY_NAME            = 'name'
KEY_EXPIRE_DATE     = 'expire_date'
KEY_FINGERPRINT     = 'fingerprint'

DATE_FORMAT = '%Y-%m-%d'

LOGGER = logging.getLogger(__name__)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def _getUsers():
    r"""读取整个用户字典
    """
    try:
        return JSONFILE_IFCFD_USERS.load(bCache=False)
    except Exception as e:
        LOGGER.error("%r", e) # 文件打不开、格式错误等各种原因，只在日志中体现，不抛出给框架
        raise RuntimeError('用户字典读取失败 %r',e)
        
def _getUserById(sId):
    r"""按用户ID返回其全部信息
    """
    dUsers = _getUsers()
    if sId not in dUsers: # ID不再用户字典里
        raise RuntimeError('用户ID{!r}未注册'.format(sId))
    return dUsers[sId]
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# breeze functions

def getUserInfo(sId):
    r"""按用户ID返回用户信息
    
    e.g. 1 正确情况
    Request:
    {
        "function" : "getUserInfo",
        "arguments" : {
            "sId" : "test_user_1"
        }
    }
    Response:
    {
        "exception" : null,
        "return" : {
            "id"   : "test_user_1",
            "name" : "测试账号有限公司1",
            "expire_date" : "2015-12-30"
        }
    }
    
    e.g. 2 异常情况
    Request:
    {
        "function" : "getUserInfo",
        "arguments" : {
            "sId" : "test_user_0"
        }
    }
    Response:
    {
        "exception": {
            "name": "RuntimeError",
            "place": "breeze_functions",
            "str": "用户ID'test_user_0'未注册"
        },
        "return": null
    }
    """
    dInfo = _getUserById(sId)
    dInfo[KEY_ID] = sId
    dInfo.pop(KEY_FINGERPRINT, None)
    return dInfo

def checkFingerprint(sId, sFingerprint):
    r"""按用户ID和指纹进行认证，返回true

    e.g. 1 正确情况
    Request JSON:
    {
        "function" : "checkFingerprint",
        "arguments" : {
            "sId" : "test_user_1",
            "sFingerprint" : "79da2375362896f1ebf3a731fafbc48f"
        }
    }
    Response JSON:
    {
        "exception" : null,
        "return" : true
    }
    
    e.g. 2 异常情况 用户不存在
    Request JSON:
    {
        "function" : "checkFingerprint",
        "arguments" : {
            "sId" : "test_user_0",
            "sFingerprint" : "79da2375362896f1ebf3a731fafbc48f"
        }
    }
    Response JSON:
    {
        "exception": {
            "name": "RuntimeError",
            "place": "breeze_functions",
            "str": "用户ID'test_user_0'未注册"
        },
        "return": null
    }
    
    e.g. 3 异常情况 指纹不匹配
    Request JSON:
    {
        "function" : "checkFingerprint",
        "arguments" : {
            "sId" : "test_user_1",
            "sFingerprint" : "showmethemoney"
        }
    }
    Response JSON:
    {
        "exception": {
            "name": "RuntimeError",
            "place": "breeze_functions",
            "str": "用户'test_user_1'指纹错误"
        },
        "return": null
    }
    
    e.g. 4 异常情况 认证过期
    Request JSON:
    {
        "function" : "checkFingerprint",
        "arguments" : {
            "sId" : "test_user_2",
            "sFingerprint" : "1c266f9cebc5de1bf5ab0e7b98e105de"
        }
    }
    Response JSON:
    {
        "exception": {
            "name": "RuntimeError",
            "place": "breeze_functions",
            "str": "用户'test_user_2'许可已于2014-12-01过期"
        },
        "return": null
    }
    """
    dInfo = _getUserById(sId)
    
    if sFingerprint != dInfo[KEY_FINGERPRINT]:
        raise RuntimeError('用户{!r}指纹错误'.format(sId))
    
    oDateExpire = datetime.datetime.strptime(dInfo.get(KEY_EXPIRE_DATE), DATE_FORMAT).date()
    if datetime.date.today() > oDateExpire:
        raise RuntimeError('用户{!r}许可已于{}过期'.format(sId, oDateExpire))
        
    return True
