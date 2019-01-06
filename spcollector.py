import socket
import argparse
from struct import pack
import threading
import syslog

def logmsg(level, msg):
    syslog.syslog(level, 'spcollector: {}: {}'.format(threading.currentThread().getName(), msg))

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

def validHostname(hostname):
	try:
		socket.gethostbyname(hostname)
	except socket.error:
		logerr("Invalid hostname {}.".format(hostname))
	return hostname

# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
def encrypt(string):
	key = 171
	result = pack('>I', len(string))
	for i in string:
		a = key ^ ord(i)
		key = a
		result += chr(a)
	return result

def decrypt(string):
	key = 171
	result = ""
	for i in string:
		a = key ^ ord(i)
		key = ord(i)
		result += chr(a)
	return result

class smartplug:

	def __init__(self, target):
		assert validHostname(target), 'asdf'
		self.ip = target

		# Predefined Smart Plug Commands
		# For a full list of commands, consult tplink-smarthome-commands.txt
		self.commands = {
					'info'     : '{"system":{"get_sysinfo":{}}}',
					'on'       : '{"system":{"set_relay_state":{"state":1}}}',
					'off'      : '{"system":{"set_relay_state":{"state":0}}}',
					'cloudinfo': '{"cnCloud":{"get_info":{}}}',
					'wlanscan' : '{"netif":{"get_scaninfo":{"refresh":0}}}',
					'time'     : '{"time":{"get_time":{}}}',
					'schedule' : '{"schedule":{"get_rules":{}}}',
					'countdown': '{"count_down":{"get_rules":{}}}',
					'antitheft': '{"anti_theft":{"get_rules":{}}}',
					'reboot'   : '{"system":{"reboot":{"delay":1}}}',
					'reset'    : '{"system":{"reset":{"delay":1}}}',
					'energy'   : '{"emeter":{"get_realtime":{}}}'
		}


	def do(self, command, port=9999):
		if command in list(self.commands):
			command = self.commands[command]
		# otherwise pass command as json

		# Send command and receive reply
		try:
			sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock_tcp.connect((self.ip, port))
			sock_tcp.send(encrypt(command))
			data = sock_tcp.recv(2048)
			sock_tcp.close()

			result = decrypt(data[4:])

			logdbg("Sent:     {}".format(command))
			logdbg("Received: {}".format(result))

			return result
		except socket.error:
			logerr("Could not connect to host " + ip + ":" + str(port))
