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

    def day(self):

        # x_label_format = %I:%M %p
        # bottom_label_format = %x %X
        # time_length = 97200    # == 27 hours

        fig, ax = plt.subplots(4, 1, figsize=(15, 10), sharex=True)

        window = 97200
        mask = self.history['time'][-1] - self.history['time'] < window

        kwargs = {'linestyle':'-', 'lw':1, 'marker':'o', 'markersize':2}
        ax[0].plot(self.history['time'][mask, self.history['current'][mask], **kwargs)
        ax[1].plot(self.history['time'][mask, self.history['voltage'][mask], **kwargs)
        ax[2].plot(self.history['time'][mask, self.history['power'][mask], **kwargs)
        ax[3].plot(self.history['time'][mask, self.history['total'][mask] - self.history['total'][0], **kwargs)
        ax[3].plot(self.history['time'][mask, self.history['integrated_power'][mask], **kwargs)

        ax[0].set_ylabel(self.label['current'])
        ax[1].set_ylabel(self.label['voltage'])
        ax[2].set_ylabel(self.label['power'])
        ax[3].set_ylabel(self.label['total'])
        ax[-1].set_xlabel(self.label['time'])

        # # minus 8 converts to PST
        # time0 = datetime.utcfromtimestamp(int(self.history['time'][0]) - 8 * 3600).strftime('%m/%d/%Y %H:%M:%S')
        # time1 = datetime.utcfromtimestamp(int(self.history['time'][-1]) - 8 * 3600).strftime('%m/%d/%Y %H:%M:%S')
        #
        # try:
        #     description = {'192.168.1.113':'First floor furnace', '192.168.1.112':'Attic furnace'}[self.ip]
        #     alias = {'192.168.1.113':'GroundFloor', '192.168.1.112':'Attic'}[self.ip]
        # except KeyError:
        #     description = alias = 'undefined'
        #
        # info = '{}: {} records from {} to {}'.format(description, len(self.history['time']), time0, time1)
        # print(info)
        # logdbg(info)
        #
        # ax[0].set_title(info)

        outfile = 'daily_{}.png'.format(alias)
        plt.savefig(outfile, bbox_inches='tight')

        os.system('sudo cp {} {}/daily_{}.png'.format(outfile, self.outdir, alias))
        os.system('sudo touch {}/index.html'.format(self.outdir))

    def weekly(self):
        # x_label_format = %a %b %d
        # bottom_label_format = %x %X
        # time_length = 604800    # == 7 days
        # aggregate_type = avg
        # aggregate_interval = 3600
        pass

    def monthly(self):
        # x_label_format = %d
        # bottom_label_format = %x %X
        # time_length = 2592000    # == 30 days
        # aggregate_type = avg
        # aggregate_interval = 10800    # == 3 hours
        # show_daynight = false
        pass

    def yearly(self):
        # x_label_format = %b
        # bottom_label_format = %x %X
        # time_length = 31536000    # == 365 days
        # aggregate_type = avg
        # aggregate_interval = 86400
        # show_daynight = false
        pass

if __name__ == '__main__':
    for address in '192.168.1.112', '192.168.1.113':
        r = reporter(address)
        r.alltime()
