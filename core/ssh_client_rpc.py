#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""基于rabbitmq的简单ssh server端."""

import pika
import uuid
import sys
from conf import settings


class SSHClient(object):
    """ssh server类，从rabbitmq服务器获取客户端命令、执行、返回结果到指定的queue."""

    def __init__(self):
        """初始化连接到rabbitmq服务器的参数."""
        self._task_id = 0
        self.task_dict = {}  # key:task_id value:任务执行结果
        self.task_correlation_ref = {}  # key: task_id value:correlation_id
        user_info = pika.PlainCredentials(
            settings.username, settings.passwd)
        conn_params = pika.ConnectionParameters(
            settings.hostname, settings.port, settings.vhost, user_info)
        self.connection = pika.BlockingConnection(conn_params)
        self.channel = self.connection.channel()
        res = self.channel.queue_declare(exclusive=True)
        self.res_queue = res.method.queue
        self.channel.exchange_declare(
            exchange=settings.exchange_name,
            exchange_type=settings.exchange_type)
        self._set_consume()
        self.route = {
            "1": self.send2rabbit,
            "2": self.check_task,
            "3": sys.exit
        }

    def _set_consume(self):
        """设置接收消息的参数."""
        self.channel.basic_consume(
            self._callback, queue=self.res_queue)

    def _callback(self, channel, method, properties, body):
        """收到消息时的回调方法."""
        for task_id, correlation_id in self.task_correlation_ref.items():
            if str(correlation_id) == properties.correlation_id:
                self.task_dict[task_id]["res"] = body.decode()
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def _send_cmd_to_rabbit(
            self, exchange, routing_key, message):
        """将消息发送到rabbitmq."""
        self._task_id += 1
        correlation_id = uuid.uuid4()
        self.task_correlation_ref[self._task_id] = correlation_id
        self.task_dict[self._task_id] = {"res": None, "host": routing_key}
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                reply_to=self.res_queue,
                correlation_id=str(correlation_id),
            )
        )

    def _clear_task(self, key):
        """删除保存任务的2个字典的key."""
        del self.task_correlation_ref[key]
        del self.task_dict[key]

    def _check_task(self, task_id):
        """检查任务执行结果是否已返回.

        :param int task_id: 任务编号
        :return: 检查结果
        """
        self.connection.process_data_events()
        if task_id in self.task_dict:
            if self.task_dict[task_id]:
                result = self.task_dict[task_id]["res"].encode()
                self._clear_task(task_id)
            else:
                result = '结果未返回'.encode()
        else:
            result = '任务不存在'.encode()
        return result

    def send2rabbit(self):
        """获取用户输入."""
        print("命令格式为：cmd host1[host2 [host3...]]")
        inp = input("请输入命令：>>").strip()
        cmd, *routing_keys = inp.split()
        print("cmd:", cmd)
        for routing_key in routing_keys:
            self._send_cmd_to_rabbit(
                exchange=settings.exchange_name,
                routing_key=routing_key,
                message=cmd
            )

    def _get_task(self):
        """将当前存在的task拼接成字符串并return."""
        temp_list = []
        for task_id in self.task_dict:
            task_info = "task_id:{},host:{}".format(
                task_id, self.task_dict[task_id]["host"])
            temp_list.append(task_info)
        all_task_info = '\n'.join(temp_list)
        return all_task_info

    def check_task(self):
        """获取用户输入的task_id交给_check_task执行."""
        all_task_info = self._get_task()
        print("当前执行中的任务信息如下：\n{}".format(all_task_info))
        task_id = input("请输入任务编号>>")
        try:
            task_id = int(task_id)
        except ValueError:
            print("任务ID输入有误")
            return
        result = self._check_task(task_id).decode()
        print(result)

    def interactive(self):
        """与用户交互的方法."""
        while True:
            choice = input("1.执行命令 2.查看结果 3.退出程序").strip()
            if self.route.get(choice, 0):
                self.route[choice]()
            else:
                print("没有这个选项")
                continue


def main():
    ssh = SSHClient()
    ssh.interactive()
