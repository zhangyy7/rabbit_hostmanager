#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""基于rabbitmq的简单ssh的通用参数."""

# rabbitmq服务器地址
hostname = '192.168.146.135'
port = 5672
username = 'guest'
passwd = 'guest'
vhost = '/'
exchange_name = 'batch_cmd'
exchange_type = 'topic'
