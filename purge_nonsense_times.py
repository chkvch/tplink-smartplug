#!/usr/bin/python
import pickle
import os
with open('{}/smartplug_192.168.1.113.pkl'.format(os.environ['HOME']), 'rb') as f:
	log = pickle.load(f)
with open('{}/smartplug_192.168.1.113.pkl.backup'.format(os.environ['HOME']), 'wb') as f:
	pickle.dump(log, f)
for key in list(log):
	if int(key) < 1500000000:
		log.pop(key, None)
with open('{}/smartplug_192.168.1.113.pkl'.format(os.environ['HOME']), 'wb') as f:
	pickle.dump(log, f)
