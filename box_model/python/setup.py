#!/usr/bin/env python3

# Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the BSD 3-Clause License.

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
__author__ = 'Chace Ashcraft'
__email__ = 'chace.ashcraft@jhuapl.edu'
__version__ = '0.0.1'
install_requires = ['numpy>=1.22.1',
                    'seawater>=3.3.4',
                    'matplotlib>=3.5.1',
                    'netCDF4',
                    'pytest'
                    ]

setuptools.setup(
    name='py_box_model',
    version=__version__,
    description='Python version of Box Model from JHU',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/JHUAPL/PACMANs',
    author=__author__,
    author_email=__email__,
    license='BSD 3-Clause',
    python_requires='>=3.9',
    packages=setuptools.find_packages(),
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Oceanography',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='simulation oceanography',
    install_requires=install_requires,
    extras_require={},
    zip_safe=False
)
