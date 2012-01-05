# -*- coding: utf-8 -*-
import urllib2
import cookielib
from urllib import quote
from urlparse import urlparse
from json import dumps, loads


class JSONRPCException(Exception):
    """
    Exception raises if there's an error when processing JSONRPC related
    tasks.
    """
    def __init__(self, rpcError):
        super(JSONRPCException, self).__init__(rpcError)
        self.error = rpcError


class JSONServiceProxy(object):
    """
    The JSONServiceProxy provides a simple way to use RPC
    services from various clients. Using the proxy object, you
    can directly call methods without the need to know where
    it actually gets executed.

    Example::

        >>> proxy = JSONServiceProxy('https://user:secret@localhost')
        >>> proxy.what_ever_method()

    =============== ============
    Parameter       Description
    =============== ============
    serviceURL      URL used to connect to the HTTP service
    serviceName     *internal*
    opener          *internal*
    =============== ============

    The URL format is::

       (http|https)://user:password@host:port/rpc
    """

    def __init__(self, serviceURL=None, serviceName=None, opener=None,
            mode='POST'):
        self.__serviceURL = serviceURL
        self.__serviceName = serviceName
        self.__mode = mode

        if not opener:
            http_handler = urllib2.HTTPHandler()
            https_handler = urllib2.HTTPSHandler()
            cookie_handler = urllib2.HTTPCookieProcessor(cookielib.CookieJar())

            # Split URL, user, password from provided URL
            tmp = urlparse(serviceURL)
            if tmp.username:
                username = tmp.username
                password = tmp.password
                self.__serviceURL = "%s://%s:%s%s" % (tmp.scheme, tmp.hostname,
                        tmp.port, tmp.path)
                passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                passman.add_password(None, self.__serviceURL, username, password)
                auth_handler = urllib2.HTTPBasicAuthHandler(passman)
                opener = urllib2.build_opener(http_handler, https_handler,
                        cookie_handler, auth_handler)

            else:
                opener = urllib2.build_opener(http_handler, https_handler, cookie_handler)

        self.__opener = opener

    def __getattr__(self, name):
        if self.__serviceName != None:
            name = "%s.%s" % (self.__serviceName, name)

        return JSONServiceProxy(self.__serviceURL, name, self.__opener, self.__mode)

    def __call__(self, *args, **kwargs):
        if len(kwargs) > 0 and len(args) > 0:
            raise JSONRPCException("JSON-RPC does not support positional and keyword arguments at the same time")

        if len(kwargs):
            postdata = dumps({"method": self.__serviceName, 'params': kwargs, 'id': 'jsonrpc'})
        else:
            postdata = dumps({"method": self.__serviceName, 'params': args, 'id': 'jsonrpc'})

        if self.__mode == 'POST':
            respdata = self.__opener.open(self.__serviceURL, postdata).read()
        else:
            respdata = self.__opener.open(self.__serviceURL + "?" + quote(postdata)).read()

        resp = loads(respdata)
        if resp['error'] != None:
            raise JSONRPCException(resp['error'])
        else:
            return resp['result']
