# -*- coding:utf-8 -*-
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from digi.xbee.models.status import NetworkDiscoveryStatus
import time

# xbee模块串口
XBEE_PORT = 'COM3'
# xbee 波特率
BAUD_RATE = 9600

RECEIVED_DATA = []
XBEE_ADDR = {}


def my_map(addr):
    for key, value in XBEE_ADDR.items():
        if value == addr:
            return key
    return None


def data_received_callback(message):
    node = my_map(str(message.remote_device.get_64bit_addr()))
    data = message.data.decode('utf8')
    t = time.localtime()

    t1 = time.strftime('%Y_%m_%d', t)
    t2 = time.strftime('%H:%M:%S', t)

    RECEIVED_DATA.append((node, data, t2))

    with open('Received_' + t1 + '.txt', 'a') as file:
        file.write('Received from  %s : %s  at %s\n' % (node, data, t2))


def xbee_send_message(from_dev, to_addr, message):
    from_dev.send_data(RemoteXBeeDevice(from_dev, XBee64BitAddress.from_hex_string(to_addr)), message)


# 查找设备
def discover_devices(device):
    print('MyNode(MAC_ADDR): ' + str(device.get_64bit_addr()))
    XBEE_ADDR['node0'] = str(device.get_64bit_addr())
    net = device.get_network()

    def device_discovered_callback(remote):
        mac = str(remote)[:16]
        print('Device discovered: %s ' % mac)
        if mac not in XBEE_ADDR.values():
            for i in range(1, 100):
                if 'node'+str(i) not in XBEE_ADDR.keys():
                    XBEE_ADDR['node'+str(i)] = mac
                    break

    def device_discovery_finished_callback(status):
        if status == NetworkDiscoveryStatus.SUCCESS:
            print('Device discovery process finished successfully')
        else:
            print('There was an error discovering devices: %s' % status.description)

    net.add_device_discovered_callback(device_discovered_callback)
    net.add_discovery_process_finished_callback(device_discovery_finished_callback)

    net.start_discovery_process()
    print('Discovering remote XBee devices...')

    while net.is_discovery_running():
        time.sleep(0.1)

    # print(net.get_devices())


with open('ser.txt','r') as f:
    a = f.read()

try:
    device = XBeeDevice(XBEE_PORT, BAUD_RATE)
    device.open()
    device.add_data_received_callback(data_received_callback)
    if a == '0':
        device.close()
        with open('ser.txt', 'w') as f:
            f.write('1')
    else:
        discover_devices(device)    # 组网发现设备

        with open('ser.txt', 'w') as f:
            f.write('0')

except Exception as e:
    print(e)
    print('device fail')








