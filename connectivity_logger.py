#!/usr/bin/env python

from datetime import datetime
from time import sleep
import os
import psycopg2

TIMEOUT_SECONDS = 30
PING_HOSTNAME = "google.com"

if __name__ == "__main__":
	conn = psycopg2.connect("dbname=netlog user=%s" % (os.environ.get("USER")))
	while True:
		return_code = os.system("ping -w %d -c 1 %s" % (TIMEOUT_SECONDS, PING_HOSTNAME))
	
		cur = conn.cursor()
		cur.execute("INSERT INTO connectivity (connected) VALUES (%s)", (not bool(return_code),))
		conn.commit()

		if not return_code:
			sleep(TIMEOUT_SECONDS)

cur.close()
conn.close()