# -*- coding: utf-8 -*-
# @Time : 2021/3/8 15:29
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : controllerThread.py
# @notice ：

import logging
from queue import Queue
from threading import Thread


class ControllerThread(Thread):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('mainLog.controllerServer')
        self.logger.info('__init__')
        self.frameQueue = Queue(10)
        self.frameQueue.put("hhh")

    def run(self):
        self.logger.info('run')
        while 1:
            pass

