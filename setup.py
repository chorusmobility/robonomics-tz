# -*- coding: utf-8 -*-
## ! DO NOT MANUALLY INVOKE THIS setup.py, USE CATKIN INSTEAD

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# fetch values from package.xml
setup_args = generate_distutils_setup(
    packages=[
        'pytezos','pytezos.rpc','pytezos.micheline','pytezos.tools',
        'netstruct',
        'robonomics_tz'
        ],
    package_dir={'': 'src'})
setup(**setup_args)
