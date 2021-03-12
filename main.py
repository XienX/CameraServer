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
from clientThread import ClientThread

import pymysql

# log初始化
logging.basicConfig(level=logging.DEBUG,  # filename='my.log')
                    format='%(asctime)s --- %(levelname)s --- %(threadName)s --- %(name)s --- %(message)s')
logger = logging.getLogger('mainLog')
logger.info("Start print log")


class Server:
    def __init__(self, port):
        logger.info("Start init")

        # 连接数据库, Database version : 8.0.17
        try:
            self.db = pymysql.connect(host="localhost", user="root", password="123456", db="cameraserver",
                                      charset="utf8mb4")
        except BaseException as e:
            logger.error(e)
            exit(1)
        self.cursor = self.db.cursor()
        # cursor.execute("SELECT VERSION()")
        # data = cursor.fetchone()
        # print("Database version : %s " % data)
        # self.db.close()

        self.usersDict = dict()  # 用户字典，存放用户和对应摄像头线程
        self.usersDict['testUser'] = []

        # 初始化服务端
        self.socketServer = socket(AF_INET, SOCK_STREAM)  # 创建 socket 对象
        self.socketServer.bind(('', port))
        self.socketServer.listen(5)
        logger.info(f"Start listen in {port}")

        self.server()

    def server(self):  # 监听端口，开始服务
        while True:
            connect, connect_addr = self.socketServer.accept()  # 阻塞，等待客户端连接
            logger.debug(f"{connect_addr} online")

            bytesMessage = connect.recv(1024).decode()
            message = json.loads(bytesMessage)
            logger.debug(f'message {message}')

            if all(k in message for k in ('code', 'userName', 'password')):
                try:  # 登录验证
                    self.cursor.execute('SELECT COUNT(*) FROM USER WHERE userName=%s AND password=%s',
                                        (message['userName'], message['password']))
                    results = self.cursor.fetchone()
                    logger.debug(results)

                    if results[0] == 1:  # 验证成功
                        if message['code'] == 100:  # 控制端的连接请求
                            controllerThread = ControllerThread(connect, self.usersDict['testUser'])
                            controllerThread.setDaemon(True)  # 设置成守护线程
                            controllerThread.start()
                        elif message['code'] == 200:  # 客户端的连接请求
                            clientThread = ClientThread(connect, self.usersDict['testUser'])
                            clientThread.setDaemon(True)
                            clientThread.start()
                        else:
                            logger.error(f'connectTypeCode Error, need 100 or 200, but is {message["code"]}')
                    else:
                        pass

                except pymysql.Error as e:
                    logger.error(e)

            else:
                logger.error(f'code userName password not all exist')


if __name__ == '__main__':
    Server(9800)
