#!/usr/bin/python
import pickle
import os
import time
stamp = int(time.time())

with open('{}/smartplug_192.168.1.113.pkl'.format(os.environ['HOME']), 'rb') as f:
	log = pickle.load(f)
with open('{}/smartplug_192.168.1.113.pkl.backup.{}'.format(os.environ['HOME'], stamp), 'wb') as f:
	pickle.dump(log, f)

# forgot we want to do this for weewx, not the power database.
#start = 1547506800 # 11pm localtime 01/14/2019
#end = start + 12 * 60 * 60 # 12 hours later
#for key in list(log):
#	if int(key) < 1500000000:
#		log.pop(key, None)
#	elif int(key) > start and int(key < end):
#		log.pop(key, None)

with open('{}/smartplug_192.168.1.113.pkl'.format(os.environ['HOME']), 'wb') as f:
	pickle.dump(log, f)
