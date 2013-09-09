#!/usr/bin/env python

from datetime import datetime
from time import sleep
import os
import psycopg2

TIMEOUT_SECONDS = 3

if __name__ == "__main__":
	conn = psycopg2.connect("dbname=netlog user=kostmo")
	while True:
		return_code = os.system("ping -w %d -c 1 google.com" % (TIMEOUT_SECONDS))
	
		cur = conn.cursor()
		cur.execute("INSERT INTO connectivity (connected) VALUES (%s)", (not bool(return_code),))
		conn.commit()

		if not return_code:
			sleep(TIMEOUT_SECONDS)

cur.close()
conn.close()