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
        self.setName('ControllerThread')

        self.logger = logging.getLogger('mainLog.controller')

        self.connect = connect

        self.controller_list = controller_list
        self.controller_list.append(self)
        self.logger.debug(f'len(self.controller_list) {len(self.controller_list)}')

        self.frameQueue = Queue(10)  # 存放帧数据
        self.frameLen = 0

    def run(self):
        try:
            self.logger.debug('run')

            message = {'code': 300}  # 允许登录
            self.connect.send(json.dumps(message).encode())

            bytesMessage = self.connect.recv(1024)
            message = json.loads(bytesMessage.decode())
            self.logger.debug(message)

            if message['code'] == 500:
                self.frameLen = message['data']
                self.logger.debug(f'frameLen {self.frameLen}')

                while 1:
                    frame = self.recv_frame()
                    if type(frame) == bytes:
                        self.logger.debug(f'Queue.qsize() {self.frameQueue.qsize()}')
                        if self.frameQueue.full():
                            self.frameQueue.get()
                        self.frameQueue.put(frame)

        except BaseException as e:
            self.logger.info(f"run Exception {e}")

    def recv_frame(self):  # 根据数据长度接受一帧数据
        receivedSize = 0
        bytesMessage = b''

        while receivedSize < self.frameLen:
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

        if receivedSize == self.frameLen:
            return bytesMessage
        return None
