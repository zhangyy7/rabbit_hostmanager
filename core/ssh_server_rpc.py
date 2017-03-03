#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""基于rabbitmq的简单ssh server端."""

import pika
import subprocess
import psutil
from conf import settings


class SSHServer(object):
    """ssh server类，从rabbitmq服务器获取客户端命令、执行、返回结果到指定的queue."""

    def __init__(self):
        """初始化连接到rabbitmq服务器的参数."""
        user_info = pika.PlainCredentials(
            settings.username, settings.passwd)
        conn_params = pika.ConnectionParameters(
            settings.hostname, settings.port, settings.vhost, user_info)
        self.ip_list = self._getip()
        self.connection = pika.BlockingConnection(conn_params)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=settings.exchange_name,
            exchange_type=settings.exchange_type
        )
        result = self.channel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue
        self._bind_keys()
        self._set_consume()

    def _bind_keys(self):
        """exchange绑定key和queue."""
        for key in self.ip_list:
            self.channel.queue_bind(
                queue=self.queue_name,
                exchange=settings.exchange_name,
                routing_key=key
            )

    def _set_consume(self):
        """设置接收消息的参数."""
        self.channel.basic_consume(
            self._callback, self.queue_name, no_ack=True)

    @staticmethod
    def _getip():
        """获取本地IP地址."""
        network_card_info = psutil.net_if_addrs()
        ip_list = []
        for k, v in network_card_info.items():
            for item in v:
                if item[0] == 2 and not item[1] == '127.0.0.1':
                    ip_list.append(item[1])
        return ip_list

    def _callback(self, channel, method, properties, body):
        """收到消息时的回调方法."""
        command = body
        result = self._exec_cmd(command)
        routing_key = properties.reply_to
        correlation_id = properties.correlation_id
        delivery = method.delivery_tag
        self._put_result_to_rabbit(result, routing_key, correlation_id)
        self.channel.basic_ack(delivery_tag=delivery)

    def _exec_cmd(self, cmd):
        """执行命令."""
        return subprocess.getoutput(cmd)

    def _put_result_to_rabbit(self, message, routing_key, correlation_id):
        """将消息发送到rabbitmq."""
        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(correlation_id=correlation_id)
        )

    def start(self):
        self.channel.start_consuming()


def main():
    ssh = SSHServer()
    ssh.start()
