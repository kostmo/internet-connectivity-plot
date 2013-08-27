#!/usr/bin/env python

'''
Webserver frontend for 'plot_transitions.py'

Also requires the file 'index.html'.
'''

from urlparse import urlparse, parse_qs
from cStringIO import StringIO

#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi

from plot_transitions import make_chart

PORT_NUMBER = 80

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):

		try:

			parsed_url = urlparse(self.path)
			url_path = parsed_url.path

			if url_path.endswith(".pdf"):
				
				query_dict = parse_qs(parsed_url.query)
				
				mimetype='application/pdf'
				#Open the static file requested and send it
				
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()

				sio = StringIO()
				make_chart(sio, int(query_dict.get("from")[0]), int(query_dict.get("to")[0]))

				self.wfile.write(sio.getvalue())
				sio.close()
				
			else:
				mimetype='text/html'
				#Open the static file requested and send it
				
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				
				self.wfile.write(open("index.html").read())
				
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
			

if __name__ == "__main__":
	try:
		#Create a web server and define the handler to manage the
		#incoming request
		server = HTTPServer(('', PORT_NUMBER), myHandler)
		print 'Started httpserver on port ' , PORT_NUMBER
		
		#Wait forever for incoming htto requests
		server.serve_forever()

	except KeyboardInterrupt:
		print '^C received, shutting down the web server'
		server.socket.close()