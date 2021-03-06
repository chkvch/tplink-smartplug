#!/usr/bin/python
import collector
import time
import pickle
import os

targets = '192.168.1.113','192.168.1.112'

for target in targets:
    try:
        sp = collector.smartplug(target)
        energy_ = sp.do('energy') # str
        #info_ = sp.do('info') # str
    except ValueError, e:
        collector.logerr(str(e))
        continue

    current = energy_.split('current')[1].split('voltage')[0][2:-2]
    voltage = energy_.split('voltage')[1].split('power')[0][2:-2]
    power = energy_.split('power')[1].split('total')[0][2:-2]
    total = energy_.split('total')[1].split('err_code')[0][2:-2]
    err_code = int(energy_.split('err_code')[1].split('}}}')[0][2:])

    data = {}
    data = {
        'current':current,
        'voltage':voltage,
        'power':power,
        'total':total,
        'err_code':err_code
        }

    stamp = int(time.time())

    outfile = '{}/smartplug_{}.pkl'.format(os.environ['HOME'], sp.ip)
    if os.path.exists(outfile): # load existing database
        with open(outfile, 'rb') as f:
            database = pickle.load(f)
        database[stamp] = data # fill new entry with current time as key
    else:
        database = {stamp:data} # sole entry

    with open(outfile, 'wb') as f:
        # write new database
        pickle.dump(database, f)
