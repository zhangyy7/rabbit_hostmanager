#! /usr/bin/env python
# -*- coding:utf-8 -*-
# from core import ssh_client_rpc
from core import ssh_server_rpc as s
from core import ssh_client_rpc as c


def main():
    inp = input("1.启动server 2.启动客户端")
    if inp == "1":
        s.main()
    elif inp == "2":
        c.main()
