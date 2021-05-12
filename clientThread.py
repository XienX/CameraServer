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
    def __init__(self, connect, users_dict: dict, user_name):
        super().__init__()
        self.setName(f'{user_name}ClientThread')
        self.logger = logging.getLogger('mainLog.client')

        self.connect = connect

        self.usersDict = users_dict
        self.userName = user_name
        self.maxCameraNum = 0
        self.controller_list = None
        self.frameSendThread = None

    def run(self):
        try:
            self.logger.debug('run')

            # 发送允许登录消息
            message = {'code': 300}  # 允许登录
            self.connect.send(json.dumps(message).encode())

            self.controller_list = self.usersDict.get(self.userName)  # 主线程已创建，必存在
            # self.logger.debug(f'type(self.controller_list) {type(self.controller_list)}')
            # if self.userName not in self.usersDict or len(self.usersDict[self.userName]) == 0:
            #     message = {'code': 331}  # 无视频流
            #     self.connect.send(json.dumps(message).encode())
            #     exit(0)
            self.maxCameraNum = len(self.controller_list)
            self.logger.debug(f'self.maxCameraNum {self.maxCameraNum}')

            # 发送摄像头数量消息
            message = {'code': 321, 'num': self.maxCameraNum}
            self.connect.send(json.dumps(message).encode())

            if self.maxCameraNum == 0:  # 无在线设备，结束
                exit(0)

            # 创建视频发送线程
            self.frameSendThread = FrameSendThread(self.connect, self.controller_list)
            self.frameSendThread.setDaemon(True)
            self.frameSendThread.start()
            self.controller_list[0].operationQueue.put({'code': 220})  # 初始默认0号

            while 1:
                jsonMessage = self.connect.recv(1024).decode()
                message = json.loads(jsonMessage)
                self.logger.debug(message)

                # # 根据 message 的 camera 编号，将消息转发至对应 controller 线程
                # self.controller_list[message['camera']].operationQueue.put(message)

                if message['code'] == 220:  # 选择摄像头
                    # 关闭旧的摄像头视频流线程
                    self.controller_list[self.frameSendThread.nowCameraNum].operationQueue.put({'code': 322})

                    # 改为读取新的摄像头
                    self.frameSendThread.nowCameraNum = message['camera']

                    # 打开新的摄像头视频流线程
                    self.controller_list[message['camera']].operationQueue.put(message)

                    # 发送摄像头数量消息
                    message = {'code': 321, 'num': self.maxCameraNum}
                    self.connect.send(json.dumps(message).encode())

                elif message['code'] == 510:  # 设置清晰度
                    # 转发
                    self.controller_list[message['camera']].operationQueue.put(message)

                    # 回馈
                    self.connect.send(self.controller_list[message['camera']].connect.recv(1024))

        except BaseException as e:
            self.logger.info(traceback.print_exc())

        if self.connect:
            self.connect.close()

        if self.frameSendThread is not None and self.frameSendThread.is_alive():
            self.frameSendThread.close()

        self.logger.debug('close')

    # def get_max_camera_num(self):  # 获取在线摄像头数量
    #     if self.controller_list is None:
    #         return 0
    #     else:
    #         return len(self.controller_list)

    # def send_frame_len(self):  # 发送帧数据大小
    #     frame = self.controller_list[0].frameQueue.get()
    #     # self.logger.debug(len(frame))
    #     lenMessage = {'code': 500, 'data': len(frame)}  # 帧数据大小
    #     self.connect.send(json.dumps(lenMessage).encode())
