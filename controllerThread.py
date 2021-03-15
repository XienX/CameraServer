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
    def __init__(self, connect, users_dict, user_name):
        super().__init__()
        self.setName(f'{user_name}ControllerThread')

        self.logger = logging.getLogger('mainLog.controller')

        self.connect = connect
        self.isConnect = True

        self.usersDict = users_dict
        self.userName = user_name
        self.controller_list = self.usersDict[self.userName]
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

                while self.isConnect:
                    frame = self.recv_frame()
                    # self.logger.debug(type(frame))
                    if type(frame) == bytes:
                        self.logger.debug(f'Queue.qsize() {self.frameQueue.qsize()}')
                        if self.frameQueue.full():
                            self.frameQueue.get()
                        self.frameQueue.put(frame)

        except BaseException as e:
            self.logger.info(f"run Exception {e}")

        if self in self.controller_list:  # 线程结束前将自己从usersDict中对应的list中删除
            self.controller_list.remove(self)
            # self.logger.debug(f'len2(self.controller_list) {len(self.controller_list)}')

        if len(self.controller_list) == 0:  # 此用户下没有其他在线设备，将用户从usersDict中删除
            del self.usersDict[self.userName]
            self.logger.debug('del')

        # self.logger.debug(len(self.usersDict))
        self.logger.debug('close')

    def recv_frame(self):  # 根据数据长度接受一帧数据
        receivedSize = 0
        bytesMessage = b''

        while receivedSize < self.frameLen:
            res = self.connect.recv(8192)
            # print(len(res))
            if len(res) == 0:  # 远端shutdown或close后，不断获取到空的结果
                self.isConnect = False
                break
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
