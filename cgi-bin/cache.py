#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Modified:  05/24/2010
# Version:   1.1
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" CGI script to display the cache page. """

import cgi, cgitb
cgitb.enable()

import sqlite3

header = "Content-Type: text/html\n\n"
path   = "/cgi-bin"
script = "cache.py"


def get_cache(urlid, indexdb="index.db", oridb="original.db"):
	""" Get the cache page from the original database. """
	# First get the url from urlid
	conn = sqlite3.connect(indexdb)
	cur = conn.cursor()
	sql = "select url from urllist where rowid=%d" % urlid
	url = cur.execute(sql).fetchone()[0]
	cur.close()

	# Second get the cache from the url
	conn = sqlite3.connect(oridb)
	cur = conn.cursor()
	sql = "select content from %s where url='%s'" % (oridb[:-3], url)
	cache = None
	try:
		cache = cur.execute(sql).fetchone()[0]
	except:
		cache = "Unresolved cache!"
	cur.close()
	return cache


def main():
	""" Handle the cache requirement and display the cache page. """
	form = cgi.FieldStorage()
	cache = get_cache(int(form['urlid'].value))
	print header + cache


if __name__ == "__main__":
	main()
