#!/usr/bin/env python

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
#logging.basicConfig()
logging.basicConfig(level=logging.DEBUG)

# Watchdog configuration
UPDATE_INTERVAL_SEC = 2 #update interval of Tessel
WAIT_TIME_SEC = 8 #the number of seconds to wait for a packet before power cycling
expected_time = None #the time the next packet is expected

# Wemo/Tessel power supply configuration
switch = wemo.WemoInsight("10.0.0.110")

# GATD connection parameters
SOCKETIO_HOST      = 'inductor.eecs.umich.edu'
SOCKETIO_PORT      = 8082
SOCKETIO_NAMESPACE = 'stream'
socketIO = None
stream_namespace = None
query = {'profile_id': 'oBNeydOsio'}

def watchdog():
	while(True):
		sys.stdout.write('bark ')
		sys.stdout.flush()
		current_time_sec = time.time()
		# initialize system with reboot of Tessel and GATD connection
		if (expected_time == None):
			restart_system()
		# if you haven't heard from the GATD stream in a while, reboot Tessel and connection
		elif (current_time_sec - expected_time > WAIT_TIME_SEC):
			restart_system()
		time.sleep(1)

# restarts whole system, deals with timing
def restart_system():
	global socketIO
	if socketIO != None:
		socketIO.disconnect()
	restart_tessel()
	time.sleep(3)
	thread.start_new_thread(connect_to_gatd, ())
	time.sleep(10)

# restarts tessel by toggling attached wemo
def restart_tessel():
	print("\n\n" + time.strftime("%c") + ": Restarting Tessel.\n\n")
	expected_time = None
	# turn wemo off
	switch.setOff()
	time.sleep(1)
	# turn wemo on
	switch.setOn()

class stream_receiver (sioc.BaseNamespace):
	def on_reconnect (self):
		if 'time' in query:
			del query['time']
		stream_namespace.emit('query', query)

	def on_connect (self):
		global stream_namespace
		stream_namespace.emit('query', query)

	def on_data (self, *args):
		global expected_time
		pkt = args[0]
		expected_time = time.time() + (UPDATE_INTERVAL_SEC)
		print(pkt)

def connect_to_gatd():
	global socketIO, stream_namespace
	socketIO = sioc.SocketIO(SOCKETIO_HOST, SOCKETIO_PORT)
	stream_namespace = socketIO.define(stream_receiver,
		'/{}'.format(SOCKETIO_NAMESPACE))
	socketIO.wait()

if __name__=="__main__":
	watchdog()




