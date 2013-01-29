#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Version:   1.0
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Accidence ananlyzer interface. """

import re

ignorewords = set(['the','of','to','and','a','in','is','it'])

class Analyzer(object):
	""" Base class of accidence analyzer. """
	def __init__(self):
		pass

	def run(self, text):
		pass

class NaiveAnalyzer(Analyzer):
	""" Most simplest analyzer which only seperate the words acconding to 
	non-words in regular expression, and discard the words in the ignorewords list. """
	def run(self, text):
		splitter = re.compile("\W*")
		res = []
		for s in splitter.split(text):
			s = s.lower()
			if s in ignorewords: continue
			res.append(s)
		return res
