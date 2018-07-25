#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import sys
import time
import json
import os
import functools
import threading
import queue
from PyQt5.Qt import QApplication, QWidget, QTextEdit, QFrame, QVBoxLayout, QGridLayout, QDesktopWidget, QTextCursor, \
    QPushButton, QIcon, QPixmap, QThread
from PyQt5.QtCore import QObject, pyqtSignal

from uarm.wrapper import SwiftAPI

sys.path.append('..')
from log import logger


class XArmThread(QThread):
    signal = pyqtSignal(dict)

    def __init__(self, que, check=False):
        super(XArmThread, self).__init__()
        self.que = que
        self.check = check

    def run(self):
        while True:
            try:
                if self.check:
                    try:
                        item = self.que.get(timeout=1)
                    except:
                        item = {'type': 'timeout', 'item': {}}
                else:
                    item = self.que.get()
                self.signal.emit(item)
            except Exception as e:
                pass


class UArmHandler(object):
    def __init__(self, ui):
        super(UArmHandler, self).__init__()
        self.ui = ui

        self.arm = None
        self.port = None
        self.cmd_que = queue.Queue(100)
        self.cmd_thread = XArmThread(self.cmd_que, check=False)
        self.cmd_thread.signal.connect(self.run_cmd)
        self.cmd_thread.start()

        self.report_que = queue.Queue()
        self.report_thread = XArmThread(self.report_que, check=True)
        self.report_thread.signal.connect(self.update_ui)
        self.report_thread.start()

    def run_cmd(self, item):
        try:
            if self.arm and self.arm.connected:
                func = getattr(self.arm, item['cmd'])
                # log(item['cmd']+':', func(*item.get('args', []), **item.get('kwargs', {})))
                ret = func(*item.get('args', []), **item.get('kwargs', {}))
                if item['cmd'] == 'get_position' and isinstance(ret, list) and len(ret) >= 3:
                    self.report_que.put({
                        'type': 'location',
                        'item': {
                            'position': ret,
                            'angles': None
                        }
                    })
                elif item['cmd'] == 'get_polar' and isinstance(ret, list) and len(ret) >= 3:
                    self.report_que.put({
                        'type': 'location',
                        'item': {
                            'position': [None, None, None, *ret],
                            'angles': None
                        }
                    })
                elif item['cmd'] == 'get_servo_angle' and isinstance(ret, list) and len(ret) >= 3:
                    self.report_que.put({
                        'type': 'location',
                        'item': {
                            'position': None,
                            'angles': ret
                        }
                    })
                elif item['cmd'] == 'get_device_info':
                    self.report_que.put({
                        'type': 'info',
                        'item': ret
                    })
                elif item['cmd'] == 'get_mode' or item['cmd'] == 'set_mode':
                    self.report_que.put({
                        'type': 'mode',
                        'item': {
                            'mode': ret
                        }
                    })
                # if isinstance(ret, int) and ret == TCP_OR_JOINT_LIMIT:
                #     self.ui.reset_flag()
                logger.debug('cmd: {}, ret:{}, args: {}, kwargs: {}'.format(item['cmd'], ret, item.get('args', []),
                                                                            item.get('kwargs', {})))
            else:
                self.cmd_que.queue.clear()
                self.report_connected_callback({
                    'connected': False
                })
                logger.debug('cmd: {}, ret: xArm is not connected'.format(item['cmd']))
        except:
            pass

    def connect(self, port):
        try:
            logger.debug('try connect to {}'.format(port))
            if self.arm and self.arm.connected:
                logger.info('disconnect from {}'.format(self.port))
                self.arm.disconnect()
        except Exception as e:
            print(e)
        threading.Thread(target=self.connnect_thread, args=(port,), daemon=True).start()

    def connnect_thread(self, port):
        try:
            self.port = port
            self.arm = SwiftAPI(port=port,
                                do_not_open=True)
            self.arm.connect()
            if not self.arm.connected:
                time.sleep(0.5)
            self.arm.waiting_ready()
            self.report_connected_callback({
                    'connected': True
                })
            device_info = self.arm.get_device_info()
            self.report_que.put({
                'type': 'info',
                'item': device_info
            })
            mode = self.arm.get_mode()
            self.report_que.put({
                'type': 'mode',
                'item': {
                    'mode': mode
                }
            })
            position = self.arm.get_position()
            if isinstance(position, list) and len(position) >= 3:
                self.report_que.put({
                    'type': 'location',
                    'item': {
                        'position': position,
                        'angles': None
                    }
                })
            polar = self.arm.get_polar()
            if isinstance(polar, list) and len(polar) >= 3:
                self.report_que.put({
                    'type': 'location',
                    'item': {
                        'position': [None, None, None, *polar],
                        'angles': None
                    }
                })
            angles = self.arm.get_servo_angle()
            if isinstance(angles, list) and len(angles) >= 3:
                self.report_que.put({
                    'type': 'location',
                    'item': {
                        'position': None,
                        'angles': angles
                    }
                })
            return True
        except Exception as e:
            # print(e)
            self.report_connected_callback({
                'connected': False
            })

    def disconnect(self):
        try:
            if self.arm and self.arm.connected:
                self.arm.disconnect()
                self.report_connected_callback({
                    'connected': False
                })
                # logger.info('diconnect from {}'.format(self.addr))
        except Exception as e:
            print(e)

    def update_ui(self, data):
        item = data['item']
        if data['type'] == 'timeout':
            if not self.arm or not self.arm.connected:
                self.ui.update_connect_status(False)
        elif data['type'] == 'connect':
            self.ui.update_connect_status(item['connected'])
        elif data['type'] == 'location':
            pos = item['position']
            angles = item['angles']
            if angles:
                self.ui.axis_ui.update_joints(angles)
            if pos:
                self.ui.cartesian_ui.update_cartesians(pos)
        elif data['type'] == 'info':
            self.ui.update_device_info(item)
        elif data['type'] == 'mode':
            self.ui.update_mode(item['mode'])

    def report_connected_callback(self, item):
        self.report_que.put({
            'type': 'connect',
            'item': item
        })

    def put_cmd_que(self, item):
        self.cmd_que.put(item)




