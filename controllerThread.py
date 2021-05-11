# -*- coding: utf-8 -*-
# @Time : 2021/3/8 15:29
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : controllerThread.py
# @notice ：ControllerThread类

import logging
import queue
import socket
from threading import Thread
import json

from frameRecvThread import FrameRecvThread


class ControllerThread(Thread):
    def __init__(self, connect: socket.socket, users_dict, user_name):
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

        # self.previewFrame = None  # 预览帧，160*120，57600 Byte
        # self.previewFrameLen = 57600

        self.frameRecvThread = None
        self.frameQueue = queue.Queue(10)  # 存放帧数据
        # self.frameLen = 0

        self.operationQueue = queue.Queue(5)  # client发送的指令

    def run(self):
        try:
            self.logger.debug('run')

            message = {'code': 300}  # 允许登录
            self.connect.send(json.dumps(message).encode())

            # self.previewFrame = self.recv_preview_frame()  # 获取预览图

            while 1:
                try:
                    operation = self.operationQueue.get(timeout=30)
                except queue.Empty:  # 隔一段时间通过异常退出阻塞，检查connect是否断开
                    # self.logger.info("queue.Empty")
                    message = {'code': 340}
                    self.connect.send(json.dumps(message).encode())
                else:
                    self.logger.debug(operation)

                    if operation['code'] == 220:  # 请求视频流
                        self.frameRecvThread = FrameRecvThread(self.connect, self.frameQueue)
                        self.frameRecvThread.setDaemon(True)
                        self.frameRecvThread.start()
                    elif operation['code'] == 322:  # 关闭视频流
                        self.frameRecvThread.close()
                        self.frameRecvThread = None

                    else:  # 510 清晰度设置, 511 帧数设置, 520 遥控指令
                        self.connect.send(json.dumps(operation).encode())

        except BaseException as e:
            self.logger.info(f"run Exception {e}")

        if self in self.controller_list:  # 线程结束前将自己从usersDict中对应的list中删除
            self.controller_list.remove(self)
            self.logger.debug(f'remove(self) {len(self.controller_list)}')

        if len(self.controller_list) == 0:  # 此用户下没有其他在线设备，将用户从usersDict中删除
            self.usersDict.pop(self.userName)
            self.logger.debug('del')

        # self.logger.debug(len(self.usersDict))
        self.logger.debug('close')

    # def recv_preview_frame(self):  # 接受预览图
    #     receivedSize = 0
    #     bytesMessage = b''
    #
    #     while receivedSize < self.previewFrameLen:
    #         res = self.connect.recv(8192)
    #         # print(len(res))
    #         if not res:  # 远端shutdown或close后，不断获取到空的结果
    #             self.isConnect = False
    #             break
    #         receivedSize += len(res)  # 每次收到的服务端的数据有可能小于8192，所以必须用len判断
    #         bytesMessage += res
    #
    #     if receivedSize == self.previewFrameLen:
    #         return bytesMessage
    #     return None


