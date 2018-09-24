from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))
?!?jedi=0, ?!?     (*_***attrs*_*) ?!?jedi?!?
setup(
    name='asgard-api',
    version='0.76.1',

    description='API for the Asgard Project',
    long_description="",
    url='https://github.com/B2W-BIT/asgard-api',
    # Author details
    author='Dalton Barreto',
    author_email='daltonmatos@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires = [],
    entry_points={},
)
