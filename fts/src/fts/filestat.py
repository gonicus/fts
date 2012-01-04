# -*- coding: utf-8 -*-
import os
import stat
from time import time
from fuse import Stat


class FileStat(Stat):

    def __init__(self):
        self.st_mode = stat.S_IFDIR | 0755
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 2
        self.st_uid = os.getuid()
        self.st_gid = os.getgid()
        self.st_size = 4096
        self.st_atime = int(time())
        self.st_mtime = self.st_atime
        self.st_ctime = self.st_atime
