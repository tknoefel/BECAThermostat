#!/bin/python

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



class BECAThermostat(object):
    server = "bestbeca.cn"
    port = 25565
    BUF_SIZE_DATA = 8
    BUF_SIZE_OK = 1
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

    def connect(self):
        self.sock = socket.create_connection((BECAThermostat.server, BECAThermostat.port))
        self.sock.sendall(self.hexIDBytes)     # error handling missing

    def disconnect(self):
        self.sock.close()

    def status(self):
        self.sock.sendall(BECAThermostat.STATUS_MSG)          # error_handling
        data = self.sock.recv(BECAThermostat.BUF_SIZE_DATA)   # error_handling
        return data

    def calc_checksum(self, data):
        cs = 0x00
        for i in range(0, len(data)):
            cs += data[i]
        return (cs & 0xFF) ^ 0xA5


k = BECAThermostat(3145)
print(k.info())
k.connect()
stat = k.status()
print(stat)
print(k.calc_checksum(stat[0:-1]))
print(stat[7])
k.disconnect()
