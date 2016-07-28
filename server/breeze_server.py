#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""Breeze server module.

Update: 2014-12-01 17:40:18
Author: vbem@163.com

       UTF-8 JSON ->               Py Object ->
Client ------------- Breeze Server ------------ Python
       <- UTF-8 JSON               <- Py Object
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import os, logging, logging.handlers, pydoc, inspect, re
import flask
import breeze_functions

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# breeze server configurations

# server port
SERVER_PORT = 9000

# flask application
SERVER_APP = flask.Flask(import_name=__name__)
SERVER_APP.config['JSON_AS_ASCII'] = False # for UTF-8 JSON response, http://flask.pocoo.org/docs/0.10/api/#flask.json.dumps

# path
DIR_THIS = os.path.dirname(os.path.abspath(__file__))
DIR_HOME = os.path.dirname(DIR_THIS)
DIR_LOG  = os.path.join(DIR_HOME, 'log')
PATH_LOGFILE = os.path.join(DIR_LOG, 'breeze.log')

# request and response JSON keys and values
KEY_FUNCTION    = 'function'
KEY_ARGUMENTS   = 'arguments'
KEY_RETURN      = 'return'
KEY_EXCEPTION   = 'exception'
KEY_EXCEPTION_PLACE = 'place'
KEY_EXCEPTION_NAME  = 'name'
KEY_EXCEPTION_STR   = 'str'
VALUE_EXCEPTION_PLACE_SERVER    = os.path.splitext(os.path.basename(__file__))[0]
VALUE_EXCEPTION_PLACE_FUNCTIONS = breeze_functions.__name__

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# breeze functions configurations

# show pydoc HTML when HTTP request method is not POST
FUNCTIONS_PYDOC_ON = True

# secure valid functions dictionary
FUNCTIONS_DICT = {s:o for (s,o) in inspect.getmembers(breeze_functions) if inspect.isfunction(o) and not s.startswith('_')}

def getPydocHtml(oModule):
    r"""Get pydoc for a module.
    """
    sHtml = pydoc.html.document(*pydoc.resolve(thing=oModule))
    sHtml = re.sub(r'<tr bgcolor="#aa55cc">.*?</td></tr></table></td></tr></table>', '</table>', sHtml, flags=re.DOTALL) # remove modules
    sHtml = re.sub(r'<tr bgcolor="#55aa55">.*?</td></tr></table>', '</table>', sHtml, flags=re.DOTALL) # remove data
    sHtml = re.sub(r'<a href=.*?</a>', '', sHtml) # remove links
    return sHtml

# rendered pydoc HTML
FUNCTIONS_PYDOC_HTML = getPydocHtml(breeze_functions)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# logging configurations

# logging level
LOGGING_LEVEL = logging.DEBUG

# logging handler
LOGGING_FOMATTER = logging.Formatter(fmt='{}\n%(asctime)s %(name)s %(levelname)s %(module)s:%(funcName)s:%(lineno)s %(message)s'.format('-'*80), datefmt='%Y-%m-%d %H:%M:%S')
LOGGING_HANDLER = logging.handlers.TimedRotatingFileHandler(filename=PATH_LOGFILE, when='MIDNIGHT', backupCount=30)
LOGGING_HANDLER.setFormatter(LOGGING_FOMATTER)

def modifyLogger(oLogger):
    r"""Modify logger's level and handler.
    """
    oLogger.setLevel(LOGGING_LEVEL)
    oLogger.handlers.clear()
    oLogger.addHandler(LOGGING_HANDLER)
    return oLogger
    
# loggers
LOGGER_WERKZEUG  = modifyLogger(logging.getLogger('werkzeug'))
LOGGER_SERVER    = modifyLogger(SERVER_APP.logger)
LOGGER_FUNCTIONS = modifyLogger(logging.getLogger(breeze_functions.__name__))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# common functions

def getResponseDict(oException=None, sExceptionPlace=None, oReturn=None):
    r"""Generate response dictionary.
    """
    dResponse = {KEY_EXCEPTION:None, KEY_RETURN:None}
    if oException is not None:
        dResponse[KEY_EXCEPTION] = {
            KEY_EXCEPTION_PLACE: sExceptionPlace,
            KEY_EXCEPTION_NAME: oException.__class__.__name__,
            KEY_EXCEPTION_STR: oException.__str__(),
        }
    else:
        dResponse[KEY_RETURN] = oReturn
    return dResponse

def getResponseObject():
    r"""Call function according to request and return flask response object.
    """
    try: # prepare function and arguments
        dRequest = flask.request.get_json(force=True) # request JSON maybe invalid
        dArguments = dRequest[KEY_ARGUMENTS] # key "arguments" may not exists
        sFunction = dRequest[KEY_FUNCTION] # key "function" may not exists
        oFunction = FUNCTIONS_DICT[sFunction] # function maybe not in valid functions dictionary
    except Exception as e:
        return flask.jsonify(getResponseDict(oException=e, sExceptionPlace=VALUE_EXCEPTION_PLACE_SERVER))
        
    try: # execute specific breeze function
        oReturn = oFunction(**dArguments) # arguments may not match, execution may fail
    except Exception as e:
        return flask.jsonify(getResponseDict(oException=e, sExceptionPlace=VALUE_EXCEPTION_PLACE_FUNCTIONS))
        
    try: # generate response object
        return flask.jsonify(getResponseDict(oReturn=oReturn)) # JSONify function's return may fail
    except Exception as e:
        return flask.jsonify(getResponseDict(oException=e, sExceptionPlace=VALUE_EXCEPTION_PLACE_SERVER))
        
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# flask routers

@SERVER_APP.route(rule='/', methods=['GET', 'POST'])
def flaskHomepage():
    r"""Breeze server homepage view.
    """
    if flask.request.method == 'POST':
        oResponse = getResponseObject()
        if LOGGER_SERVER.isEnabledFor(logging.DEBUG):
            LOGGER_SERVER.debug( # server logging for POST
                '\n@ Remote: %s\n@ Headers:\n%s\n@ Request:\n%s\n@ Response:\n%s',
                flask.request.remote_addr,
                str(flask.request.headers).strip(),
                flask.request.get_data(as_text=True).strip(),
                oResponse.get_data(as_text=True).strip()
            )
        return oResponse
    elif FUNCTIONS_PYDOC_ON and flask.request.method == 'GET':
        return FUNCTIONS_PYDOC_HTML
    else:
        flask.abort(405)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main

def main():
    r"""Main process.
    """
    # LOGGER_SERVER.debug("all loggers: %s", logging.Logger.manager.loggerDict)
    SERVER_APP.run(host='0.0.0.0', port=SERVER_PORT, threaded=True, debug=True, use_evalex=False)
    
if __name__ == '__main__':
    main()
    