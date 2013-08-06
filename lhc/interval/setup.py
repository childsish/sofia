#!/usr/bin/python

from distutils.core import setup, Extension

setup (name = "interval",
 version = "1.0",
 ext_modules = [
  Extension('interval', sources=['interval.cpp'])
 ]
) 

