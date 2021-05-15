# -*- coding: utf-8 -*-
# @Time : 2021/3/24 14:37
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : frameSendThread.py
# @notice ：FrameSendThread类--帧发送线程

import json
import logging
import queue
import random
from socket import *
import time
import traceback
from threading import Thread


class FrameSendThread(Thread):  # 视频帧的发送线程
    def __init__(self, connect, controller_list):
        super().__init__()
        self.setName(f'FrameSendThread-{random.randint(0,9999)}')
        self.logger = logging.getLogger('mainLog.frameSend')

        self.controllerConnect = connect

        self.connect = socket()
        self.isAlive = True

        self.controller_list = controller_list

        self.nowCameraNum = 0

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
            time.sleep(0.1)
            message = {'code': 320, 'port': port}
            self.controllerConnect.send(json.dumps(message).encode())

            # 连接
            self.connect, connect_addr = socketServer.accept()
            self.logger.debug(f"{connect_addr} online")
            socketServer.close()

            while self.isAlive:
                # self.logger.debug(self.nowCameraNum)
                self.send_frame()
                time.sleep(0.02)

        except queue.Empty:
            self.logger.info("queue.Empty")
        except BaseException as e:
            self.logger.debug(traceback.print_exc())

        # 关闭正在传输的视频流线程
        self.controller_list[self.nowCameraNum].operationQueue.put({'code': 322})

        self.logger.info('FrameSendThread end')

    # def send_frame(self):  # 发送一帧数据
    #     # flag, frame = self.camera.cap.read()
    #     frame = self.camera.get_frame()
    #     # print(frame)
    #     frameData = frame.tobytes()
    #     # print(len(frameData))  # 921600
    #     self.connect.sendall(frameData)

    def send_frame(self):  # 发送一帧数据
        data = self.controller_list[self.nowCameraNum].frameQueue.get(timeout=10)  # 阻塞等待10s，失败会产生queue.Empty

        # message = {'code': 500, 'frameLen': data['frameLen']}
        # self.connect.send(json.dumps(message).encode())
        # time.sleep(0.01)
        self.connect.send(data['frameLen'].to_bytes(4, byteorder='big'))
        self.logger.debug(data['frameLen'])
        self.connect.sendall(data['frame'])
        # self.logger.debug('send')

    def close(self):  # 结束
        self.connect.close()
        self.isAlive = False

        self.logger.debug('FrameSendThread.close(self)')
