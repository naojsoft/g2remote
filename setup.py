#! /usr/bin/env python
#
import os
from g2remote.version import version

srcdir = os.path.dirname(__file__)

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

setup(
    name = "g2remote",
    version = version,
    author = "Software Division, Subaru Telescope, NAOJ",
    author_email = "ocs@naoj.org",
    description = ("Programs for conducting extended remote "
                   "observation with Subaru Telescope."),
    license = "BSD",
    keywords = "subaru, telescope, remote, observation, tools",
    url = "http://naojsoft.github.com/g2remote",
    packages = ['g2remote'],
    package_data = {'g2remote': ['html/*']},
    python_requires = '>=3.7',
    install_requires = ['pyotp>=2.3.0', 'paramiko>=2.7.1', 'pyyaml>=5.3.1',
                        'jinja2>=3.0.0'],
    scripts = ["scripts/g2connect", "scripts/g2connect.bat"],
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
)
