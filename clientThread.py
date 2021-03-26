# -*- coding: utf-8 -*-
# @Time : 2021/3/10 15:05
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : clientThread.py
# @notice ：ClientThread类

import logging
import time
import queue
import traceback
from threading import Thread
import json

from frameSendThread import FrameSendThread


class ClientThread(Thread):
    def __init__(self, connect, users_dict, user_name):
        super().__init__()
        self.setName(f'{user_name}ClientThread')
        self.logger = logging.getLogger('mainLog.client')

        self.connect = connect

        self.usersDict = users_dict
        self.userName = user_name
        self.controller_list = None

        self.frameSendThread = None

    def run(self):
        try:
            self.logger.debug('run')

            message = {'code': 300}  # 允许登录
            self.connect.send(json.dumps(message).encode())

            if self.userName not in self.usersDict or len(self.usersDict[self.userName]) == 0:
                message = {'code': 331}  # 无视频流
                self.connect.send(json.dumps(message).encode())
                exit(0)

            self.controller_list = self.usersDict[self.userName]
            self.logger.debug(f'len(self.controller_list) {len(self.controller_list)}')

            self.frameSendThread = FrameSendThread(self.connect, self.controller_list)
            self.frameSendThread.setDaemon(True)
            self.frameSendThread.start()

            while 1:
                jsonMessage = self.connect.recv(1024).decode()
                message = json.loads(jsonMessage)
                self.logger.debug(message)

                # 根据 message 的 camera 编号，将消息转发至对应 controller 线程
                self.controller_list[message['camera']].operationQueue.put(message)

        except BaseException as e:
            self.logger.info(traceback.print_exc())

        if self.connect:
            self.connect.close()

        if self.frameSendThread is not None and self.frameSendThread.is_alive():
            self.frameSendThread.close()

        self.logger.debug('close')

    # def send_frame_len(self):  # 发送帧数据大小
    #     frame = self.controller_list[0].frameQueue.get()
    #     # self.logger.debug(len(frame))
    #     lenMessage = {'code': 500, 'data': len(frame)}  # 帧数据大小
    #     self.connect.send(json.dumps(lenMessage).encode())
