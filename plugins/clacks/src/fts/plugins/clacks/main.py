# -*- coding: utf-8 -*-
from fts.plugins.interface import BootPlugin
from clacks.common.components import AMQPServiceProxy


class ClacksBoot(BootPlugin):

    def __init__(self):
        super(ClacksBoot, self).__init__()
        proxy_url = self.config.get('clacks.proxy')
        if not proxy_url:
            raise RuntimeError("no clacks.proxy defined - bailing out")

        self.proxy = AMQPServiceProxy(proxy_url)

    def getBootParams(self, address):
        return self.proxy.systemGetBootString(None, address)

    def getInfo(self):
        return "Clacks - object remote boot"
