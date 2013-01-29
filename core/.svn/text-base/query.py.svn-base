#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Modified:  05/24/2010
# Version:   1.1
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Query interface to analyze the user's query condition and get the results. """

import sqlite3
from analyzer import NaiveAnalyzer

class Query(object):
	""" Base query class. """
	# Only support 'and' and 'or' query operation
	# but only 'and' under test.
	QueryOp = ['and','or']
	
	def __init__(self, dbname="index.db"):
		self.conn = sqlite3.connect(dbname)
		self.cur  = self.conn.cursor()
		self.analyzer = NaiveAnalyzer()
		self.op = 'and'
		self.res = []

	def __del__(self):
		self.cur.close()

	def query(self, q, op='and'):
		pass

	def query_op(self, s, t):
		""" Opearte the query condition. """
		if self.op == 'and':
			return s & t
		elif self.op == 'or':
			return s | t
		else:
			pass


class SimpleQuery(Query):
	""" Simple query class. """
	def query(self, q, op='and'):
		""" Query the condition and return the results. """
		wordids = self.parse_query(q)
		sets = []
		for wordid in wordids:
			sql = "select urlid from wordlocation where wordid=%d" % wordid
			urlids = self.cur.execute(sql).fetchall()
			s = set()
			for urlid in urlids:
				s.add(urlid[0])
			sets.append(s)
			
		if len(sets) >0 :
			res = set(sets[0])
			for i in range(1,len(sets)):
				res = self.query_op(res,sets[i])
			self.res = list(res)
		else:
			self.res = []
			
		return self.res

	def parse_query(self, q):
		""" Analyze the query condition and get wordid from the database. """
		words = self.analyzer.run(q)
		wordids = []
		for word in words:
			sql = "select rowid from wordlist where word='%s'" % word
			try:
				wordid = self.cur.execute(sql).fetchone()[0]
				wordids.append(wordid)
			except:
				pass
		return wordids


if __name__ == "__main__":
	query = SimpleQuery()
	print query.query('fudan email')
		
