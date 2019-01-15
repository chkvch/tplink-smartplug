#!/usr/bin/python

#%matplotlib inline
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
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

	# various cosmetics to get closer to the weewx plot style; see /etc/weewx/skin.conf
	self.bold_font = font_manager.FontProperties(fname='/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf')
	self.reg_font = font_manager.FontProperties(fname='/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf')
	self.chart_background_color = '#d8d8d8'
	self.chart_gridline_color = '#a0a0a0'
	self.chart_line_colors = '#4282B4', '#B44242', '#42B443', 'purple', 'coral'

    def daily(self):

        # x_label_format = %I:%M %p
        # bottom_label_format = %x %X
        # time_length = 97200    # == 27 hours

        fig, ax = plt.subplots(4, 1, figsize=(16, 12), sharex=True)
        kwargs = {'linestyle':'-', 'lw':2}
        window = 97200

        for i, (ip, log) in enumerate(self.history.items()):
            mask = log['time'][-1] - log['time'] < window
            alias = {'192.168.1.113':'Ground Floor', '192.168.1.112':'Attic'}[ip]
            kwargs['label'] = alias

            info = '{}: daily: {} records from {} to {}'.format(alias, len(log['time'][mask]),
                time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime(log['time'][mask][0])),
                time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime(log['time'][mask][-1]))
                )
            print(info)
            logdbg(info)

            kwargs['color'] = self.chart_line_colors[i]
            ax[0].plot(log['time'][mask], log['current'][mask], **kwargs)
            ax[1].plot(log['time'][mask], log['voltage'][mask], **kwargs)
            ax[2].plot(log['time'][mask], log['power'][mask], **kwargs)
            ax[3].plot(log['time'][mask], log['total'][mask] - log['total'][mask][0], **kwargs) # subtracting off value at beginning of plot
            # ax[3].plot(log['time'][mask], log['integrated_power'][mask], **kwargs)

            x_title = {'192.168.1.113':0.49, '192.168.1.112':0.51}[ip]
            ha = {'192.168.1.113':'right', '192.168.1.112':'left'}[ip]

            ax[0].text(x_title, 1., alias, color=kwargs['color'], transform=ax[0].transAxes,
                va='bottom', fontsize=20, ha=ha, fontproperties=self.bold_font)

        now = time.time()
        start = now - 27 * 3600
        # human-readable time ticks every hour
        ticks = []
        ticklabels = []
        minorticks = []
        first_hour = int(start / 3600.) * 3600.
        last_hour = int(now / 3600.) * 3600.
        for hour in np.arange(first_hour, last_hour + 3600., 3600.)[::3]:
            ticks.append(hour) # unix timestamp on the hour
            ticklabels.append(time.strftime('%I %p', time.localtime(hour)))
        for hour in np.arange(first_hour, last_hour + 3600., 3600.):
            minorticks.append(hour)

	kw = {'fontproperties':self.reg_font, 'fontsize':20}
        ax[-1].xaxis.set_ticklabels(ticklabels, **kw)
        ax[-1].xaxis.set_ticks(ticks)
        ax[-1].xaxis.set_ticks(minorticks, minor=True)
        ax[-1].set_xlim(start, now) # only need apply to one axis because of sharex=True in subplots

        ax[0].set_ylabel(self.labels['current'], **kw)
        ax[1].set_ylabel(self.labels['voltage'], **kw)
        ax[2].set_ylabel(self.labels['power'], **kw)
        ax[3].set_ylabel(self.labels['total'], **kw)
        ax[-1].set_xlabel(time.strftime('%x %I:%M %p', time.localtime(now)), **kw)

	for z in ax:
		for label in z.get_yticklabels():
			label.set_fontproperties(self.reg_font)

        # ax[-1].legend()

        outfile = 'daypower.png'
        plt.savefig(outfile, bbox_inches='tight')

        stamp = int(time.time())
        os.system('sudo cp {} {}/daypower_{}.png'.format(outfile, self.htmldir, stamp))
        update_html(outfile, stamp)

	# os.system('sudo cp {0}/index.html {0}/index.html.tmp'.format(self.htmldir)) # touch index.html so that browser will reload
	# os.system('sudo mv {0}/index.html.tmp {0}/index.html'.format(self.htmldir)) # touch index.html so that browser will reload

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

def update_html(tag, stamp):
    old = '{}/index.html'.format(os.environ['POWER_HTML_ROOT'])
    new = '{}/index.html.tmp'.format(os.environ['HOME'])
    os.system('sudo cp {} {}'.format(old, new))
    with open(new, 'w') as fw:
        with open(old, 'r') as fr:
            for line in fr.readlines():
                if not 'daypower' in line:
                    fw.write('{}\n'.format(line))
                else:
                    contents = line.split()
                    contents[1] = 'src="daypower_{}.png"'.format(stamp)
                    out = ''
                    for element in contents:
                        out += '{} '.format(element)
                    fw.write('{}\n'.format(out))

    os.system('sudo mv {} {}'.format(new, old))

    # purge old versions of this figure
    for item in os.listdir(os.environ['POWER_HTML_ROOT']):
        if 'daypower' in item:
            if item == '{}.png'.format(tag):
                os.system('sudo rm {}/{}'.format(os.environ['POWER_HTML_ROOT'], item))
            else:
                if int(item.split('_')[1].split('.')[0]) < stamp:
                    os.system('sudo rm {}/{}'.format(os.environ['POWER_HTML_ROOT'], item))

if __name__ == '__main__':
    r = reporter()
    r.daily()
