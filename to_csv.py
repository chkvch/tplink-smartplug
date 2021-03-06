#!/usr/bin/python

import pickle
import os
for ip in ('192.168.1.112', '192.168.1.113'):

    with open('{}/smartplug_{}.pkl'.format(os.environ['HOME'], ip), 'rb') as f:
        log = pickle.load(f)

    outfile = '{}/smartplug_{}.csv'.format(os.environ['HOME'], ip)
    with open(outfile, 'wb') as f:

        f.write('unixtime,current,voltage,power,total\n')
        for stamp in sorted(list(log)):
            data = log[stamp]
            line = '{},{},{},{},{}\n'.format(stamp, data['current'], data['voltage'], data['power'], data['total'])
            f.write(line)
	print('wrote {}'.format(outfile))
