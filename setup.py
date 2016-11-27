# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

exec(open('tosker/__init__.py').read())

setup(
    name='tosKer',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=__version__,

    description='A TOSCA engine working with Docker container',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/di-unipi-socc/tosKer',

    # Author details
    author='lucarin91',
    author_email='to@lucar.in',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Console',

        'Intended Audience :: Developers',

        'Topic :: System :: Installation/Setup',

        'License :: OSI Approved :: MIT License',

        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],

    keywords='docker TOSCA deployment management development',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['test']),
    packages=find_packages(),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['docker-py', 'tosca-parser', 'termcolor', 'six'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest', 'isort'],
        'test': ['coverage'],
    },

    test_suite="tosker.tests",

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,
    # package_data={
    #     'tosker': ['*.yaml'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[
        ('/etc/tosker', ['tosker/tosker-types.yaml'])
    ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'tosker=tosker.shell:run',
        ],
    },
)
