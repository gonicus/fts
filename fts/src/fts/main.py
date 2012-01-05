#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage:

Call "fts" as root to mount the layer filesystem.
Call "fusermount -u PATH" as root to unmount the layer filesystem.
"""
import os
import syslog
import fuse
import sys
from fts.pxefs import PXEfs


def main():
    # Fuse sanity check
    if not hasattr(fuse, '__version__'):
        raise RuntimeError, \
            "Your fuse python module doesn't know it's version, probably it's too old."

    # Setup
    fuse.fuse_python_api = (0, 2)
    fuse.feature_assert('stateful_files', 'has_init')

    syslog.openlog('fts', syslog.LOG_PID, syslog.LOG_USER)
    usage = """
TFTP supplicant: provide pxelinux configuration files based on external state
information.

""" + fuse.Fuse.fusage

    fs = PXEfs(version="%prog " + fuse.__version__, usage=usage,
            dash_s_do='setsingle')

    # Disable multithreading and set up the fs parser
    fs.multithreaded = False
    fs.parser.add_option(mountopt="root",
            metavar="PATH",
            default=os.sep,
            help="mirror filesystem from PATH [default: %default]")
    fs.parse(values=fs, errex=1)

    try:
        if fs.fuse_args.mount_expected():
            os.chdir(fs.root)

    except OSError:
        syslog.syslog(syslog.LOG_ERR, "can't enter static filesystem")
        sys.exit(1)

    syslog.syslog(syslog.LOG_INFO, "fts is now mounted on %s" % fs.cfg_path)
    fs.main()


if __name__ == '__main__':
    main()
