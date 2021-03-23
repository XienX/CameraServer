# -*- coding: utf-8 -*-
# @Time : 2021/3/8 14:27
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : main.py
# @notice ：程序入口，log初始化，Server类

import logging
import json
import traceback
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
        # self.usersDict['test'] = []

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

            try:
                bytesMessage = connect.recv(1024).decode()
                message = json.loads(bytesMessage)
                logger.debug(f'message {message}')

                if 'code' in message:
                    if message['code'] == 100 or message['code'] == 200:  # 登录请求
                        if 'userName' in message and 'password' in message:
                            try:  # 登录验证
                                self.cursor.execute('SELECT COUNT(*) FROM USER WHERE userName=%s AND password=%s',
                                                    (message['userName'], message['password']))
                                results = self.cursor.fetchone()
                                # logger.debug(results)

                                if results[0] == 1:  # 验证成功
                                    if message['userName'] not in self.usersDict:  # usersDict中不存在该用户，添加
                                        self.usersDict[message['userName']] = []

                                    if message['code'] == 100:  # 控制端的连接请求
                                        controllerThread = ControllerThread(connect, self.usersDict, message['userName'])
                                        controllerThread.setDaemon(True)  # 设置成守护线程
                                        controllerThread.start()
                                    elif message['code'] == 200:  # 客户端的连接请求
                                        clientThread = ClientThread(connect, self.usersDict, message['userName'])
                                        clientThread.setDaemon(True)
                                        clientThread.start()

                                else:
                                    refuseMessage = {'code': 301}  # 拒绝登录
                                    connect.send(json.dumps(refuseMessage).encode())
                                    logger.info(f'login refuse, message is {message}')

                            except pymysql.Error as e:  # 数据库错误
                                returnMessage = {'code': 420}
                                connect.send(json.dumps(returnMessage).encode())
                                logger.error(f'pymysql.Error {e}')
                        else:  # 缺少必须字段
                            returnMessage = {'code': 412}
                            connect.send(json.dumps(returnMessage).encode())
                            logger.error('userName or password not exist')

                    elif message['code'] == 210:  # 注册请求
                        logger.debug('register')
                        if 'userName' in message and 'password' in message:
                            try:  # 用户是否重名
                                self.cursor.execute('SELECT COUNT(*) FROM USER WHERE userName=%s', (message['userName']))
                                results = self.cursor.fetchone()
                                logger.debug(results)

                                if results[0] == 0:  # 未重复
                                    try:
                                        self.cursor.execute('INSERT INTO USER VALUES (%s, %s)',
                                                            (message['userName'], message['password']))
                                        self.db.commit()

                                        returnMessage = {'code': 310}  # 注册成功
                                        connect.send(json.dumps(returnMessage).encode())
                                        logger.info(f'register success, message is {message}')
                                    except pymysql.Error as e:  # 数据库错误
                                        self.db.rollback()
                                        returnMessage = {'code': 420}
                                        connect.send(json.dumps(returnMessage).encode())
                                        logger.error(traceback.print_exc())

                                else:
                                    returnMessage = {'code': 311}  # 注册失败，用户名已存在
                                    connect.send(json.dumps(returnMessage).encode())
                                    logger.info(f'register failed, message is {message}')
                            except BaseException as e:
                                logger.error(traceback.print_exc())

                        else:  # 缺少必须字段
                            returnMessage = {'code': 412}
                            connect.send(json.dumps(returnMessage).encode())
                            logger.error('userName or password not exist')

                    else:  # 非预期code
                        returnMessage = {'code': 411}
                        connect.send(json.dumps(returnMessage).encode())
                        logger.error(f'need code 100, 200 or 210, but is {message["code"]}')

                else:  # 缺少code
                    returnMessage = {'code': 410}
                    connect.send(json.dumps(returnMessage).encode())
                    logger.error(f'code not exist')

            except json.decoder.JSONDecodeError:  # Json错误
                returnMessage = {'code': 430}
                connect.send(json.dumps(returnMessage).encode())
                logger.error(traceback.print_exc())
            except error:  # socket.error
                logger.error(traceback.print_exc())
            except BaseException:  # 未定义错误, 400
                # returnMessage = {'code': 400}
                # connect.send(json.dumps(returnMessage).encode())
                logger.error(traceback.print_exc())


if __name__ == '__main__':
    Server(9800)
