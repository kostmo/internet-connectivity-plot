#!/usr/bin/env python

'''
Plots transitions in internet connectivity within a specified time range.

Does a linear scan of a text file containing lines of timestamped 'ping'
output (see ./connectivity_tester_loop.sh).

The plot itself is drawn efficiently for a small filesize. However, the scan
of the data leading up to the plottable range is linear and inefficient.
May be more efficient with a database.
'''

import os
import datetime

import matplotlib
matplotlib.use('Agg')

from pylab import figure
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter, FixedLocator

def make_chart(input_filepath, output_file_specifier, DAYS_AGO_TO_START_PLOT, DAYS_AGO_TO_END_PLOT):

	time_now = datetime.datetime.now()

	time_to_end_plotting = time_now - datetime.timedelta(days=DAYS_AGO_TO_END_PLOT)

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
	first_available_timestamp = None
	lapse_count = 0	# XXX DEBUG
	
	for line in open(input_filepath):
		splitted = line.split()

		date = splitted[0]
		time_24hr = splitted[1]
		
		decimal_point_location = time_24hr.rfind(".")
		time_24hr_integral_seconds = time_24hr
		if decimal_point_location >= 0:
			time_24hr_integral_seconds = time_24hr[:decimal_point_location - 1]
		ping_return_code = int(splitted[2])


		fulltime = datetime.datetime.strptime(date + "-" + time_24hr_integral_seconds, "%Y-%m-%d-%H:%M:%S")
		if not first_available_timestamp:
			first_available_timestamp = fulltime
			
		if DAYS_AGO_TO_START_PLOT is not None:
			time_to_start_plotting = time_now - datetime.timedelta(days=DAYS_AGO_TO_START_PLOT)
			if fulltime < time_to_start_plotting:
				continue

		if fulltime > time_to_end_plotting:
			break

		is_connected = not bool(ping_return_code)


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

	# Draw the final data point
	xvals.append(last_timestamp)
	yvals.append(int(previous_is_connected))

	total_time_seconds = (last_timestamp - first_used_timestamp).total_seconds()
	total_off_time_seconds = total_off_time.total_seconds()
	print "total considered time range: %.1f minutes" % (total_time_seconds/60)
	print "total lapse time within considered time range: %.1f minutes" % (total_off_time_seconds/60)
	print "Percentage of internet connectivity lapse: %.1f%%" % (100*(total_off_time_seconds/total_time_seconds))
	print "Connectivity lapse count:", lapse_count
	print "First available timestamp is", (time_now - first_available_timestamp).days, "days ago."

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
