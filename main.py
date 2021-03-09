# -*- coding: utf-8 -*-
# @Time : 2021/3/8 14:27
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : main.py
# @notice ：

import logging
import json
from socket import *

from controllerThread import ControllerThread

# log初始化
logging.basicConfig(level=logging.DEBUG,  # filename='my.log')
                    format='%(asctime)s --- %(levelname)s --- %(threadName)s --- %(name)s --- %(message)s')
logger = logging.getLogger('mainLog')
logger.info("Start print log")


class Server():
    def __init__(self, port):
        logger.info("Start init")
        self.usersDict = dict()  # 用户字典，存放用户和对应摄像头线程

        # 初始化服务端
        self.socketServer = socket(AF_INET, SOCK_STREAM)  # 创建 socket 对象
        self.socketServer.bind(('', port))
        self.socketServer.listen(5)
        logger.info(f"Start listen in {port}")

        self.listen()

    def listen(self):  # 监听端口，开始服务
        while True:
            client, client_addr = self.socketServer.accept()  # 阻塞，等待客户端连接
            logger.debug(f"{client_addr} online")

            message = client.recv(2048).decode()
            logger.info(json.loads(message)['code'])


            # controllerThread = ControllerThread()
            # controllerThread.setDaemon(True)  # 设置成守护线程
            # controllerThread.start()





if __name__ == '__main__':
    Server(9800)

    # cThread = ControllerThread()
    # cThread.start()
    #
    # usersDict['testUser'] = [cThread]
    #
    # logger.debug(usersDict['testUser'][0].frameQueue.get())
    # logger.debug(len(usersDict['testUser']))
    #
    # usersDict['testUser'].pop()
    # logger.debug(len(usersDict['testUser']))
