#!/usr/bin/env python3

from setuptools import setup, find_packages

install_requires = (
    'html2text',
    'matterhook',
    'exchangelib',
)

setup(name='calendarBot',
      version='0.1.2',
      description='Mattermost calendar Bot',
      long_description=open('README.md').read(),
      url='https://github.com/mharrend',
      author='Marco A. Harrendorf',
      author_email='marco.harrendorf@cern.ch',
      license='MIT',
      keywords='chat bot calendar mattermost',
      platforms=['Any'],
      zip_safe = False,
      packages = find_packages(),
      install_requires=install_requires,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ]
     )
