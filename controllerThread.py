# -*- coding: utf-8 -*-
# @Time : 2021/3/8 15:29
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : controllerThread.py
# @notice ：

import logging
from queue import Queue
from threading import Thread
import json


class ControllerThread(Thread):
    def __init__(self, connect, controller_list):
        super().__init__()
        self.setName('testUserControllerThread')

        self.logger = logging.getLogger('mainLog.controller')
        self.logger.debug('__init__')

        self.connect = connect

        self.controller_list = controller_list
        self.controller_list.append(self)
        self.logger.debug(f'len(self.controller_list) {len(self.controller_list)}')

        self.frameQueue = Queue(25)  # 存放帧数据

    def run(self):
        self.logger.debug('run')

        message = {'code': 300}  # 允许登录
        self.connect.send(json.dumps(message).encode())

        bytesMessage = self.connect.recv(1024)
        message = json.loads(bytesMessage.decode())
        self.logger.debug(message)

        if message['code'] == 500:
            frame = self.recv_frame(message['data'])
            if frame != -1:
                self.frameQueue.put(frame)

        # while 1:
        #     pass

    def recv_frame(self, size):  # 根据数据长度接受一帧数据
        receivedSize = 0
        bytesMessage = b''

        while receivedSize < size:
            res = self.connect.recv(8192)
            receivedSize += len(res)  # 每次收到的服务端的数据有可能小于8192，所以必须用len判断
            bytesMessage += res

        # message = json.loads(bytesMessage.decode())
        # self.logger.debug(message)
        # self.logger.debug(len(bytesMessage))
        # if message['code'] == 350:
        #     return message['data']
        # else:
        #     return -1

        if len(bytesMessage) == size:
            return bytesMessage
        else:
            return -1
