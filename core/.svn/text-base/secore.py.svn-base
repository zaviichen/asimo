#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Modified:  05/24/2010
# Version:   1.1
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Search engine interface. """

from config import Config
from webspider import SpiderController
from index import Indexer
from rank  import ContentRanker, PageRanker
from query import SimpleQuery
from utils import ferrmsg, normalize


class SearchEngine(object):
	""" Interface Class for the core of search engine. """
	def __init__(self):
		pass
			
	def config(self, config):
		""" Read the config file to configure the search engine. """
		self.config = Config()
		self.config.load(config)
			
	def collect_page(self):
		""" Configure the spider controller to collect the webpages. """
		sc = SpiderController( name       = self.config.spider,     \
							   start_url  = self.config.start_url,  \
							   spider_num = self.config.spider_num, \
							   page_limit = self.config.page_limit, \
							   oridb      = self.config.oridb,      \
							   mergedb    = self.config.mergedb,    \
							   headers    = self.config.headers
							  )
		sc.work()
		
	def index(self):
		""" Index the got pages, include two steps:
		1, index the pages for all page information.
		2, pageranke the page and also store the scores to
		   accelerate the query process."""
		idb  = self.config.indexdb
		odb  = self.config.oridb
		sort = int(self.config.sort)
		
		indexer = Indexer(idb)
		indexer.index(odb)
		del indexer
		
		pr = PageRanker(idb, sort)
		pr.build_links(odb)
		pr.pagerank()
		del pr

	def query(self, q, op='and'):
		""" Query and rank the results. Calculate the scores according to 
		both factors of the content rank and page rank. 
		Note: In this function, calculate the content rank scores in the real time
		and only get the page rank scores which are preloaded in the database. """
		db   = self.config.indexdb
		sort = int(self.config.sort)
		cr_fac = float(self.config.rankers['content'])
		pr_fac = float(self.config.rankers['page'])

		query = SimpleQuery(db)
		words = query.parse_query(q)
		urls  = query.query(q)
		
		if len(urls) == 0:
			return []

		scores = {}
		valid_fac   = {}
		valid_score = {}
		if cr_fac > 0:
			cr = ContentRanker(db, sort)
			cr_scores = cr.score(urls, words)
			cr_scores = normalize(cr_scores)
			valid_fac['content'] = cr_fac
			valid_score['content'] = cr_scores

		if pr_fac > 0:
			pr = PageRanker(db, sort)
			pr_scores = pr.score(urls, words)
			pr_scores = normalize(pr_scores)
			valid_fac['page'] = pr_fac
			valid_score['page'] = pr_scores

		for urlid in urls:
			scores[urlid] = 0.0
			try:
				for key in valid_fac.keys():
					scores[urlid] += valid_fac[key]*valid_score[key][urlid]
			except:
				ferrmsg("Error: urlid(%s) is not find in the results of each rank." % urlid, \
						'SECore')
				
		res = sorted(scores.items(), key=lambda v:v[1], reverse=sort)
		res = [t[0] for t in res]
		return res
		

if __name__ == "__main__":
	se = SearchEngine()
	se.config("config.xml")
	## se.collect_page()
	## se.index()
	print se.query('python')

