#!/usr/bin/env python
# -*- coding: utf-8

from setuptools import setup

setup(name='pyqtorm',
      version='0.1',
      description='Object Relational Mapper suitable to use with PyQt Model/View framework and data edit widgets.',
      url='https://github.com/acida/pyqtorm',
      author='Alexey Verkhogluad',
      author_email='acidaone@gmail.com',
      license='MIT',
      packages=['pyqtorm'],
      install_requires=['PyQt4'],
      zip_safe=False,
      long_description='''
This python module implements simple concept of Object Relational Mapper that gives PyQt application developers
an opportunity to use advantages of object oriented design and automatic sql query generation with PyQt Model/View
framework and data edit widgets.
      '''
      )