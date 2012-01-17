# -*- coding: utf-8 -*-
import syslog
from fts.bootplugin import BootPlugin
from fts.jsonrpc_proxy import JSONServiceProxy

# Optionally load AMQP module to provide a more
# failsafe mode.
has_amqp = False
try:
    from clacks.common import AMQPServiceProxy
    has_amqp = True
except ImportError:
    pass


class ClacksBoot(BootPlugin):

    enabled = False

    def __init__(self):
        super(ClacksBoot, self).__init__()
        proxy_url = self.config.get('clacks.proxy')
        if not proxy_url:
            syslog.syslog(syslog.LOG_ERR, "no clacks.proxy defined - disabling module")
            return

        if proxy_url.startswith('amqp'):
            if not has_amqp:
                syslog.syslog(syslog.LOG_ERR, "AMQP is configured, but there's no clacks.common available - disabling module")
                return
            self.proxy = AMQPServiceProxy(proxy_url)
        else:
            self.proxy = JSONServiceProxy(proxy_url)

        self.enabled = True

    def getBootParams(self, address):
        return self.proxy.systemGetBootString(None, address)

    def getInfo(self):
        return "Clacks - object remote boot"
