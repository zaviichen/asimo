#!/usr/bin/env python
#-*- coding:utf-8 -*-

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Version:   1.0
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Web spider script to collect the webpages. 
This web spider script could create multi-thread sub-spiders to 
collect the webpages simultaneously, and cooperate under the same spider controller. 

This script is customized, with customizing these properties:
1, the spider number
2, each spider's collect limit
3, the start url
4, the disguise headers
"""

import re, sqlite3, gzip, threading, os, glob
import urllib2, urlparse
from sgmllib import SGMLParser
from cStringIO import StringIO
from Queue import Queue
from bloom import Bloom
from utils import RET_ERROR, replace_quote, ferrmsg

Headers = { 'User-Agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
			'Accept-encoding':'gzip'}
	
class MyHTMLParser(SGMLParser):
	""" Simple HTML parser class. """
	def __init__(self, url):
		SGMLParser.__init__(self)
		self.starturl = url
		self.urls = []
		self.title = ''
		self.htmutls = []
	
	def start_a(self, attrs): 
		""" Called whenever meeting a <A> tag. 
		Get all href(urls) in the page. """                   
		href = [v for k, v in attrs if k=='href']  
		if href:
			self.urls.extend(href)
		
	def htm_urls(self):
		""" Analyze the urls. """
		rehtm = re.compile("(htm|html)$")
		rehttp = re.compile("^(http|https)://")
		for url in self.urls:
			if rehtm.search(url):
				if rehttp.search(url):
					self.htmutls.append(url)
				else:
					self.htmutls.append(urlparse.urljoin(self.starturl, url))
		return self.htmutls


class Retriever(object):
	""" Page retriever class. """
	def __init__(self, url, headers=Headers):
		self.url  = url
		self.file = self.filename(url)
		self.data = None
		self.opener  = urllib2.build_opener()
		self.headers = headers
		
	def filename(self, url):
		return url
		
	def download(self):
		""" Download a given url's page. """
		try:
			request = urllib2.Request(url=self.url, headers=self.headers)
			page = self.opener.open(request)
			if page.code == 200:
				gzipdata = page.read()
				gzipstream = StringIO(gzipdata)
				try:
					self.data  = gzip.GzipFile(fileobj=gzipstream).read()
				except IOError:
					self.data = gzipdata
		except:
			ferrmsg('Error: invalid URL "%s"' % self.url, 'Spider')
			self.data = RET_ERROR
		return self.data
		
				
class WebSpider(threading.Thread):
	""" Web spider class. """
	def __init__(self, name, lock, queue, bloom, limit, headers):
		super(WebSpider, self).__init__(name=name)
		self.lock  = lock
		self.queue = queue
		self.bloom = bloom
		self.limit = limit
		self.num_gets = 0
		self.headers = headers
		
	def get_page(self, url):
		""" Download the page and analyze all the urls in this page. """
		rer = Retriever(url, self.headers)
		retval = rer.download()	
		if retval is RET_ERROR:
			return retval
		self.num_gets += 1
		if url not in self.bloom:
			self.bloom.add(url)
		
		p = MyHTMLParser(url)
		try:
			p.feed(retval)
		except:
			ferrmsg('Error: feed error in url: %s' % url, 'Spider')
		for link in p.htm_urls():
			if (link not in self.bloom) and (link not in self.queue.queue):
				self.queue.put(link)
		return retval

	def save_page(self, cur, url, data):
		""" Save the whole page to the database. """
		data = replace_quote(data)
		sql = "insert into %s values('%s','%s');" % (self.name, url, data)
		cur.execute(sql)
			
	def run(self):
		""" Begin to run in multi-threading environment. """
		print "%s run..." % self.name
		self.lock.acquire()
		try:
			conn = sqlite3.connect('%s.db'%self.name, timeout=1)
			cur  = conn.cursor()
			sql  = "create table %s (url text, content text);" % self.name
			cur.execute(sql)
		finally:
			self.lock.release()
		
		while not self.queue.empty():
			url = self.queue.get()
			## print "Spider: %s, Page: %s" % (self.name, self.num_gets)
			## print "Getting: ", url
			data = self.get_page(url)
			if data is RET_ERROR: continue
			self.lock.acquire()
			try:
				self.save_page(cur, url, data)
			finally:
				self.lock.release()
			if self.num_gets > self.limit: break
			
		conn.commit()
		cur.close()


class SpiderController(object):
	""" Spider controller class. """
	def __init__(self, **config):
		self.name       = config.get('name', 'sc')
		self.start_url  = config.get('start_url', "http://www.g.cn")
		self.oridb      = config.get('oridb', 'original.db')
		self.headers    = config.get('headers', Headers)
		self.mergedb    = int(config.get('mergedb', 1))
		self.spider_num = int(config.get('spider_num', 10))
		self.page_limit = int(config.get('page_limit', 100))
		self.bloom = Bloom(1024, 5)
		self.queue = Queue()
		self.queue.put(self.start_url)
		
	def work(self):
		""" Run the spider controller, and create the spiders to collect the pages. 
		Warning: runuing a spider controller will remove all the *.db file in current directory. """
		for db in glob.glob('*.db'):
			os.remove(db)
		lock = threading.RLock()

		name = '%s_spider_ori' % self.name
		disdbs = ['%s.db' % name]
		spider = WebSpider(name, lock, self.queue, self.bloom, self.page_limit, self.headers)
		if self.spider_num > 1:
			spider.limit = self.spider_num
		else:
			spider.limit = self.page_limit
		spider.start()
		spider.join()
		
		if self.spider_num > 1:		
			for i in range(self.spider_num):
				name = '%s_spider_%d' % (self.name, i)
				spider = WebSpider(name, lock, self.queue, self.bloom, \
								   self.page_limit, self.headers)
				spider.start()
				disdbs.append('%s.db' % name)
			for i in range(self.spider_num):
				spider.join()

		if self.mergedb:
			self.merge(self.oridb, disdbs)
			
	def merge(self, tardb, srcdbs):
		""" Merge the distribute databases. 
		For sqlite does not support multi-thread very well, so each spider 
		will save its own collected pages in an individual database.
		With this funcion, it could merge the distribute databases to a single one. """
		tconn = sqlite3.connect(tardb)
		tcur  = tconn.cursor()
		sql = "create table %s (url text, content text)" % tardb[:-3]
		tcur.execute(sql)
		for src in srcdbs:
			print "Processing %s ..." % src
			sconn = sqlite3.connect(src)
			scur  = sconn.cursor()
			sconn.text_factory = str
			sql = "select * from %s " % src[:-3]
			contents = scur.execute(sql).fetchall()
			for content in contents:
				sql = "insert into %s (url, content) values('%s','%s')" % \
					  (tardb[:-3], content[0], replace_quote(content[1]))
				tcur.execute(sql)
			scur.close()
		tconn.commit()
		tconn.close()
		## for db in srcdbs:
		##	os.remove(db)
		
		
def main():
	SpiderController(start_url="http://www.google.com").work()
	
	
if __name__ == '__main__':
	import os
	import glob
	for db in glob.glob('*.db'):
		os.remove(db)
	main()
