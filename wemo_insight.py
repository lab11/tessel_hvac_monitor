import logging
#import urllib.parse
#import urllib.request
import socket
import sys
import time
import xml.etree.ElementTree as ET

class WemoInsight ():
    test = """GET /setup.xml
HOST: {ipaddr}:{port}
User-Agent: GATD-HTTP/1.0"""
    hdr = """POST /upnp/control/basicevent1 HTTP/1.1
SOAPACTION: "urn:Belkin:service:basicevent:1#{command}"
Content-Length: {length}
Content-Type: text/xml; charset="utf-8"
HOST: {ipaddr}:{port}
User-Agent: CyberGarage-HTTP/1.0"""
    set_body = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" \
s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
 <s:Body>
  <u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1">
   <BinaryState>{binstate}</BinaryState>
  </u:SetBinaryState>
 </s:Body>
</s:Envelope>
"""
    get_body = """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" \
s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
 <s:Body>
  <u:GetBinaryState xmlns:u="urn:Belkin:service:basicevent:1">
  </u:GetBinaryState>
 </s:Body>
</s:Envelope>
"""

    def __init__ (self, ip_addr, port=49152):
        self.ip_addr = ip_addr
        self.port = port

    # Returns True if the load on, False if the load is off
    def getPowerState (self):
        tag = '<BinaryState>'
        response = self._state_get('GetBinaryState')
        idx = response.index(tag)
        return int(response[idx+len(tag)]) == 1

    def setOn (self):
        self._state_control('SetBinaryState', '1')

    def setOff (self):
        self._state_control('SetBinaryState', '0')

    def _connect (self):
        for i in range(0,2):
            connection_attempts = 2
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while connection_attempts > 0:
                try:
                    sock.connect((self.ip_addr, self.port + i))
                    sock.settimeout(0.1)
                    testreq = self.test.format(ipaddr=self.ip_addr,port=self.port+i)
                    testreq = testreq.replace('\n', '\r\n') + '\r\n\r\n'
                    sock.send(testreq.encode())
                    sock.recv(10000)
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((self.ip_addr, self.port + i))
                    return sock
                except:
                    connection_attempts -= 1
        raise WemoError('Unable to connect to wemo ip addr={}'
                    .format(self.ip_addr))

    def _state_get (self, cmd):
        sock = self._connect()
        soap_bdy = self.get_body
        soap_hdr = self.hdr.format(command=cmd,
            length=len(soap_bdy),
            ipaddr=self.ip_addr,
            port=self.port)
        soap_hdr = soap_hdr.replace('\n', '\r\n')
        soap = soap_hdr + '\r\n\r\n' + soap_bdy
        sock.send(soap.encode())
        response = ''
        while True:
            data = sock.recv(1024)
            response += data.decode()
            if '</s:Envelope>' in response:
                break
        sock.close()
        return response

    def _state_control (self, cmd, state):
        sock = self._connect()
        soap_bdy = self.set_body.format(binstate=state)
        soap_hdr = self.hdr.format(command=cmd,
            length=len(soap_bdy),
            ipaddr=self.ip_addr,
            port=self.port)
        soap_hdr = soap_hdr.replace('\n', '\r\n')
        soap = soap_hdr + '\r\n\r\n' + soap_bdy
        sock.send(soap.encode())
        sock.close()