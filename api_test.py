# -*- coding:utf-8 -*-
import requests
import time


IP = 'http://127.0.0.1:5000'


def api_login_test(name, pwd):
    print(requests.get(IP+'/api/login?username=%s&password=%s'%(name, pwd)).text)


def api_logout_test():
    print(requests.get(IP+'/api/logout').text)


def api_index_test(name, body):
    print(requests.get(IP+'/api/index?name=%s&body=%s'%(name, body)).text)


def api_devices_test():
    print(requests.get(IP+'/api/devices').text)


def api_delete_test(node):
    print(requests.get(IP+'/api/delete?node=%s'%node).text)


def api_discover_test():
    print(requests.get(IP+'/api/discover').text)


def api_discover_init_test():
    print(requests.get(IP+'/api/discover_init').text)


def api_my_data_test():
    print(requests.get(IP+'/api/my_data').text)


def api_received_data_test():
    print(requests.get(IP+'/api/received_data').text)


def api_send_data_test():
    print(requests.get(IP+'/api/send_data').text)


if __name__ == '__main__':
    api_login_test('admin', '666666')
    time.sleep(1)
    api_devices_test()
    time.sleep(1)
    api_delete_test('node1')
    time.sleep(1)
    api_discover_init_test()
    time.sleep(1)
    api_index_test('node1','hello world')
    time.sleep(1)
    for i in range(5):
        api_my_data_test()
        time.sleep(1)

    api_received_data_test()
    api_send_data_test()
    api_logout_test()
    time.sleep(1)

