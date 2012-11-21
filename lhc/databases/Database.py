import os

try:
	import sqlite3
except ImportError:
	from pysqlite2 import dbapi2 as sqlite3

class Database(object):
	def __init__(self, db=':memory:', *args):
		exists = os.path.exists(db)
		self.conn = sqlite3.connect(db)
		self.curs = self.conn.cursor()
		if db == ':memory:' or not exists:
			self.createTables(*args)
	
	def createTables(self):
		raise NotImplementedError()
	
	def createIndices(self):
		raise NotImplementedError()
	
	def execute(self, qry, args=None):
		""" Only exists to cover queries that aren't covered by the existing wrapper
		 functions."""
		if args == None:
			return self.curs.execute(qry)
		return self.curs.execute(qry, args)
	
	def commit(self):
		self.conn.commit()
	
	def close(self):
		""" Create indices and close the connection """
		self.curs.close()
		self.conn.commit()
		self.conn.close()
	
	def getTables(self):
		qry = '''SELECT name FROM sqlite_master WHERE type='table' ORDER BY name'''
		return (row[0] for row in self.conn.execute(qry))
	
	def getIndices(self):
		qry = '''SELECT name FROM sqlite_master WHERE type='index' ORDER BY name'''
		return (row[0] for row in self.conn.execute(qry))
