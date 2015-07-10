#!/usr/bin/env python
import os
import sys

if sys.version < '2.7':
    print 'Python >= 2.7 required'
    sys.exit(1)

from setuptools import setup

long_description = '''
A simple Python package for using Twitter search functionality
that is only available through the Twitter web interface
(such as searching for tweets older than a few weeks).'''.strip()

setup(
    name = 'twitterwebsearch',
    version='0.1.3',
    author = 'Raynor Vliegendhart',
    author_email = 'ShinNoNoir@gmail.com',
    url = 'https://github.com/ShinNoNoir/twitterwebsearch',
    
    packages=['twitterwebsearch'],
    
    description = "Package for Twitter's web search",
    long_description = long_description,
    platforms = 'Any',
    license = 'MIT (see: LICENSE.txt)',
    keywords = 'Twitter, search',
    
    install_requires = open('requirements.txt').readlines(),
)
