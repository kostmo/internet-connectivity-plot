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
import json

from plot_transitions import make_chart, get_timeseries

PORT_NUMBER = 8080

from time import mktime
from datetime import datetime

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return int(mktime(obj.timetuple()))*1000

        return json.JSONEncoder.default(self, obj)

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
				
			elif url_path.endswith(".json"):
				query_dict = parse_qs(parsed_url.query)
				
				mimetype='text/json'
				#Open the static file requested and send it
				
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				
				start_date_string = query_dict.get("start")[0]
				end_date_string = query_dict.get("end")[0]

				start_date = datetime.strptime(start_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
				end_date = datetime.strptime(end_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')

				data_dict = {"timeseries": zip(*get_timeseries(
					start_date,
					end_date
				))}

				output_json_string = json.dumps(data_dict, cls = MyEncoder)
				self.wfile.write(output_json_string)
				
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