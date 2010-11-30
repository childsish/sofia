#!/usr/bin/python

from svm import svm_model

class MFEGenerator:
	def __init__(self):
		self.__avg = svm_model('/home/childs/data/Tools/GenerateMFE/mfe_avg.model')
		#self.__std = svm_model('/home/childs/data/Tools/GenerateMFE/mfe_std.model')
		infile = open('/home/childs/data/Tools/GenerateMFE/mfe.range')
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
		return (self.__avg.predict((0, l, atcg, at, cg))),
		 self.__std.predict((0, l, atcg, at, cg)))
	
	def __scale(self, a, alim):
		blim = self.__tgt
		return (a - alim[0]) / (alim[1] - alim[0]) * (blim[1] - blim[0]) + blim[0]

def main(argv):
	import numpy
	
	mfes = MFEGenerator()
	
	infile = open(argv[1])
	for line in infile:
		parts = line.split()
		exp = float(parts[0])
		l, atcg, at, cg = map(lambda x:float(x.split(':')[1]), parts[1:])
		obs_avg = mfes.generate(l, atcg, at, cg)
		sys.stdout.write('%.3f\t%.3f\n'%(exp, obs_avg))
	infile.close()

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
