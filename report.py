#!/usr/bin/python

#%matplotlib inline
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from spcollector import logdbg

for address in '192.168.1.112', '192.168.1.113':

    try:
        inpath = '{}/smartplug_{}.pkl'.format(os.environ['HOME'], address)
        with open(inpath, 'rb') as f:
            log = pickle.load(f)
    except Exception, e:
        logdbg('failed to load database {}: {}'.format(inpath, e))
        continue

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
    # minus 8 converts to PST
    #date = datetime.utcfromtimestamp(int(history['time'][0]) - 8 * 3600).strftime('%Y-%m-%d')
    time0 = datetime.utcfromtimestamp(int(history['time'][0]) - 8 * 3600).strftime('%m/%d/%Y %H:%M:%S')
    time1 = datetime.utcfromtimestamp(int(history['time'][-1]) - 8 * 3600).strftime('%m/%d/%Y %H:%M:%S')

    description = {'192.168.1.113':'First floor furnace', '192.168.1.112':'Attic furnace'}[address]
    alias = {'192.168.1.113':'GroundFloor', '192.168.1.112':'Attic'}[address]

    info = '{}: {} records from {} to {}'.format(description, len(history['time']), time0, time1)
    print(info)
    logdbg(info)
    ax[0].set_title(info)
    #plt.savefig('history_test.pdf', bbox_inches='tight')
    outfile = '/home/pi/tplink-smartplug/history_{}.png'.format(alias)
    plt.savefig(outfile, bbox_inches='tight')

    os.system('sudo cp {} /var/www/html/power/history_{}.png'.format(outfile, alias))

os.system('sudo touch /var/www/html/power/index.html')
