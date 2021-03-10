# -*- coding: utf-8 -*-
# @Time : 2021/3/10 15:05
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : clientThread.py
# @notice ：

import logging
from queue import Queue
from threading import Thread
import json


class ClientThread(Thread):
    def __init__(self, connect, controller_list):
        super().__init__()
        self.setName('testUserClientThread')

        self.logger = logging.getLogger('mainLog.client')
        self.logger.debug('__init__')

        self.connect = connect

        self.controller_list = controller_list
        self.logger.debug(f'len(self.controller_list) {len(self.controller_list)}')

    def run(self):
        self.logger.debug('run')

        message = {'code': 300}  # 允许登录
        self.connect.send(json.dumps(message).encode())

        self.send_frame()

    def send_frame(self):  # 发送一帧数据
        frame = self.controller_list[0].frameQueue.get()
        self.logger.debug(len(frame))
        lenMessage = {'code': 500, 'data': len(frame)}  # 帧数据大小
        self.connect.send(json.dumps(lenMessage).encode())

        try:
            self.logger.debug(self.connect.sendall(frame))
        except BaseException as e:
            print(e)
