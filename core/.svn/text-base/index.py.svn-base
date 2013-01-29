#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Version:   1.0
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Indexer interface to index the original webpage. """

import sqlite3, os
from htmlparser import Parser
from analyzer import NaiveAnalyzer
from progress import ProgressMeter
from utils import replace_quote, ferrmsg

REFRESH_CNT = 10

class Indexer(object):
	""" Indexer class. """
	def __init__(self, dbname="index.db"):
		""" Initial indexer. 
		Warning: when initial indexer, it will overwrite existed index database in current dircetory. """
		if os.path.exists(dbname):
			os.remove(dbname)
		self.analyzer = NaiveAnalyzer()
		self.conn = sqlite3.connect(dbname)
		self.cur  = self.conn.cursor()
		# create tables to store information
		sqls = []
		sqls.append("create table urllist(url text)")
		sqls.append("create table wordlist(word text)")
		sqls.append("create table urltitle(urlid integer, title text)")
		sqls.append("create table wordlocation(urlid integer, wordid integer, location integer)");
		sqls.append("create table wordinfo(urlid integer, wordid integer, tf real)");
		sqls.append("create table linkwords(wordid integer, linkid integer)")
		sqls.append("create index urlidx on urllist(url)")
		sqls.append("create index wordidx on wordlist(word)")
		sqls.append("create index wordurlidx on wordlocation(wordid)")
		sqls.append("create index tfidx on wordinfo(tf)")
		for sql in sqls:
			self.cur.execute(sql)
		self.conn.commit()
		
	def __del__(self):
		self.conn.commit()
		self.cur.close()

	def getitems(self, html):
		""" Analyze the original webpage, and extract the valuable info.
		Here only extract the page title and all page contents. """
		try:
			p = Parser()
			p.feed(html)
		except:
			ferrmsg('Error: feed error!', 'Index')
		items = {}
	   	title = p.get_title()
		items['title'] = title
		content = p.get_content()
		items['content'] = content
		return items

	def getid(self, table, field, value):
		""" Get given field's index-value from the tabel,
		if the field is not exist, create a new one and return the newly added index. """
		sql = "select rowid from %s where %s='%s'" % (table, field, value)
		res = self.cur.execute(sql).fetchone()
		if res is None:
			sql = "insert into %s (%s) values('%s')" % (table, field, value)
			return self.cur.execute(sql).lastrowid
		else:
			return res[0]		

	def index(self, db):
		""" Index the given database. 
		Index steps consist of:
		1, seperate the content into individual words.
		2, record each word.
		3, calculate the term frequency in current page. 
		Note: index process is time-wasting. """
		conn = sqlite3.connect(db)
		cur  = conn.cursor()
		conn.text_factory = str
		dbname = db[:-3]
		sql  = "select url from %s" % dbname
		urls = [ url[0] for url in cur.execute(sql).fetchall()]
		progress = ProgressMeter(total=len(urls))
		# traverse all webpages
		for (cnt, url) in enumerate(urls):
			urlid = self.getid('urllist','url',url)
			sql = "select content from %s where url='%s'" % (dbname, url)
			html = cur.execute(sql).fetchone()[0]
			items = self.getitems(html)
			title = replace_quote(items['title'])
			sql = "insert into urltitle values(%d,'%s')" % (urlid, title)
			self.cur.execute(sql)
			content = items['content']
			words = self.analyzer.run(content)
			tfdir = {}
			# traverse all words in current webpage
			for i in range(len(words)):
				word = words[i]
				if word not in tfdir:
					tfdir[word] = 1
				else:
					tfdir[word] += 1
				wordid = self.getid('wordlist','word',word)
				sql = "insert into wordlocation values(%d,%d,%d)" % (urlid, wordid, i)
				self.cur.execute(sql)
			for (word, tf) in tfdir.items():
				wordid = self.getid('wordlist','word',word)
				sql = "insert into wordinfo values(%d,%d,%f)" % \
					  (urlid, wordid, float(tf)/len(words))
				self.cur.execute(sql)
			# update the progress
			if (cnt % REFRESH_CNT) == 0 or cnt == progress.total-1:
				progress.update(cnt+1)
		del progress
		cur.close()	


if __name__ == "__main__":
	indexer = Indexer()
	indexer.index('mydb.db')
