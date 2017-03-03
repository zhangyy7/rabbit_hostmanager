# rabbit_hostmanager
基于rabbitmq的命令分发软件
### 作者介绍：
* author：zhangyy
* nickname:逆光穿行
* github:[zhangyy.com](https://github.com/zhangyy7)

### 功能介绍：
- 给多台主机发送命令，异步的获取执行结果
- 跨平台


### 环境依赖：
* Python3.5+
* pip3 install psutil
* pip3 install pika
* rabbitmq

### 目录结构：

    FTPServer
    ├── index.py #程序唯一入口脚本
    ├── README.md
    ├── bin
    │   ├── __init__.py
    │   └── main.py #主函数
    ├── core #程序核心目录
    │   ├── ssh_client_rpc.py #客户端，发命令收结果
    |   └── ssh_server_rpc.py #服务端，收命令发结果
    |── couf
        └── settings.py #配置文件



###使用说明：
* 测试使用多台机器，每台机器需从github clone项目
* [rabbit_hostmanager](https://github.com/zhangyy7/rabbit_hostmanager.git)
* 其中一台作为rabbitmq中间件服务器，需安装rabbitmq
* 随意选择一台机器作为客户端，运行python index.py，启动客户端
* 除rabbitmq服务器和客户端机器外的其他机器运行python index.py启动服务端
* 客户端侧根据提示可以执行命令、查看命令结果、退出程序，执行命令的格式入下：cmd host1 host2 ....，每个host生成一个task_id，查看命令结果时会展示当前执行中的任务ID，输入task_id查询结果，如果已有结果则打印结果并删除此任务；没有结果打印提示继续其他操作，所有步骤都不阻塞。
