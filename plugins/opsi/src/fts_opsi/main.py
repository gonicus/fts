# -*- coding: utf-8 -*-
import syslog
from fts.bootplugin import BootPlugin
from fts.jsonrpc_proxy import JSONServiceProxy


class OPSIBoot(BootPlugin):

    enabled = False

    def __init__(self):
        super(OPSIBoot, self).__init__()

        self.proxy_url = self.config.get('opsi.proxy')
        if not self.proxy_url:
            syslog.syslog(syslog.LOG_ERR, "no opsi.proxy defined - disabling module")
            return

        self.enabled = True

        self.append = self.config.get('opsi.append', "noapic ramdisk_size=175112 init=/etc/init initrd=opsi-root.gz reboot=b video=vesa:ywrap,mtrr vga=791 quiet splash")
        self.lang = self.config.get('opsi.language', 'en')
        self.force_hostname = self.config.get('opsi.force_hostname', True)
        if self.force_hostname.lower() in ['yes', '1', 'true', 'on']:
            self.force_hostname = True
        elif self.force_hostname.lower() in ['no', '0', 'false', 'off']:
            self.force_hostname = False
        else:
            syslog.syslog(syslog.LOG_ERR, "Parse error: Option '{option}', given value '{value}' is invalid!".format(option='opsi.force_hostname', value=self.force_hostname))
            return

        self.force_domain = self.config.get('opsi.force_domain', False)
        if self.force_domain.lower() in ['yes', '1', 'true', 'on']:
            self.force_domain = True
        elif self.force_domain.lower() in ['no', '0', 'false', 'off']:
            self.force_domain = False
        else:
            syslog.syslog(syslog.LOG_ERR, "Parse error: Option '{option}', given value '{value}' is invalid!".format(option='opsi.force_domain', value=self.force_domain))
            return

    def getBootParams(self, address):
        if not self.enabled:
            return None

        proxy = JSONServiceProxy(self.proxy_url, mode='GET')

        status= "localboot"
        kernel = "localboot"
        append = ""
        product= ""

        client_id = proxy.getClientIdByMac(address)
        if not client_id:
            return None

        # Find netboot product with actionRequest
        for product in proxy.getNetBootProductStates_hash(client_id)[client_id]:
            if 'actionRequest' in product and not product['actionRequest'] in ['', 'undefined', 'none']:
                status = "install"
                product = "product=%s" % product['productId']
                break

        # Installation requested
        if status == "install":
            params = []

            # append short hostname
            if self.force_hostname:
                params.append("hn=%s" % client_id.split('.', 1)[0])

            # append domain
            if self.force_domain:
                params.append("dn=%s" % client_id.split('.', 1)[1])

            # Set product
            params.append(product)

            # Load pc key
            pc_key = proxy.getOpsiHostKey(client_id)
            if pc_key:
                params.append("pckey=%s" % pc_key)

            # Load depot server for this client
            depot_id = proxy.getDepotId(client_id)
            if depot_id:
                params.append("service=%s" % depot_id)

            # Set language
            params.append("lang=%s" % self.lang)

            # Set PXE parameters
            kernel = "opsi-install"
            append = " ".join([self.append] + params)

        return self.make_pxe_entry(kernel, append, label="OPSI boot - powered by FTS")


    def getInfo(self):
        return "OPSI - Open PC Server Integration"
