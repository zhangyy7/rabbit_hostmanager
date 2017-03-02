#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""基于rabbitmq的简单ssh server端."""

import pika
import subprocess
from conf import settings


class SSHClient(object):
    """ssh server类，从rabbitmq服务器获取客户端命令、执行、返回结果到指定的queue."""

    def __init__(self):
        """初始化连接到rabbitmq服务器的参数."""
        user_info = pika.PlainCredentials(
            settings.username, settings.passwd)
        conn_params = pika.ConnectionParameters(
            settings.hostname, settings.port, settings.vhost, user_info)
        self.connection = pika.BlockingConnection(conn_params)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=settings.exchange_name,
            exchange_type=settings.exchange_type)
        self._set_consume()

    def _set_consume(self):
        """设置接收消息的参数."""
        self.channel.basic_consume(self._callback, self.queue)

    def _callback(self, channel, method, properties, body):
        """收到消息时的回调方法."""
        command = body
        result = self._exec_cmd(command)
        routing_key = properties.reply_to
        delivery = method.delivery_tag
        self._put_result_to_rabbit(result, routing_key, properties)
        self.channel.basic_ack(delivery_tag=delivery)

    def _exec_cmd(self, cmd):
        """执行命令."""
        return subprocess.getoutput(cmd)

    def _put_result_to_rabbit(self, message, routing_key, properties):
        """将消息发送到rabbitmq."""
        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=message,
            properties=properties
        )
