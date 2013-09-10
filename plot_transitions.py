#!/usr/bin/env python

'''
Plots transitions in internet connectivity within a specified time range.

Does a linear scan of a text file containing lines of timestamped 'ping'
output (see ./connectivity_tester_loop.sh).

The plot itself is drawn efficiently for a small filesize. However, the scan
of the data leading up to the plottable range is linear and inefficient.
May be more efficient with a database.
'''

import psycopg2
import os
import datetime

import matplotlib
matplotlib.use('Agg')

from pylab import figure
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter, FixedLocator

def get_timeseries(time_to_start_plotting, time_to_end_plotting):

	conn = psycopg2.connect("dbname=netlog user=kostmo password=hunter2")
	cur = conn.cursor()

	time_now = datetime.datetime.now()

	where_clauses = []
	where_args = []

	if time_to_start_plotting is not None:
		where_clauses.append("timestamp >= %s")
		where_args.append(time_to_start_plotting)	
	
	if time_to_end_plotting is not None:
		where_clauses.append("timestamp <= %s")
		where_args.append(time_to_end_plotting)
	
	where_clause_string = ""
	if where_clauses:
		where_clause_string = " WHERE " + " AND ".join(where_clauses)

	# first element - dateestamp
	# second element - duration
	# third element - connectivity
	runlength_tuples = []
	previous_connectivity = False
	last_transition_date = None


	temp_tuples = []
	xvals = []
	yvals = []
	previous_is_connected = True
	last_connection_loss_timestamp = None
	
	total_off_time = datetime.timedelta(seconds=0)
	last_timestamp = None
	first_used_timestamp = None
	lapse_count = 0	# XXX DEBUG
	
	cur.execute( ("SELECT * FROM connectivity" + where_clause_string + ";"), tuple(where_args))
	
	for row in cur.fetchall():

		fulltime = row[0]
		is_connected = row[1]

		if not first_used_timestamp:
			first_used_timestamp = fulltime
			last_timestamp = fulltime
			last_connection_loss_timestamp = fulltime
		else:
			if previous_is_connected and not is_connected:
				last_connection_loss_timestamp = fulltime
			elif is_connected and not previous_is_connected:
				# We are becomming reconnected after a lapse in connectivity
				total_off_time += (fulltime - last_connection_loss_timestamp)
				lapse_count += 1

		# We only need to draw a point if the state changes
		if previous_is_connected != is_connected:
			
			# We actually need to draw two points to form a vertical edge.
			# The .step() graph will do this automatically with just one
			# point, but it doesn't support "filling" the region below the line.
			xvals.append(fulltime)
			yvals.append(int(previous_is_connected))

			xvals.append(fulltime)
			yvals.append(int(is_connected))
		
		previous_is_connected = is_connected
		last_timestamp = fulltime
		

	cur.close()
	conn.close()

	# Draw the final data point
	xvals.append(last_timestamp)
	yvals.append(int(previous_is_connected))

	total_time_seconds = (last_timestamp - first_used_timestamp).total_seconds()
	total_off_time_seconds = total_off_time.total_seconds()
	print "total considered time range: %.1f minutes" % (total_time_seconds/60)
	print "total lapse time within considered time range: %.1f minutes" % (total_off_time_seconds/60)
	print "Percentage of internet connectivity lapse: %.1f%%" % (100*(total_off_time_seconds/total_time_seconds))
	print "Connectivity lapse count:", lapse_count

	return xvals, yvals

def make_chart(output_file_specifier, days_ago_to_start_plot, days_ago_to_end_plot):

	time_to_start_plotting = None
	if days_ago_to_start_plot is not None:
		time_to_start_plotting = time_now - datetime.timedelta(days=days_ago_to_start_plot)
		
	time_to_end_plotting = None
	if days_ago_to_end_plot is not None:
		time_to_end_plotting = time_now - datetime.timedelta(days=days_ago_to_end_plot)


	xvals, yvals = get_timeseries(time_to_start_plotting, time_to_end_plotting)
	chart_title = 'Internet Connectivity since ' + first_used_timestamp.strftime("%A, %B %d")
	
	fig = render_figure(chart_title, xvals, yvals)

	pp = PdfPages(output_file_specifier)
	pp.savefig(fig)
	pp.close()


def render_figure(chart_title, xvals, yvals):
	
	print "Now rendering figure..."
	
	fig = figure()
	ax1 = fig.add_subplot(111)

#	ax1.step(xvals, yvals, linewidth=2.0, marker=".", linestyle="-")
	ax1.fill_between(xvals, 0, yvals, linewidth=0, facecolor='blue', alpha=0.3)

	def mjrFormatter(x, pos):
		if x == 1:
			return "On"
		elif x == 0:
			return "Off"
		else:
			return ""

	ax1.grid(False)
	ax1.set_xlabel('Time')
	ax1.set_ylabel('Connection Status')
	ax1.set_ylim([0,1.5])
	ax1.set_title(chart_title)
	ax1.xaxis.set_major_formatter(DateFormatter('%a %b %d, %I:%M %P'))
	ax1.yaxis.set_major_formatter(FuncFormatter(mjrFormatter))
	ax1.yaxis.set_major_locator(FixedLocator([0, 1]))
	fig.autofmt_xdate()
	ax1.autoscale_view()
	return fig

if __name__ == "__main__":
	input_filepath = "sample-data/connectivity.log"
	output_filename = "simple_connectivity_plot" + ".pdf"
	make_chart(input_filepath, output_filename, None, 0)
	os.system("evince %s" % output_filename)
