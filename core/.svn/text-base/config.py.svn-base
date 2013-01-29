#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Version:   1.0
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Configure file parser interface. Configure file must be a XML file. """

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

class Config(ElementTree.ElementTree):
	""" Configure parser class. """
	def __init__(self):
		self.root  = None
		self.elems = []
		self.headers = {}
		self.rankers = {}
		
	def load(self, config):
		try:
			self.root = self.parse(config)
			self.elems = self.getiterator()
		except:
			ferrmsg("Error: failed building xml tree.", 'Config')
		for elem in self.elems:
			self.start_element(elem)

	def start_element(self, elem):
		pass_elems = set(['config','database','headers','rank','rankers','file'])
		ename = elem.tag
		attrs = elem.attrib

		if   ename == 'oridb'     : self.oridb   = attrs['name']
		elif ename == 'indexdb'   : self.indexdb = attrs['name']  
		elif ename == 'mergedb'   : self.mergedb = elem.text	
		elif ename == 'spider'    : self.spider  = attrs['name']
		elif ename == 'spider_num': self.spider_num = elem.text
		elif ename == 'page_limit': self.page_limit = elem.text
		elif ename == 'start_url' : self.start_url  = elem.text
		elif ename == 'User-Agent' or ename == 'Accept-encoding':
			self.headers[ename] = elem.text
		elif ename == 'content' or ename == 'page':
			self.rankers[ename] = elem.text
		elif ename == 'sort'   : self.sort    = elem.text
		elif ename == 'errfile': self.errfile = elem.text
		else: pass


if __name__ == "__main__":
	import sys
	if len(sys.argv) < 2:
		print "Usage: python config.py config.xml"
		sys.exit(1)
	c = Config()
	c.load(sys.argv[1])
	
