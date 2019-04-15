# -*- coding:utf-8 -*-
import requests

data={
    'name':'aaa',
    'body':'bbb'
}


def post_data(data):
    response=requests.post('http://127.0.0.1:5000/post_pi', data=data)
    print(response.text)


if __name__ == '__main__':
    post_data(data)