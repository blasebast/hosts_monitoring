# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='hosts_monitoring',
    version='0.1.0',
    description='monitoring hosts basing on /etc/hosts file',
    long_description=readme,
    author='Sebastian Blasiak',
    author_email='sebastian.blasiak@gmail.com',
    url='https://github.com/blasebast/hosts_monitoring',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

