#!/usr/bin/python

#%matplotlib inline
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from spcollector import logdbg
import time

class reporter:

    def __init__(self, ips=('192.168.1.113', '192.168.1.112')):
        self.history = {}
        for ip in ips:
            inpath = '{}/smartplug_{}.pkl'.format(os.environ['HOME'], ip)
            with open(inpath, 'rb') as f:
                log = pickle.load(f)

            self.history[ip] = {}
            self.history[ip]['time'] = np.array(sorted(list(log)))
            for stamp in sorted(list(log)):
                for key in list(log[stamp]):
                    if not key in list(self.history[ip]):
                        self.history[ip][key] = np.array([])
                    self.history[ip][key] = np.append(self.history[ip][key], float(log[stamp][key]))

            from scipy.integrate import cumtrapz
            int_p_dt = cumtrapz(self.history[ip]['power'], x=self.history[ip]['time'], initial=0.) / 3600. / 1e3
            self.history[ip]['integrated_power'] = int_p_dt

        self.labels = {
            'current':r'Current (A)',
            'voltage':r'Voltage (V)',
            'power':r'Power (W)',
            'total':r'Energy (kWh)'
        }

        assert 'POWER_HTML_ROOT' in list(os.environ), 'must set POWER_HTML_ROOT'
        self.htmldir = os.environ['POWER_HTML_ROOT']
        self.ip = ip

    def daily(self):

        # x_label_format = %I:%M %p
        # bottom_label_format = %x %X
        # time_length = 97200    # == 27 hours

        fig, ax = plt.subplots(4, 1, figsize=(15, 10), sharex=True)
        kwargs = {'linestyle':'-', 'lw':1, 'marker':'o', 'markersize':2}
        window = 97200

        for ip, log in self.history.items():
            mask = log['time'][-1] - log['time'] < window
            alias = {'192.168.1.113':'Ground Floor', '192.168.1.112':'Attic'}[ip]
            kwargs['label'] = alias

            info = '{}: daily: {} records from {} to {}'.format(alias, len(log['time'][mask]),
                time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime(log['time'][mask][0])),
                time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime(log['time'][mask][-1]))
                )
            print(info)
            logdbg(info)

            ax[0].plot(log['time'][mask], log['current'][mask], **kwargs)
            ax[1].plot(log['time'][mask], log['voltage'][mask], **kwargs)
            ax[2].plot(log['time'][mask], log['power'][mask], **kwargs)
            c, = ax[3].plot(log['time'][mask], log['total'][mask] - log['total'][0], **kwargs)
            # ax[3].plot(log['time'][mask], log['integrated_power'][mask], **kwargs)

            x_title = {'192.168.1.113':0.49, '192.168.1.112':0.51}[ip]
            ha = {'192.168.1.113':'right', '192.168.1.112':'left'}[ip]

            fig.text(x_title, 0.9, alias, color=c.get_color(), transform=fig.transFigure,
                va='bottom', fontsize=24, ha=ha)

        now = time.time()
        start = now - 27 * 3600
        # human-readable time ticks every hour
        ticks = []
        ticklabels = []
        first_hour = int(start / 3600.) * 3600.
        last_hour = int(now / 3600.) * 3600.
        for hour in np.arange(first_hour, last_hour, 3600.)[::3]:
            ticks.append(hour) # unix timestamp on the hour
            ticklabels.append(time.strftime('%I %p', time.localtime(hour)))

        ax[-1].xaxis.set_ticklabels(ticklabels)
        ax[-1].xaxis.set_ticks(ticks)
        ax[-1].set_xlim(start, now) # only need apply to one axis because of sharex=True in subplots

        ax[0].set_ylabel(self.labels['current'])
        ax[1].set_ylabel(self.labels['voltage'])
        ax[2].set_ylabel(self.labels['power'])
        ax[3].set_ylabel(self.labels['total'])
        ax[-1].set_xlabel(time.strftime('%I:%M %p', time.localtime(now)))

        # ax[-1].legend()

        outfile = 'daily.png'
        plt.savefig(outfile, bbox_inches='tight')

        os.system('sudo cp {} {}/daily.png'.format(outfile, self.htmldir))
        os.system('sudo touch {}/index.html'.format(self.htmldir))

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
    r = reporter()
    r.daily()
