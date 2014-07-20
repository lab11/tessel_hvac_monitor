#!/usr/bin/env python

import IPy
import json
import sys
import time
import wemo_insight as wemo
import thread

try:
	import socketIO_client as sioc
except ImportError:
	print('Could not import the socket.io client library.')
	print('sudo pip install socketIO-client')
	sys.exit(1)

import logging
logging.basicConfig()

UPDATE_INTERVAL_SEC = 2
WAIT_TIME_SEC = 10 #the number of seconds to wait for a packet before power cycling

expected_time = None #the time the next packet is expected

switch = wemo.WemoInsight("10.0.0.110")

SOCKETIO_HOST      = 'inductor.eecs.umich.edu'
SOCKETIO_PORT      = 8082
SOCKETIO_NAMESPACE = 'stream'

query = {'profile_id': 'oBNeydOsio'}

def watchdog():
	while(True):
		sys.stdout.write('bark ')
		sys.stdout.flush()
		current_time_sec = time.time()
		if (expected_time != None) and (current_time_sec - expected_time > WAIT_TIME_SEC):
			restart_tessel()
		time.sleep(1)

# restarts tessel by toggling attached wemo
def restart_tessel():
	print("\n\n" + time.strftime("%c") + ": Restarting Tessel.\n\n")
	expected_time = None
	pass
	# turn wemo off
	switch.setOff()
	time.sleep(5)
	# turn wemo on
	switch.setOn()
	time.sleep(30)

class stream_receiver (sioc.BaseNamespace):
	def on_reconnect (self):
		if 'time' in query:
			del query['time']
		stream_namespace.emit('query', query)

	def on_connect (self):
		stream_namespace.emit('query', query)

	def on_data (self, *args):
		global expected_time
		pkt = args[0]
		expected_time = time.time() + (UPDATE_INTERVAL_SEC)
		print(pkt)


socketIO = sioc.SocketIO(SOCKETIO_HOST, SOCKETIO_PORT)
stream_namespace = socketIO.define(stream_receiver,
	'/{}'.format(SOCKETIO_NAMESPACE))

thread.start_new_thread(watchdog, ())

socketIO.wait()
