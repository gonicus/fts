# -*- coding: utf-8 -*-
import ldap
import ldap.filter
import syslog
from fts.ldap_utils import LDAPHandler
from fts.plugins.interface import BootPlugin


class FAIBoot(BootPlugin):

    def __init__(self):
        super(FAIBoot, self).__init__()

        self.ldap = LDAPHandler.get_instance()
        self.nfs_root= self.config.get('fai.nfs-root', '/srv/nfsroot')
        self.nfs_opts= self.config.get('fai.nfs-opts', 'nfs4')
        self.fai_flags= self.config.get('fai.flags', 'verbose,sshd,syslogd,createvt,reboot')
        self.union= self.config.get('fai.union', 'unionfs')

    def getBootParams(self, address):
        with self.ldap.get_handle() as conn:
            res = conn.search_s(
                self.ldap.get_base(),
                ldap.SCOPE_SUBTREE,
                ldap.filter.filter_format("(&(macAddress=%s)(objectClass=FAIobject))", [address]),
                ['FAIstate', 'gotoBootKernel', 'gotoKernelParameters', 'gotoLdapServer', 'cn', 'ipHostNumber'])

            if res.count() > 1:
                syslog.syslog("ignoring %s - LDAP search is not unique (%d entries match)" % (address, res.count()))
                return None

            if res.count() == 1:
                result = self.make_pxe_entry(kernel="TODO", append="TODO")
                syslog.syslog(syslog.LOG_DEBUG, "found %s, returning %s" % (address, result))
                return result

        return None

    def getInfo(self):
        return "FAI - Fully Automatic Installation"
