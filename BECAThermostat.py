#!/bin/python
"""
PyBECA interface implementation for BECA Thermostat
"""


# >>> x=b'test'
# >>> x=binascii.hexlify(x)
# >>> x
# b'74657374'
# >>> y=str(x,'ascii')
# >>> y
# '74657374'
# >>> x=binascii.unhexlify(x)
# >>> x
# b'test'
# >>> y=str(x,'ascii')
# >>> y
# 'test'


# A0 01 01 01 01 01 00 00


import binascii
import socket
import struct
import logging


_LOGGER = logging.getLogger(__name__)


class SelfCleaningSocket(socket.socket):
    """
    This socket subclass can be used with the "with" statement. It
    will attempt to clean up and close itself on exit.
    """
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        try:
            self.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(IP_ADDRESS) + socket.inet_aton('0.0.0.0'))
        except socket.error:
            pass
        self.close()





class BECARequest(object):
    def __init__(self):
        pass
    def send(self, sock):
        pass

class BECAReadMsg(BECAMsg):
    def __init__(self):
        self = bytearray.fromhex("00")

class BECAThermostat(object):
    """Interacts with a BECA thermostat via public socket API.
        Example usage: t = Tado('me@somewhere.com', 'mypasswd')
                       t.getClimate(1) # Get climate, zone 1.
        """

    _debugCalls = False

    # Instance-wide constant info
    headers = {'Referer': 'https://my.tado.com/'}
    api2url = 'https://my.tado.com/api/v2/homes/'
    mobi2url = 'https://my.tado.com/mobile/1.9/'
    refresh_token = ''
    refresh_at = datetime.datetime.now() + datetime.timedelta(minutes=5)

    # 'Private' methods for use in class
    __server = "bestbeca.cn"
    __PORT = 25565
    __BUF_SIZE_DATA = 8
    __BUF_SIZE_OK = 1
    STATUS_MSG = bytes.fromhex("A001010101010000")

    def __init__(self, beca_id):
        self.id = beca_id
        self.effectID = (self.id + 1) * 65535 + 65535
        self.hexID = '{:x}'.format(self.effectID)
        if len(self.hexID) % 2: self.hexID = '0' + self.hexID
        self.hexIDBytes = bytes.fromhex(self.hexID)
        self.sock = 0

    def info(self):
        return (self.hexID)


    with SelfCleaningSocket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        # set the receive timeout to 1 second
        sock.settimeout(1)
        # make the address reuseable
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.sendto(MESSAGE, (IP_ADDRESS, PORT))

        ip_mreq = struct.pack("=4sl", socket.inet_aton(IP_ADDRESS), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, ip_mreq)
        thermostats = []

        while True:
            try:
                data, thermostat = sock.recvfrom(4096)
                # append IP address only
                thermostats.append(thermostat[0])
            except socket.timeout:
                break

        if len(thermostats) == 0:
            raise IOError('No thermostats were found')
        if len(thermostats) > 1:
            raise IOError("Found %d thermostats and I don't know which to pick." % len(thermostats))
        return thermostats[0]




    def connect(self):
        self.sock = socket.create_connection((BECAThermostat.__server, BECAThermostat.__PORT))
        self.sock.sendall(self.hexIDBytes)     # error handling missing

    def disconnect(self):
        self.sock.close()

    def status(self) -> bytearray:
        self.sock.sendall(BECAThermostat.STATUS_MSG)          # error_handling
        data = self.sock.recv(BECAThermostat.__BUF_SIZE_DATA)  # error_handling
        #data = b'P\x01\x010\xfe()t'
        return data

    def __calc_checksum(self, data):
        cs = 0x00
        for i in range(0, len(data)-1):
            cs += data[i]
        return (cs & 0xFF) ^ 0xA5

    def temperature(self):
        t = -1
        self.connect()
        data = self.status()
        print(self.__calc_checksum(data))
        if data[7] != self.__calc_checksum(data):
            print("checksum error")
        else:
            t = data[5] / 2
        self.disconnect()
        return t



k = BECAThermostat(3145)
print(k.info())
k.connect()
stat = k.status()
print(stat)
#print(k.__calc_checksum(stat[0:-1]))
print(stat[7])
print(k.temperature())
k.disconnect()
