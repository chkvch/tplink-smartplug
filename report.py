#!/usr/bin/python

#%matplotlib inline
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from spcollector import logdbg
from datetime import datetime

class reporter:

    def __init__(self, ip):
        inpath = '{}/smartplug_{}.pkl'.format(os.environ['HOME'], address)
        with open(inpath, 'rb') as f:
            log = pickle.load(f)

        self.history = {}
        for stamp in sorted(list(log)):
            for key in list(log[stamp]):
                if not key in list(self.history):
                    self.history[key] = np.array([])
                self.history[key] = np.append(self.history[key], float(log[stamp][key]))

        self.history['time'] = np.array(sorted(list(log)))

        from scipy.integrate import cumtrapz
        int_p_dt = cumtrapz(self.history['power'], x=self.history['time'], initial=0.) / 3600. / 1e3
        self.history['integrated_power'] = int_p_dt

        self.label = {
            'current':r'Current (A)',
            'voltage':r'Voltage (V)',
            'power':r'Power (W)',
            'total':r'Energy (kWh)',
            'time':r'Time (Unix)'
        }

        assert 'POWER_HTML_ROOT' in list(os.environ), 'must set POWER_HTML_ROOT'
        self.outdir = os.environ['POWER_HTML_ROOT']
        self.ip = ip

    def alltime(self):

        fig, ax = plt.subplots(4, 1, figsize=(15, 10), sharex=True)

        kwargs = {'linestyle':'-', 'lw':1, 'marker':'o', 'markersize':2}
        ax[0].plot(self.history['time'], self.history['current'], **kwargs)
        ax[1].plot(self.history['time'], self.history['voltage'], **kwargs)
        ax[2].plot(self.history['time'], self.history['power'], **kwargs)
        ax[3].plot(self.history['time'], self.history['total'] - self.history['total'][0], **kwargs)
        ax[3].plot(self.history['time'], self.history['integrated_power'], **kwargs)

        ax[0].set_ylabel(self.label['current'])
        ax[1].set_ylabel(self.label['voltage'])
        ax[2].set_ylabel(self.label['power'])
        ax[3].set_ylabel(self.label['total'])
        ax[-1].set_xlabel(self.label['time'])

        # minus 8 converts to PST
        #date = datetime.utcfromtimestamp(int(history['time'][0]) - 8 * 3600).strftime('%Y-%m-%d')
        time0 = datetime.utcfromtimestamp(int(self.history['time'][0]) - 8 * 3600).strftime('%m/%d/%Y %H:%M:%S')
        time1 = datetime.utcfromtimestamp(int(self.history['time'][-1]) - 8 * 3600).strftime('%m/%d/%Y %H:%M:%S')

        try:
            description = {'192.168.1.113':'First floor furnace', '192.168.1.112':'Attic furnace'}[self.ip]
            alias = {'192.168.1.113':'GroundFloor', '192.168.1.112':'Attic'}[self.ip]
        except KeyError:
            description = alias = 'undefined'

        info = '{}: {} records from {} to {}'.format(description, len(self.history['time']), time0, time1)
        print(info)
        logdbg(info)

        ax[0].set_title(info)
        #plt.savefig('history_test.pdf', bbox_inches='tight')
        outfile = 'history_{}.png'.format(alias)
        plt.savefig(outfile, bbox_inches='tight')

        os.system('sudo cp {} {}/history_{}.png'.format(outfile, self.outdir, alias))
        os.system('sudo touch {}/index.html'.format(self.outdir))

    def daily(self):
        pass

    def weekly(self):
        pass

    def monthly(self):
        pass

    def yearly(self):
        pass

if __name__ == '__main__':
    for address in '192.168.1.112', '192.168.1.113':
        r = reporter(address)
        r.alltime()
