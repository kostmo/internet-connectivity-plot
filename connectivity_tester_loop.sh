#!/usr/bin/env python

from datetime import datetime
from time import sleep
import os

TIMEOUT_SECONDS = 3

log_fh = open("connectivity.log", "a")
while True:
	return_code = os.system("ping -w %d -c 1 google.com" % (TIMEOUT_SECONDS))
	
	log_fh.write( str(datetime.now()) + "\t" + str(return_code) + "\n")
	log_fh.flush()
	if not return_code:
		sleep(TIMEOUT_SECONDS)

log_fh.close()
