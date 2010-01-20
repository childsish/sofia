import sys
import time

class Debug:
	def __init__(self):
		self.__on = False
		self.__times = {}

	def set(self, key='main'):
		self.__times[key] = time.time()

	def activate(self):
		self.__on = True
		self.__times['main'] = time.time()

	def write(self, output, key='main'):
		if self.__on:
			sys.stdout.write(output)

