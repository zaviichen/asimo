#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Version:   1.0
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Ranker interface to rank the results, 
include two ranker: content-based ranker and pageranke-based ranker. """

import sqlite3
from webspider import MyHTMLParser
from progress import ProgressMeter
from utils import REFRESH_CNT, check_for_sqlite, ferrmsg, normalize


class Ranker(object):
	""" Base class of the ranker. 
	dbname: the index database, default: index.db
	rev:    toggle to rank the results with which scores' order. 
	        If true, from high to low, otherwise. Default: Ture."""
	def __init__(self, dbname="index.db", rev=True):
		self.conn = sqlite3.connect(dbname)
		self.cur  = self.conn.cursor()
		self.rev  = rev
		self.scores  = {}
		self.urlids  = [] 	# result urls
		self.wordids = []	# query words

	def __del__(self):
		self.cur.close()

	def score(self):
		pass
	
	def rank(self):
		pass


class ContentRanker(Ranker):
	""" The content-based ranker. """
	def __init__(self, dbname="index.db", rev=True):
		Ranker.__init__(self, dbname, rev)
		
	def tf_score(self):
		""" Calculate the scores according to the term frequency. """
		scores = {}
		for urlid in self.urlids:
			url_score = 0.0
			for wordid in self.wordids:
				sql = "select tf from wordinfo where urlid=%d and wordid=%d" % (urlid,wordid)
				tf = self.cur.execute(sql).fetchone()[0]
				url_score += tf
			scores[urlid] = url_score
		return scores

	def score(self, urlids, wordids):
		""" Calcalute the scores according to the content.
		only associating to term frequency in this version. """
		self.urlids  = urlids
		self.wordids = wordids
		self.scores = self.tf_score()
		return self.scores

	def rank(self, urlids, wordids):
		""" Rank the results according to the scores. """
		self.score()
		return sorted(self.scores.items(), key=lambda v:v[1], reverse=self.rev)		


class PageRanker(Ranker):
	""" The pagerank-based ranker. """
	def __init__(self, dbname="index.db", rev=True):
		Ranker.__init__(self, dbname, rev)
		self.url_ids  = []
		self.from_ids = {}
		self.to_ids   = {}
		self.all_scores = {}
		
	def get_urlid(self, url):
		""" Get urlid via url query in database. """
		sql = "select rowid from urllist where url='%s'" % (url)
		res = self.cur.execute(sql).fetchone()
		if res is None:
			return 0
		else:
			return res[0]

	def urls2ids(self, urls):
		""" Manipulate url-to-urlid in groups. """
		ids = []
		for url in urls:
			if check_for_sqlite(url):
				id_ = self.get_urlid(url)
				if id_ == 0: continue
				ids.append(id_)
		return ids
		
	def build_links(self, db):
		""" Analyze the original page, and rebulid the link-relationship. """
		print "Building links' connections."
		conn = sqlite3.connect(db)
		cur  = conn.cursor()
		conn.text_factory = str
		dbname = db[:-3]
		sql  = "select url from %s" % dbname
		urls = [ url[0] for url in cur.execute(sql).fetchall()]
		
		urlids    = self.urls2ids(urls)
		from_urls = dict([(urlid,[]) for urlid in urlids])
		to_urls   = dict([(urlid,[]) for urlid in urlids])

		progress = ProgressMeter(total=len(urls))
		for (cnt, url) in enumerate(urls):
			urlid = self.get_urlid(url)
			p = MyHTMLParser(url)
			sql = "select content from %s where url='%s'" % (dbname, url)
			content = cur.execute(sql).fetchone()[0]
			try:    p.feed(content)
			except:	ferrmsg('Error: feed error in %s.' % url, 'Rank')
			to_urls[urlid] = self.urls2ids(p.htm_urls())
			for lid in to_urls[urlid]:
				if lid not in from_urls.keys():
					continue
				else:
					from_urls[lid].append(urlid)
			# update the progress
			if (cnt % REFRESH_CNT) == 0 or cnt == progress.total-1:
				progress.update(cnt+1)
		self.url_ids  = urlids
		self.from_ids = from_urls
		self.to_ids   = to_urls

	def save_pr(self):
		""" Save the link-relationship in the index database. """
		sql = "drop table if exists pagelink"
		self.cur.execute(sql)
		sql = "create table pagelink(urlid integer, fromids text, toids text, pagerank real)"
		self.cur.execute(sql)
		for urlid in self.url_ids:
			fromids = ' '.join([str(v) for v in self.from_ids[urlid]])
			toids   = ' '.join([str(v) for v in self.to_ids[urlid]])
			sql = "insert into pagelink values(%d,'%s','%s',%f)" \
				  % (urlid, fromids, toids, self.all_scores[urlid])
			self.cur.execute(sql)
		self.conn.commit()

	def pagerank(self, limit=20):
		""" Calculate the pagerank scores from multi-interations. """
		for urlid in self.url_ids:
			self.all_scores[urlid] = 1.0

		for i in range(limit):
			for urlid in self.url_ids:
				score = self.all_scores[urlid]
				for fromid in self.from_ids[urlid]:
					score += self.all_scores[fromid] / \
							 (len(self.from_ids[fromid])+len(self.to_ids[fromid]))
				score *= 0.85
				score += 0.15
				self.all_scores[urlid] = score
		self.save_pr()

	def score(self, urlids, wordids):
		""" Only get the scores from the database. """
		self.urlids  = urlids
		self.wordids = wordids
		for urlid in self.urlids:
		   	sql = "select pagerank from pagelink where urlid=%d" % urlid
			pr = self.cur.execute(sql).fetchone()[0]
			self.scores[urlid] = pr
		return self.scores

	def rank(self, urlids, wordids):
		""" Rank the results. """
		self.score(urlids, wordids)
		return sorted(self.scores.items(), key=lambda v:v[1], reverse=self.rev)


if __name__ == "__main__":
	## ranker = ContentRanker()
	## print ranker.rank([1,2],[2])
	ranker = PageRanker()
	ranker.build_links('mydb.db')
	#ranker.pagerank()
	#print ranker.rank([1,2],[2])
