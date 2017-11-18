#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open('DESCRIPTION.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

exec(open('tosker/__init__.py').read())

requirements = [  # 'Click>=6.0',
    'docker', 'tosca-parser', 'termcolor', 'six', 'enum34',
    'tabulate', 'tinydb', 'scandir', 'halo'
]

# put setup requirements (distutils extensions, etc.) here
setup_requirements = []

# put package test requirements here
test_requirements = []

# put package dev requirements here
dev_requirements = ['coverage', 'check-manifest', 'wheel', 'flake8', 'tox',
                    'Sphinx', 'isort']

setup(
    name='TosKer',
    version=__version__,
    description='A TOSCA engine working with Docker container',
    long_description=readme + '\n\n' + history,
    author="lucarin91",
    author_email='to@lucar.in',
    url='https://github.com/di-unipi-socc/TosKer',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'tosker=tosker.ui:run'
        ]
    },
    include_package_data=True,
    data_files=[
        ('/usr/share/tosker', ['data/tosker-types.yaml']),
        ('/usr/share/tosker/examples',
            ['data/examples/thoughts-app/thoughts.csar',
             'data/examples/node-mongo-csar/node-mongo.csar',
             'data/examples/sockshop-app/sockshop.csar'])

    ],
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='docker TOSCA deployment management development',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    extras_require={'dev': dev_requirements},
    tests_require=test_requirements,
    setup_requires=setup_requirements
)
