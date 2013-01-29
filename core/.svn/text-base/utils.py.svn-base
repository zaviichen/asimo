#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Version:   1.0
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Valuable variable-definitions and functions. """

import re,sys

# global variables
RET_ERROR  = 'RET_ERROR'
PAGE_LIMIT = 100
SPIDER_NUM = 10
REFRESH_CNT = int(SPIDER_NUM*PAGE_LIMIT/100)

ERROR_LOG = "error.log"

# util functions
def check_for_sqlite(s):
	""" Check sql for sqlite database.
	In sqlite, it doesn't allow the sql contains a single-quote('),
	so this function is using regular expression to check the given 
	string whether to contain a single-quote. """
	pattern = re.compile("'")
	res = pattern.search(s)
	if not res: return True
	else:   return False

def replace_quote(s):
	""" Replace a single quote to two continuous single qutoes. """
	if s is None:
		return RET_ERROR
	else:
		return re.sub("'","''",s)

def normalize(li, max_=0):
	""" Normalize the list with given max value.
	If the max_ is default value, and it is automatically 
	assigned the maximun value in the list. """
	if type(li) == list:
		if max_ == 0:
			max_ = max(li)
		return [e/float(max_) for e in li]
	elif type(li) == dict:
		if max_ == 0:
			max_ = max(li.values())
		return dict([(k, v/float(max_)) for (k,v) in li.items()]) 

def ferrmsg(msg, proc=''):
	""" Format the error message to the error log file. """
	f = open(ERROR_LOG, 'a')
	f.write("<%s>: %s\n" % (proc,msg))
	f.close()


if __name__ == "__main__":
	print normalize([1,2,3,4,5,6])
	print normalize({'a':1, 'b':2, 'c':4})
