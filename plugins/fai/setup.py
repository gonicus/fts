#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "fts_fai",
    version = "0.9",
    author = "Jan Wenzel",
    author_email = "wenzel@gonicus.de",
    description = "PXE/TFTP supplicant application",
    long_description = """
    This application generates pxelinux configuration files for systems identified by mac addresses.
    It needs a TFTP-Server to allow controlling network boot.
""",
    license = "LGPL",
    url = "http://www.gosa-project.org",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Monitoring',
    ],

    download_url = "http://oss.gonicus.de/pub/gosa",
    packages = find_packages('src', exclude=['examples', 'tests']),
    package_dir={'': 'src'},

    include_package_data = True,
    package_data = {
    },

    zip_safe = False,

    install_requires = [
        'fts',
        'python-ldap',
    ],

    entry_points = """
    [fts.plugin]
    fai = fts_fai.main:FAIBoot
""",
)
