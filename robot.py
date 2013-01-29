#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      05/24/2010
# Version:   1.1
# Copyright (c) 2010 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Interface to create or update the database. """

from core.secore import SearchEngine
	
se = SearchEngine()
se.config("config.xml")
se.collect_page()
se.index()	