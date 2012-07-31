#!/usr/bin/python

from distutils.core import setup, Extension

setup (name = "digen",
 version = "1.0",
 ext_modules = [
  Extension('digen', sources=['digenmodule.cpp', 'digen.cpp'])
 ]
) 
