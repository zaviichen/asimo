#! /usr/bin/env python

# -------------------------------------------------------------
# Author:    Chen Zhihui (zaviichen@gmail.com)
# Date:      11/28/2009
# Version:   1.0
# Copyright (c) 2009 by Chen Zhihui. All Rights Reserved.
# -------------------------------------------------------------

""" Simple server framework. """

from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading

class MyServer(ThreadingMixIn, HTTPServer):
	""" Self-defined server class. """
	pass

def main():
	try:
		print "Welcome to the localhost server!"
		print "Serving HTTP on localhost port 8000 ..."
		server_addr = ('',8000)
		server = MyServer(server_addr, CGIHTTPRequestHandler)
		server.serve_forever()
	except KeyboardInterrupt:
		print "Shutting down the server, byebye!"
		server.socket.close()

if __name__ == "__main__":
	main()
