# -*- coding:utf-8 -*-
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
import time


XBEE_SERIAL = 'COM5'
XBEE_ADDR = {
    'node0': '0013A2004109C696',
    'node1': '0013A20041756875'
}

BAUD_RATE = 9600


def data_received_callback(message):
    address = message.remote_device.get_64bit_addr()
    data = message.data.decode('utf8')
    print('received from %s: %s'%(address, data))


def xbee_send_message(from_dev, to_addr, message):
    from_dev.send_data(RemoteXBeeDevice(from_dev, XBee64BitAddress.from_hex_string(to_addr)),message)


with open('ser.txt','r') as f:
    a = f.read()

try:
    device = XBeeDevice(XBEE_SERIAL, BAUD_RATE)
    device.open()
    device.add_data_received_callback(data_received_callback)
    if a == '0':
        device.close()
        with open('ser.txt', 'w') as f:
            f.write('1')
    else:
        xbee_send_message(device, XBEE_ADDR['node0'], 'test')
        with open('ser.txt', 'w') as f:
            f.write('0')

except Exception as e:
    print(e)
    print('device fail')








