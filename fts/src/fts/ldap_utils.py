# -*- coding: utf-8 -*-
import ldap
import ldapurl
import ldap.sasl
import types
import logging
import sys
from fts import Config
from contextlib import contextmanager


class LDAPHandler(object):
    """
    The *LDAPHandler* creates connections based on what's configured in the
    ``[ldap]`` section of the clacks configuration files. Here's a list of valid
    keywords:

    ============== =============
    Key            Description
    ============== =============
    url            LDAP URL to connect to
    bind_dn        DN to connect with
    bind_secret    Password to connect with
    pool_size      Number of parallel connections in the pool
    retry_max      How often a connection should be tried after the service is considered dead
    retry_delay    Time delta on which to try a reconnection
    ============== =============

    Example::

        [ldap]
        url = ldap://ldap.example.net/dc=example,dc=net
        bind_dn = cn=manager,dc=example,dc=net
        bind_secret = secret
        pool_size = 10
    """
    connection_handle = []
    connection_usage  = []
    instance = None

    def __init__(self):
        self.config = Config.get_instance()
        self.log = logging.getLogger(__name__)

        # Initialize from configuration
        get = self.config.get
        self.__url = ldapurl.LDAPUrl(get("ldap.url"))
        self.__bind_user = get('ldap.bind_user', default=None)
        self.__bind_dn = get('ldap.bind_dn', default=None)
        self.__bind_secret = get('ldap.bind_secret', default=None)
        self.__pool = int(get('ldap.pool_size', default=10))

        # Sanity check
        if self.__bind_user and not ldap.SASL_AVAIL:
            self.log.error("bind_user needs SASL support, which doesn't seem to be available in python-ldap")
            sys.exit(1)

        if not self.__url:
            self.log.error("there is no 'url' specified in the 'ldap' section of the configuration file")
            sys.exit(1)

        # Initialize static pool
        LDAPHandler.connection_handle = [None] * self.__pool
        LDAPHandler.connection_usage = [False] * self.__pool

    def get_base(self):
        """
        Return the configured base DN.

        ``Return``: base DN
        """
        return self.__url.dn

    def get_connection(self):
        """
        Get a new connection from the pool.

        ``Return``: LDAP connection
        """
        # Are there free connections in the pool?
        try:
            next_free = LDAPHandler.connection_usage.index(False)
        except ValueError:
            raise Exception("no free LDAP connection available")

        # Need to initialize?
        if not LDAPHandler.connection_handle[next_free]:
            get = self.config.get
            self.log.debug("initializing LDAP connection to %s" %
                    str(self.__url))
            conn = ldap.ldapobject.ReconnectLDAPObject("%s://%s" % (self.__url.urlscheme,
                self.__url.hostport),
                retry_max=int(get("ldap.retry_max", default=3)),
                retry_delay=int(get("ldap.retry_delay", default=5)))

            # We only want v3
            conn.protocol_version = ldap.VERSION3

            # If no SSL scheme used, try TLS
            if ldap.TLS_AVAIL and self.__url.urlscheme != "ldaps":
                try:
                    conn.start_tls_s()
                except ldap.PROTOCOL_ERROR as detail:
                    self.log.debug("cannot use TLS, falling back to unencrypted session")

            try:
                # Simple bind?
                if self.__bind_dn:
                    self.log.debug("starting simple bind using '%s'" %
                        self.__bind_dn)
                    conn.simple_bind_s(self.__bind_dn, self.__bind_secret)
                elif self.__bind_user:
                    self.log.debug("starting SASL bind using '%s'" %
                        self.__bind_user)
                    auth_tokens = ldap.sasl.digest_md5(self.__bind_user, self.__bind_secret)
                    conn.sasl_interactive_bind_s("", auth_tokens)
                else:
                    self.log.debug("starting anonymous bind")
                    conn.simple_bind_s()

            except ldap.INVALID_CREDENTIALS as detail:
                self.log.error("LDAP authentication failed: %s" %
                        str(detail))

            LDAPHandler.connection_handle[next_free] = conn

        # Lock entry
        LDAPHandler.connection_usage[next_free] = True

        return LDAPHandler.connection_handle[next_free]

    def free_connection(self, conn):
        """
        Free an allocated pool connection to make it available for others.

        ================= ==========================
        Parameter         Description
        ================= ==========================
        conn              Allocated LDAP connection
        ================= ==========================
        """
        index = LDAPHandler.connection_handle.index(conn)
        LDAPHandler.connection_usage[index] = False

    @contextmanager
    def get_handle(self):
        """
        Context manager which is meant to be used with the :meth:`with` statement.
        For an example see above.

        ``Return``: LDAP connection
        """
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.free_connection(conn)

    @staticmethod
    def get_instance():
        """
        Singleton for *LDAPHandler* objects. Return the instance.

        ``Return``: LDAPHandler instance
        """
        if not LDAPHandler.instance:
            LDAPHandler.instance = LDAPHandler()
        return LDAPHandler.instance


def map_ldap_value(value):
    """
    Method to map various data into LDAP compatible values. Maps
    bool values to TRUE/FALSE and unicode values to be 'utf-8' encoded.

    ================= ==========================
    Parameter         Description
    ================= ==========================
    value             data to be prepared for LDAP
    ================= ==========================

    ``Return``: adapted dict
    """
    if type(value) == types.BooleanType:
        return "TRUE" if value else "FALSE"
    if type(value) == types.UnicodeType:
        return value.encode('utf-8')
    if type(value) == types.ListType:
        return map(map_ldap_value, value)
    return value


def unicode2utf8(data):
    """
    Method to map unicode strings to utf-8.

    ================= ==========================
    Parameter         Description
    ================= ==========================
    data              string or list to convert
    ================= ==========================

    ``Return``: adapted data
    """
    return map_ldap_value(data)


def normalize_ldap(data):
    """
    Convert *single values* to lists.

    ================= ==========================
    Parameter         Description
    ================= ==========================
    data              input string or list
    ================= ==========================

    ``Return``: adapted data
    """
    if type(data) != types.ListType:
        return [data]

    return data
