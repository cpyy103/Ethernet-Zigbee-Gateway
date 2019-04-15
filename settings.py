# -*- coding:utf-8 -*-
import os
import sys


WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', prefix + os.getcwd() + r'\data.db')


