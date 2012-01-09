FTS README
==========

What is FTS?
^^^^^^^^^^^^

FTS is a TFTP supplicant package. It uses a FUSE in conjunction to your
ordinary TFTP service (like atftpd, tftpd, etc.) in order to provide
dynamically generated start configurations for certain MAC addresses.

How does it work?
^^^^^^^^^^^^^^^^^

If you have different mechanisms which compete for PXE boot authority,
it may be hard to glue all of them together. For that reason, FTS creates
a filesystem layer on top of your ordinary (static) tftpboot directory
and tries to resolve the requested files within it's modules first - then
falling back to your static files.

There are currently modules for OPSI, FAI (LDAP), LTSP5 (LDAP) and Clacks.
If you've installed all of them, a booting client will first request a
file partly named after it's hardware address (MAC). Every FTS module is
asked if it want's to handle the provided MAC address in an specific
order. The first one which claims to have a proper PXE configuration will
provide a virtual file which is then served to the client.
