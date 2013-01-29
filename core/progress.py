#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Version:   1.0
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Progress meter interface to display progress meter in the command window. """

import time, sys, math

class ProgressMeter(object):
	""" Progress meter class. """
	def __init__(self, **kw):
		self.total = int(kw.get('total', 100))
		self.count = int(kw.get('count', 0))
		self.tick  = str(kw.get('tick', '-'))
		self.stream   = kw.get('stream', sys.stdout)
		self.inc_mode = kw.get('inc_mode', False)
		# number of ticks in meter
		self.meter_ticks = int(kw.get('ticks', 60))
		self.meter_div   = float(self.total) / self.meter_ticks
		self.meter_value = int(self.count / self.meter_div)
		self.rate_refresh = float(kw.get('rate_refresh', 0.5))
		self.last_refresh = 0.0

	def update(self, count):
		""" Update the progress meter. """
		now = time.time()
		if self.inc_mode:
			self.count += count
		else:
			self.count = count
		self.count = min(self.count, self.total)
		value = int(self.count / self.meter_div)
		if value > self.meter_value:
			self.meter_value = value
		if self.last_refresh:
			if (now - self.last_refresh) > self.rate_refresh or \
			   self.count >= self.total:
				self.refresh()
		else:
			self.refresh()

	def refresh(self):
		""" Redraw the progress meter. """
		# print progress meter
		self.stream.write('\r')
		meter_text = self.get_meter()
		self.stream.write(meter_text)	
		# finish
		if self.count >= self.total:
			self.stream.write('\n')
		self.stream.flush()
		# timestamp
		self.last_refresh = time.time()

	def get_meter(self):
		""" Return the asic string describing the progress meter. """
		bar  = self.tick * self.meter_value
		pad  = ' ' * (self.meter_ticks - self.meter_value)
		prec = (float(self.count) / self.total) * 100
		return '[%s>%s] %d%%' % (bar, pad, prec)


if __name__ == "__main__":	
	import time
	import random
	
	total = 100
	p = ProgressMeter(total=total)
	
	while total > 0:
		cnt = random.randint(1, 25)
		p.update(cnt)
		total -= cnt
		time.sleep(random.random())

