#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup configuration for hosts_monitoring."""

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_text = f.read()

setup(
    name='hosts_monitoring',
    version='0.2.0',
    description='Monitor LAN hosts via ping/arp, export Prometheus metrics',
    long_description=readme,
    author='Sebastian Blasiak',
    author_email='sebastian.blasiak@gmail.com',
    url='https://github.com/blasebast/hosts_monitoring',
    license=license_text,
    packages=find_packages(exclude=('tests', 'docs')),
    entry_points={
        'console_scripts': [
            'hosts-monitoring=hmon.__main__:main',
        ],
    },
    install_requires=[
        'smoothlogging>=1.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
        ],
    },
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
    ],
    keywords='monitoring prometheus hosts ping arp network',
    project_urls={
        'Bug Reports': 'https://github.com/blasebast/hosts_monitoring/issues',
        'Documentation': 'https://github.com/blasebast/hosts_monitoring/blob/main/README.rst',
        'Source': 'https://github.com/blasebast/hosts_monitoring',
    },
)
