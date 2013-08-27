Internet connectivity plotter
==========================

Monitors and plots internet connectivity

Overview
-------------
We've been having a lot of problems with our ISP lately, and wanted to generate
some data regarding connectivity to help diagnose the problem and/or potentiallly
build the case for a partial refund on our monthly bill.

The `./connectivity_tester_loop.sh` script will `ping` Google every 3 seconds,
writing the timestamped return code to a file.

The `./plot_transitions.py` script will generate a PDF of the connection
status over a specified range of days, using the above file as input.

The `./chart_server.py` script is a webserver that will dynamically render
the above PDF over HTTP.

Prerequisites
-------------
Ubuntu packages:
* python-matplotlib