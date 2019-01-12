#!/usr/bin/python
import sqlite3
import time
import os

# limit to entries in the last week
window = 7 * 24 * 60 * 60
now = time.time()
start_time = now - window

db = sqlite3.connect('/var/lib/weewx/weewx.sdb')
c = db.cursor()

# for row in c.execute('PRAGMA table_info([archive])'):
#     print(row)
    
outfile = '{}/weewx.sdb.dump.csv'.format(os.environ['HOME'])
with open(outfile, 'w') as f:
    f.write('dateTime,inTemp,outTemp,Humidity\n')
    t = (start_time, now)
    for row in c.execute('SELECT dateTime, inTemp, outTemp, outHumidity FROM archive WHERE dateTime > ? AND dateTime < ?', t):
        f.write('{:n},{:.1f},{:.1f},{:n}\n'.format(*row))
print('wrote {}'.format(outfile))
