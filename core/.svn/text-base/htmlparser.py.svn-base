#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Version:   1.0
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Self-defined HTML parser interface. """

from HTMLParser import HTMLParser
from htmlentitydefs import entitydefs

class Parser(HTMLParser):
	""" HTML parser class. """
	def __init__(self):
		HTMLParser.__init__(self)
		self.taglevels = []
		self.handle_tags = ['title']
		self.processing = None
		self.data = ''
		self.title = ''
		self.content = ''

	def handle_starttag(self, tag, attrs):
		""" Called whenever a start tag is encountered. """
		# Processing a previous version of this tag.
		# Close it out and then start anew on this one.
		if len(self.taglevels) and self.taglevels[-1] == tag:
			self.handle_endtag(tag)

		self.taglevels.append(tag)

		if tag in self.handle_tags:
			self.data = ''
			self.processing = tag

	def handle_endtag(self, tag):
		""" Called whenever a end tag is encountered. """
		# We didn't have a start tag for this way, just ignore.
		# e.g., a miswrited end tag
		if tag not in self.taglevels:
			return

		while len(self.taglevels):
			starttag = self.taglevels.pop()
			if starttag in self.handle_tags:
				self.process(starttag)
			if starttag == tag:
				break

	def handle_data(self, data):
		""" This function simply records incoming data
		if we are presently inside a handle tag. """
		if self.processing:
			self.data += data
		self.content += data

	def handle_entityref(self, name):
		""" Called whenever a entity is encountered.
		If entity is recognized, convert it to related value,
		otherwise, just record the stream value. """
		if entitydefs.has_key(name):
			self.handle_data(entitydefs[name])
		else:
			self.handle_data('&%s;'%name)

	def handle_charref(self, name):
		""" Called whenever a character reference is encountered. """
		try:
			charnum = int(name)
		except ValueError:
			return
		if charnum < 1 or charnum > 255:
			return
		self.handle_data(chr(charnum))

	def process(self, tag):
		""" Process the interested tags. """
		if tag == 'title':
			self.title = self.data
			
		self.processing = None

	def get_title(self):
		""" Return the html title. """
		return self.title

	def get_content(self):
		""" Return the html content. """
		return self.content


if __name__ == "__main__":
	html = """<HTML>
<HEAD>
<TITLE>title &amp; Intro&#174;
</HEAD>
<BODY>This is content text.
</BODY>
</HTML>"""
	import sys
	p = Parser()
	if len(sys.argv) == 1:
		p.feed(html)
	else:
		p.feed(open(sys.argv[1]).read())
	print p.get_title()
	print p.get_content()

	
