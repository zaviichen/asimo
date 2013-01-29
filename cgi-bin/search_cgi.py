#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Modified:  05/24/2010
# Version:   1.1
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" CGI script to get user's querys and return the html frame of searching results. """

import sys, os
sys.path.append(os.getcwd())

import cgitb, cgi
cgitb.enable()

import sqlite3

header = "Content-Type: text/html\n\n"
path   = "/cgi-bin"
script = "search_cgi.py"
cache_script = "cache.py"
pagelist = 10


def query(q):
	""" Call the core search engine to get the query results. """
	from core.secore import SearchEngine
	se = SearchEngine()
	se.config("config.xml")
	return se.query(q)
	
	
def get_url(urlid):
	""" Get the url according to the urlid from index database. """
	conn = sqlite3.connect("index.db")
	cur = conn.cursor()
	sql = "select url from urllist where rowid=%d" % urlid
	url = cur.execute(sql).fetchone()[0]
	return url


def get_title(urlid):
	""" Get the page title according to the urlid from index database. """
	conn = sqlite3.connect("index.db")
	cur = conn.cursor()
	sql = "select title from urltitle where urlid=%d" % urlid
	title = cur.execute(sql).fetchone()[0]
	return title
	
	
def assemble_html(**kw):
	""" Assemble the result html. """
	resids = kw.get('resids')
	query  = kw.get('query')
	
	T_reshtml = open("./template/result.htm").read()
	T_resitem = open("./template/result_item.htm").read()
	results = ''
	res_item = ''
	
	if len(resids) < pagelist:
		pageid = -1;
		
	for pageid in range(len(resids)/pagelist):
		for i in range(pagelist):
			num = pageid*pagelist+i
			urlid = resids[num]
			url = get_url(urlid)
			title = get_title(urlid)
			res_item = T_resitem % { 'url'  : url, \
									 'urlid': urlid, \
									 'title': title, \
									 'num'  : num, \
									 'path' : path, \
									 'cache_script' : cache_script }
			results += res_item
			
	residual = len(resids)%pagelist
	if residual != 0:
		for i in range(residual):
			num = (pageid+1)*pagelist+i
			urlid = resids[num]
			url = get_url(urlid)
			title = get_title(urlid)
			res_item = T_resitem % { 'url'  : url, \
									 'urlid': urlid, \
									 'title': title, \
									 'num'  : num, \
									 'path' : path, \
									 'cache_script' : cache_script }
			results += res_item
			
	reshtml = header + T_reshtml % { 'result' : results, \
								     'query'  : query,
								     'resnum' : len(resids) }
	return reshtml
	
	
def display(html):
	""" Display the html content. """
	print html
	
	
def main():
	""" Handle the query conditon and then return the CGI results. """
	form = cgi.FieldStorage()
	q = form['query'].value
	resids  = query(q)
	reshtml = assemble_html(resids=resids, query=q)
	display(reshtml)
	

if __name__ == "__main__":
	main()
	
