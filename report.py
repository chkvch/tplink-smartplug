#!/usr/bin/python

#%matplotlib inline
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

with open('{}/smartplug_192.168.1.113.pkl'.format(os.environ['HOME']), 'rb') as f:
    log = pickle.load(f)

#print(list(log)[0])
#print(log[list(log)[0]])

history = {}
for stamp in sorted(list(log)):
    for key in list(log[stamp]):
        if not key in list(history):
            history[key] = np.array([])
        history[key] = np.append(history[key], float(log[stamp][key]))

history['time'] = np.array(sorted(list(log)))

#fig, ax = plt.subplots(4, 1, figsize=(15, 10), sharex=True, gridspec_kw={'hspace':0.1})
fig, ax = plt.subplots(4, 1, figsize=(15, 10), sharex=True)

kwargs = {'linestyle':'-', 'lw':1, 'marker':'o', 'markersize':2}
ax[0].plot(history['time'], history['current'], **kwargs)
ax[1].plot(history['time'], history['voltage'], **kwargs)
ax[2].plot(history['time'], history['power'], **kwargs)
ax[3].plot(history['time'], history['total'] - history['total'][0], **kwargs)
from scipy.integrate import cumtrapz
int_p_dt = cumtrapz(history['power'], x=history['time'], initial=0.) / 3600. / 1e3
ax[3].plot(history['time'], int_p_dt, **kwargs)

ax[0].set_ylabel(r'Current (A)')
ax[1].set_ylabel(r'Voltage (V)')
ax[2].set_ylabel(r'Power (W)')
ax[3].set_ylabel(r'Energy (kWh)')
ax[-1].set_xlabel(r'Time (Unix)')

from datetime import datetime
#date = datetime.utcfromtimestamp(int(history['time'][0]) - 8 * 3600).strftime('%Y-%m-%d')
time0 = datetime.utcfromtimestamp(int(history['time'][0]) - 8 * 3600).strftime('%m/%d/%Y %H:%M:%S')
time1 = datetime.utcfromtimestamp(int(history['time'][-1]) - 8 * 3600).strftime('%m/%d/%Y %H:%M:%S')

print('{} records from {} to {}'.format(len(history['time']), time0, time1))

ax[0].set_title('First floor furnace: {} to {}'.format(time0, time1))
#plt.savefig('history_test.pdf', bbox_inches='tight')
plt.savefig('/home/pi/tplink-smartplug/history_test.png', bbox_inches='tight')

os.system('sudo cp /home/pi/tplink-smartplug/history_test.png /var/www/html/power/history_test.png')
os.system('sudo touch /var/www/html/power/index.html')
