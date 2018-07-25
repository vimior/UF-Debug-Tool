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

from xarm.wrapper import XArmAPI
from xarm.core.config import x2_config
from xarm.x3.error import ServoError, ControlError, ControlWarn

sys.path.append('..')
from log import logger

lock = threading.Lock()
on_init = False

RAD_DEGREE = 57.295779513082320876798154814105
TCP_OR_JOINT_LIMIT = -6


def log_servo_error(servo, state, errno, only_log_error_servo=True):
    if only_log_error_servo and errno == 0:
        return
    logger.info('伺服: {},  状态: {}'.format(servo, state))
    if errno != 0:
        error = ServoError(errno)
        logger.info('报警代码: <span style="color: red">{}</span>'.format(hex(error.errno)))
        logger.info('报警说明: <span style="color: red">{}</span>'.format(error.description))
        logger.info('报警处理:      ')
        for i, h in enumerate(error.handle):
            logger.info('------>{}. <span style="color: red">{}</span>'.format(i + 1, h))
    logger.log('-' * 50)


class XArmThread(QThread):
    signal = pyqtSignal(dict)

    def __init__(self, que):
        super(XArmThread, self).__init__()
        self.que = que

    def run(self):
        while True:
            try:
                item = self.que.get()
                self.signal.emit(item)
            except:
                pass


class XArmHandler(object):
    def __init__(self, ui):
        super(XArmHandler, self).__init__()
        self.ui = ui

        self.xarm = None
        self.addr = None
        self.report_type = 'normal'
        self.cmd_que = queue.Queue(100)

        self.cmd_thread = XArmThread(self.cmd_que)
        self.cmd_thread.signal.connect(self.run_cmd)
        self.cmd_thread.start()
        # threading.Thread(target=self._handle_cmd_thread, daemon=True).start()

        self.report_que = queue.Queue()
        self.report_thread = XArmThread(self.report_que)
        self.report_thread.signal.connect(self.update_ui)
        self.report_thread.start()

    def run_cmd(self, item):
        try:
            if self.xarm and self.xarm.connected:
                func = getattr(self.xarm, item['cmd'])
                # log(item['cmd']+':', func(*item.get('args', []), **item.get('kwargs', {})))
                ret = func(*item.get('args', []), **item.get('kwargs', {}))
                if isinstance(ret, int) and ret == TCP_OR_JOINT_LIMIT:
                    self.ui.reset_flag()
                logger.debug('cmd: {}, ret:{}, args: {}, kwargs: {}'.format(item['cmd'], ret, item.get('args', []),
                                                                            item.get('kwargs', {})))
            else:
                self.cmd_que.queue.clear()
                logger.debug('cmd: {}, ret: xArm is not connected'.format(item['cmd']))
        except:
            pass

    def connect(self, addr, report_type='normal'):
        try:
            logger.debug('try connect to {}, report: {}'.format(addr, report_type))
            if self.xarm and self.xarm.connected:
                logger.info('disconnect from {}'.format(self.addr))
                self.xarm.disconnect()
        except Exception as e:
            print(e)
        threading.Thread(target=self.connnect_thread, args=(addr, report_type), daemon=True).start()

    def connnect_thread(self, addr, report_type):
        try:
            self.addr = addr
            self.xarm = XArmAPI(port=addr,
                                enable_heartbeat=True,
                                enable_report=True,
                                report_type=report_type, do_not_open=True)
            self.xarm.register_maable_mtbrake_changed_callback(self.report_brake_callback)
            self.xarm.register_state_changed_callback(self.report_state_callback)
            self.xarm.register_connect_changed_callback(self.report_connected_callback)
            self.xarm.register_report_location_callback(self.report_location_callback, report_cartesian=True, report_joints=True)
            self.xarm.register_error_warn_changed_callback(self.report_warn_error_callback)
            self.xarm.register_cmdnum_changed_callback(self.report_cmdnum_callback)
            self.xarm.connect()
            if not self.xarm.connected:
                time.sleep(0.5)
            # threading.Timer(1, self.init_robot).start()
            self.report_type = report_type
            return True
        except Exception as e:
            self.report_que.put({
                'type': 'connect',
                'item': {
                    'mainConnected': False,
                    'reportConnected': False
                }
            })

    def disconnect(self):
        try:
            if self.xarm and self.xarm.connected:
                self.xarm.disconnect()
                # logger.info('diconnect from {}'.format(self.addr))
        except Exception as e:
            print(e)

    def update_ui(self, data):
        item = data['item']
        if data['type'] == 'brake':
            maable, mtbrake = item['maable'], item['mtbrake']
            self.ui.axis_ui.brake_changed_callback(list(map(lambda x: bool(x[0] & x[1]), zip(mtbrake, maable))))
            maable_value = 0
            for i, v in enumerate(maable):
                if v is True:
                    maable_value += pow(2, i)
            mtbrake_value = 0
            for i, v in enumerate(mtbrake):
                if v is True:
                    mtbrake_value += pow(2, i)
            self.ui.update_maable_mtbrake(maable_value, mtbrake_value)

            # self.ui.update_maable_mtbrake(maable, mtbrake)
            # mtbrake = [mtbrake & 0x01, mtbrake >> 1 & 0x01, mtbrake >> 2 & 0x01, mtbrake >> 3 & 0x01,
            #            mtbrake >> 4 & 0x01, mtbrake >> 5 & 0x01, mtbrake >> 6 & 0x01, mtbrake >> 7 & 0x01]
            # maable = [maable & 0x01, maable >> 1 & 0x01, maable >> 2 & 0x01, maable >> 3 & 0x01,
            #           maable >> 4 & 0x01, maable >> 5 & 0x01, maable >> 6 & 0x01, maable >> 7 & 0x01]
            # self.ui.axis_ui.brake_changed_callback(list(map(lambda x: bool(x[0] & x[1]), zip(mtbrake, maable))))

        elif data['type'] == 'error':
            self.ui.update_warn_error([item['warnCode'], item['errorCode']])
            if item['errorCode'] != 0 or item['warnCode'] != 0:
                if item['warnCode'] != 0:
                    logger.warn('warn: code: {}, desc: {}'.format(item['warnCode'], ControlWarn(item['warnCode']).description))
                if item['errorCode'] != 0:
                    logger.error('error: code: {}, desc: {}'.format(item['errorCode'], ControlError(item['errorCode']).description))
            else:
                logger.info('warn: {}, error: {}'.format(item['warnCode'], item['errorCode']))
            if item['errorCode'] != 0:
                try:
                    self.get_servo_debug_msg()
                except Exception as e:
                    logger.error(str(e))
        elif data['type'] == 'state':
            state = item['state']
            self.ui.update_state(state)
        elif data['type'] == 'connect':
            self.ui.update_connect_status([item['mainConnected'], item['reportConnected']])
        elif data['type'] == 'location':
            pos = item['position']
            angles = item['angles']
            self.ui.axis_ui.update_joints(angles)
            self.ui.cartesian_ui.update_cartesians(pos)
        elif data['type'] == 'cmdnum':
            cmdnum = item['cmdnum']
            self.ui.update_cmd_count(cmdnum)

    def report_state_callback(self, item):
        self.report_que.put({
            'type': 'state',
            'item': item
        })

    def report_cmdnum_callback(self, item):
        self.report_que.put({
            'type': 'cmdnum',
            'item': item
        })

    def report_connected_callback(self, item):
        self.report_que.put({
            'type': 'connect',
            'item': item
        })

    def report_location_callback(self, item):
        try:
            pos = item['cartesian']
            angles = item['joints']
            location = {
                'position': [float('{:.1f}'.format(p * RAD_DEGREE)) if 2 < i < 6 else float('{:.1f}'.format(p)) for i, p in enumerate(pos)],
                'angles': [float('{:.1f}'.format(angle * RAD_DEGREE)) for angle in angles],
            }
            self.report_que.put({
                'type': 'location',
                'item': location
            })
        except Exception as e:
            print(e)
            pass

    def report_brake_callback(self, item):
        self.report_que.put({
            'type': 'brake',
            'item': item
        })

    def report_warn_error_callback(self, item):
        self.report_que.put({
            'type': 'error',
            'item': item
        })

    def get_servo_debug_msg(self, only_log_error_servo=True):
        if self.ui.main_ui.window.log_window.isHidden():
            self.ui.main_ui.window.log_window.show()
            self.ui.main_ui.logAction.setText('Close-Log')
        try:
            if self.xarm and self.xarm.connected:
                ret = self.xarm.get_servo_debug_msg()
                if ret[0] in [0, x2_config.UX2_ERR_CODE, x2_config.UX2_WAR_CODE]:
                    logger.log('=' * 50)
                    for i in range(1, 8):
                        servo = '机械臂第{}轴'.format(i)
                        log_servo_error(servo, ret[i * 2 - 1], ret[i * 2], only_log_error_servo=only_log_error_servo)
                    log_servo_error('机械爪', ret[15], ret[16], only_log_error_servo=only_log_error_servo)
                    logger.log('=' * 50)
                elif ret[0] == 3:
                    logger.debug('cmd: get_servo_debug_msg, ret: 通信错误')
            else:
                logger.debug('cmd: get_servo_debug_msg, ret: xArm is not connected')
        except Exception as e:
            print(e)

    def init_robot(self):
        global on_init
        with lock:
            on_init = True
        if self.xarm and self.xarm.connected:
            if self.xarm.warn_code != 0:
                logger.debug('clean warn:', self.xarm.clean_warn())
            if self.xarm.error_code != 0:
                logger.debug('clean error:', self.xarm.clean_error())
                time.sleep(0.3)
            logger.debug('motion enable:', self.xarm.motion_enable(enable=True))
            time.sleep(0.5)
            logger.debug('set state:', self.xarm.set_state(0))
            time.sleep(0.2)
            self.xarm.get_version()
            logger.info('xarm_version:', self.xarm.version)
        with lock:
            on_init = False

    def put_cmd_que(self, item):
        self.cmd_que.put(item)





