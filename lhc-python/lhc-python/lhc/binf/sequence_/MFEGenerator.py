#!/usr/bin/python

import os

from paths.misc import mfe
from libsvm import svmutil

class MFEGenerator:
	def __init__(self, mdl, rng):
		self.mdl = svm_load_model
		self.__avg = svm_model(os.path.join(mfe, '%s_avg.model'%typ))
		self.__std = svm_model(os.path.join(mfe, '%s_std.model'%typ))
		infile = open(os.path.join(mfe, '%s.range'%typ))
		infile.readline()
		self.__tgt = tuple(map(float, infile.readline().split()))
		self.__len_lim = tuple(map(float, infile.readline().split()[1:]))
		self.__atcg_lim = tuple(map(float, infile.readline().split()[1:]))
		self.__at_lim = tuple(map(float, infile.readline().split()[1:]))
		self.__cg_lim = tuple(map(float, infile.readline().split()[1:]))
		infile.close()
	
	def generate(self, l, atcg, at, cg):
		l = self.__scale(l, self.__len_lim)
		atcg = self.__scale(atcg, self.__atcg_lim)
		at = self.__scale(at, self.__at_lim)
		cg = self.__scale(cg, self.__cg_lim)
		return self.__avg.predict((0, l, atcg, at, cg)),\
		 self.__std.predict((0, l, atcg, at, cg))
	
	def __scale(self, a, alim):
		blim = self.__tgt
		return (a - alim[0]) / (alim[1] - alim[0]) * (blim[1] - blim[0]) + blim[0]
