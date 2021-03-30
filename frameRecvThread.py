# -*- coding: utf-8 -*-
# @Time : 2021/3/23 16:29
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : frameRecvThread.py
# @notice ：FrameRecvThread类--帧接受线程

import logging
import random
import traceback
from socket import *
from threading import Thread
import json


class FrameRecvThread(Thread):
    def __init__(self, connect, frame_queue):
        super().__init__()
        self.setName('FrameRecvThread')
        self.logger = logging.getLogger('mainLog.frameRecv')

        self.controllerConnect = connect

        self.connect = None
        self.isConnect = True

        # self.frameLen = 921600  # 默认640*480
        self.frameQueue = frame_queue

    def run(self):
        try:
            # 选择未占用的端口，开启
            socketServer = socket(AF_INET, SOCK_STREAM)
            while 1:
                try:
                    port = random.randint(10000, 50000)
                    socketServer.bind(('', port))
                except Exception:
                    self.logger.debug(traceback.print_exc())
                else:
                    break

            socketServer.listen(1)
            self.logger.info(f"listen in {port}")

            # 用 controllerConnect 发送端口号
            message = {'code': 320, 'port': port}
            self.controllerConnect.send(json.dumps(message).encode())

            # 连接
            self.connect, connect_addr = socketServer.accept()
            self.logger.debug(f"{connect_addr} online")
            socketServer.close()

            # 接受视频帧放入frameQueue
            while self.isConnect:
                frame = self.recv_frame()
                # self.logger.debug(type(frame))
                if frame is not None:
                    self.logger.debug(f'Queue.qsize() {self.frameQueue.qsize()}')
                    if self.frameQueue.full():
                        self.frameQueue.get()
                    self.frameQueue.put(frame)

        except BaseException as e:
            self.logger.info(f"run Exception {e}")
            # self.logger.debug(traceback.print_exc())

            # --关闭controllerThread--

        self.logger.debug('close')

    def recv_frame(self):  # 根据数据长度接受一帧数据
        receivedSize = 0
        bytesMessage = b''

        frameLenBytesMessage = self.connect.recv(1024).decode()
        message = json.loads(frameLenBytesMessage)

        if message['code'] == 500:
            frameLen = message['frameLen']

            while receivedSize < frameLen:
                res = self.connect.recv(8192)
                # print(len(res))
                if not res:  # 远端shutdown或close后，不断获取到空的结果
                    self.isConnect = False
                    break
                receivedSize += len(res)  # 每次收到的服务端的数据有可能小于8192，所以必须用len判断
                bytesMessage += res

            if receivedSize == frameLen:
                return {'frameLen': frameLen, 'frame': bytesMessage}

        return None

    def close(self):  # 关闭此线程
        pass
