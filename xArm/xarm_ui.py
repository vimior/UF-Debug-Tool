#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import functools
import os
import sys
import threading
import time
from PyQt5.QtCore import Qt
from PyQt5.Qt import QWidget, QTabWidget, QFrame, QMenuBar, QToolBox, QGroupBox, QMessageBox
from PyQt5.Qt import QVBoxLayout, QGridLayout, QHBoxLayout, QBoxLayout
from PyQt5.Qt import QAction, QLabel, QLineEdit, QPushButton, QSpinBox, QSlider, QComboBox, QImage, QPixmap

from .joint_ui import JointUI
from .cartesian_ui import CartesianUI
from .handler import XArmHandler

sys.path.append('..')
from log import logger


path = os.path.join(os.path.split(sys.path[0])[0], 'icon')
if not os.path.exists(path):
    path = os.path.join(os.getcwd(), 'icon')

connect_icon_path = os.path.join(path, 'connect.png')
disconnect_icon_path = os.path.join(path, 'disconnect.png')

i18n = {
    'cn': {
        'Connect': '连接',
        'Disconnect': '断开',
        'Connected': '连接状态',
        'Reported': '上报状态',
        'WarnCode': '警告码',
        'ErrorCode': '错误码',
        'CmdCount': '指令数量',
        'State': '运动状态',
        'Maable': '使能状态',
        'Mtbrake': '抱闸状态',
        'Joint': '关节',
        'Cartesian': '笛卡尔',
        'Speed': '速度',
        'Acc': '加速度',
        'MotionEnable': '使能电机',
        'MotionDisable': '关闭电机',
        'ServoAttach': '关闭抱闸',
        'ServoDetach': '使能抱闸',
        'SetState': '设置状态',
        'CleanErrorWarn': '清除错误和警告',
        'Stop': '停止运动',
        'Reset': '复位',
        'GetServoAddr16': 'GetServoAddr16',
        'SetServoAddr16': 'SetServoAddr16',
        'GetServoAddr32': 'GetServoAddr32',
        'SetServoAddr32': 'SetServoAddr32',
        'SetServoZero': 'SetServoZero',
        'GetServoDebugMsg': 'GetServoDebugMsg',
    },
    'en': {
        'Connect': 'Connect',
        'Disconnect': 'Disconnect',
        'Connected': 'Connected',
        'Reported': 'Reported',
        'WarnCode': 'WarnCode',
        'ErrorCode': 'ErrorCode',
        'CmdCount': 'CmdCount',
        'State': 'State',
        'Maable': 'Maable',
        'Mtbrake': 'Mtbrake',
        'Joint': 'Joint',
        'Cartesian': 'Cartesian',
        'Speed': 'Speed',
        'Acc': 'Acc',
        'MotionEnable': 'MotionEnable',
        'MotionDisable': 'MotionDisable',
        'ServoAttach': 'ServoAttach',
        'ServoDetach': 'ServoDetach',
        'SetState': 'SetState',
        'CleanErrorWarn': 'CleanErrorWarn',
        'Stop': 'Stop',
        'Reset': 'Reset',
        'GetServoAddr16': 'GetServoAddr16',
        'SetServoAddr16': 'SetServoAddr16',
        'GetServoAddr32': 'GetServoAddr32',
        'SetServoAddr32': 'SetServoAddr32',
        'SetServoZero': 'SetServoZero',
        'GetServoDebugMsg': 'GetServoDebugMsg',
    }
}


class XArmUI(object):
    def __init__(self, ui, layout):
        self.main_ui = ui
        self.layout = layout
        super(XArmUI, self).__init__()
        self.handler = XArmHandler(self)
        self.lang = self.main_ui.lang
        self.set_ui()
        self.set_disable(True)

    def set_ui(self):
        self._set_common_top_ui()
        self._set_tab()
        self._set_common_down_ui()
        self.connect_slot()

    def _set_common_top_ui(self):
        top_frame = QFrame()
        top_frame.setMaximumHeight(60)
        top_layout = QVBoxLayout(top_frame)
        self.layout.addWidget(top_frame)

        common_top_frame = QFrame()
        common_top_frame.setMinimumHeight(50)
        common_top_layout = QHBoxLayout(common_top_frame)
        top_layout.addWidget(common_top_frame)

        label_1 = QLabel(i18n[self.lang]['Connected'] + ':')
        self.label_connected = QLabel()
        img = QImage()
        self.label_connected.setMaximumHeight(20)
        self.label_connected.setMaximumWidth(20)
        self.label_connected.setScaledContents(True)
        if img.load(disconnect_icon_path):
            self.label_connected.setPixmap(QPixmap.fromImage(img))

        label_2 = QLabel(i18n[self.lang]['Reported'] + ':')
        self.label_reported = QLabel()
        img = QImage()
        self.label_reported.setMaximumHeight(20)
        self.label_reported.setMaximumWidth(20)
        self.label_reported.setScaledContents(True)
        if img.load(disconnect_icon_path):
            self.label_reported.setPixmap(QPixmap.fromImage(img))

        self.lnt_addr = QLineEdit('192.168.1.182')
        self.lnt_addr.setMaximumWidth(100)
        self.lnt_addr.setMinimumWidth(60)
        self.btn_connect = QPushButton(i18n[self.lang]['Connect'])
        # self.btn_connect.setMaximumWidth(50)

        # common_top_layout.addStretch(0)
        common_top_layout.setSpacing(10)
        common_top_layout.addWidget(label_1)
        common_top_layout.addWidget(self.label_connected)
        common_top_layout.addWidget(label_2)
        common_top_layout.addWidget(self.label_reported)
        common_top_layout.addWidget(self.lnt_addr)
        common_top_layout.addWidget(self.btn_connect)

        # common_down_frame = QFrame()
        # common_down_layout = QHBoxLayout(common_down_frame)
        # common_down_layout.setSpacing(0)
        # top_layout.addWidget(common_down_frame)
        common_down_layout = common_top_layout

        label = QLabel(i18n[self.lang]['WarnCode'] + ':')
        self.label_warn_code = QLabel('0')
        self.label_warn_code.setStyleSheet('''color: gray;font:bold;''')
        common_down_layout.addWidget(label)
        common_down_layout.addWidget(self.label_warn_code)

        label = QLabel(i18n[self.lang]['ErrorCode'] + ':')
        self.label_error_code = QLabel('0')
        self.label_error_code.setStyleSheet('''color: gray;font:bold;''')
        common_down_layout.addWidget(label)
        common_down_layout.addWidget(self.label_error_code)

        label = QLabel(i18n[self.lang]['CmdCount'] + ':')
        self.label_cmd_count = QLabel('0')
        self.label_cmd_count.setStyleSheet('''color: gray;font:bold;''')
        common_down_layout.addWidget(label)
        common_down_layout.addWidget(self.label_cmd_count)

        label = QLabel(i18n[self.lang]['State'] + ':')
        self.label_state = QLabel('4')
        self.label_state.setStyleSheet('''color: gray;font:bold;''')
        common_down_layout.addWidget(label)
        common_down_layout.addWidget(self.label_state)

        label = QLabel(i18n[self.lang]['Maable'] + ':')
        self.label_maable = QLabel('128')
        self.label_maable.setStyleSheet('''color: gray;font:bold;''')
        common_down_layout.addWidget(label)
        common_down_layout.addWidget(self.label_maable)

        label = QLabel(i18n[self.lang]['Mtbrake'] + ':')
        self.label_mtbrake = QLabel('128')
        self.label_mtbrake.setStyleSheet('''color: gray;font:bold;''')
        common_down_layout.addWidget(label)
        common_down_layout.addWidget(self.label_mtbrake)

    def _set_tab(self):
        tab_widget = QTabWidget()
        tab_widget.setMaximumHeight(self.main_ui.window.geometry().height() // 2)
        self.layout.addWidget(tab_widget)

        toolBox1 = QToolBox()
        toolBox2 = QToolBox()

        groupBox1 = QGroupBox()
        groupBox2 = QGroupBox()

        toolBox1.addItem(groupBox1, "")
        toolBox2.addItem(groupBox2, "")

        tab_widget.addTab(toolBox1, i18n[self.lang]['Joint'])
        tab_widget.addTab(toolBox2, i18n[self.lang]['Cartesian'])

        joint_layout = QVBoxLayout(groupBox1)
        cartesian_layout = QVBoxLayout(groupBox2)

        self.cartesian_ui = CartesianUI(self, cartesian_layout)
        self.axis_ui = JointUI(self, joint_layout)

    def _set_common_down_ui(self):
        slider_frame = QFrame()
        slider_layout = QGridLayout(slider_frame)
        self.layout.addWidget(slider_frame)

        label = QLabel(i18n[self.lang]['Speed'] + ':')
        self.slider_speed = QSlider(Qt.Horizontal)
        self.spinbox_speed = QSpinBox()
        self.slider_speed.setMinimum(1)
        self.slider_speed.setMaximum(1000)
        self.slider_speed.setValue(50)
        self.spinbox_speed.setSingleStep(1)
        self.spinbox_speed.setMinimum(1)
        self.spinbox_speed.setMaximum(1000)
        self.spinbox_speed.setValue(50)
        slider_layout.addWidget(label, 0, 0)
        slider_layout.addWidget(self.slider_speed, 0, 1)
        slider_layout.addWidget(self.spinbox_speed, 0, 2)

        label = QLabel(i18n[self.lang]['Acc'] + ':')
        self.slider_acc = QSlider(Qt.Horizontal)
        self.spinbox_acc = QSpinBox()
        self.slider_acc.setMinimum(1)
        self.slider_acc.setMaximum(100000)
        self.slider_acc.setValue(5000)
        self.spinbox_acc.setSingleStep(1)
        self.spinbox_acc.setMinimum(1)
        self.spinbox_acc.setMaximum(100000)
        self.spinbox_acc.setValue(5000)
        slider_layout.addWidget(label, 0, 3)
        slider_layout.addWidget(self.slider_acc, 0, 4)
        slider_layout.addWidget(self.spinbox_acc, 0, 5)

        common_frame = QFrame()
        common_layout = QGridLayout(common_frame)
        self.layout.addWidget(common_frame)

        self.btn_stop = QPushButton(i18n[self.lang]['Stop'])
        self.btn_clean = QPushButton(i18n[self.lang]['CleanErrorWarn'])
        self.btn_reset = QPushButton(i18n[self.lang]['Reset'])
        self.btn_get_servo_dbmsg = QPushButton(i18n[self.lang]['GetServoDebugMsg'])

        common_layout.addWidget(self.btn_stop, 0, 0)
        common_layout.addWidget(self.btn_clean, 0, 2)
        common_layout.addWidget(self.btn_reset, 0, 3)
        common_layout.addWidget(self.btn_get_servo_dbmsg, 0, 4)

        btn_frame = QFrame()
        btn_layout = QGridLayout(btn_frame)
        self.layout.addWidget(btn_frame)

        self.combobox_servo = QComboBox()
        self.combobox_servo.setStyleSheet('''color: blue;''')
        for item in ['axis-all', 'axis-1', 'axis-2', 'axis-3', 'axis-4', 'axis-5', 'axis-6', 'axis-7']:
            self.combobox_servo.addItem(item)
        self.combobox_servo.setCurrentIndex(1)
        btn_layout.addWidget(self.combobox_servo, 0, 0)

        self.btn_motion_enable = QPushButton(i18n[self.lang]['MotionEnable'])
        self.btn_motion_disable = QPushButton(i18n[self.lang]['MotionDisable'])
        self.btn_servo_attach = QPushButton(i18n[self.lang]['ServoAttach'])
        self.btn_servo_detach = QPushButton(i18n[self.lang]['ServoDetach'])

        self.combobox_state = QComboBox()
        self.combobox_state.setStyleSheet('''color: blue;''')
        for item in ['sport', 'pause', 'stop']:
            self.combobox_state.addItem(item)
            self.combobox_state.setCurrentIndex(0)
        self.btn_set_state = QPushButton(i18n[self.lang]['SetState'])

        btn_layout.addWidget(self.btn_motion_enable, 0, 1)
        btn_layout.addWidget(self.btn_motion_disable, 0, 2)
        btn_layout.addWidget(self.btn_servo_attach, 0, 3)
        btn_layout.addWidget(self.btn_servo_detach, 0, 4)
        btn_layout.addWidget(self.combobox_state, 0, 5)
        btn_layout.addWidget(self.btn_set_state, 0, 6)

        self.lnt_servo_addr = QLineEdit('servo_addr')
        self.lnt_servo_addr_value = QLineEdit('value')
        self.btn_get_servo_addr16 = QPushButton(i18n[self.lang]['GetServoAddr16'])
        self.btn_set_servo_addr16 = QPushButton(i18n[self.lang]['SetServoAddr16'])
        self.btn_get_servo_addr32 = QPushButton(i18n[self.lang]['GetServoAddr32'])
        self.btn_set_servo_addr32 = QPushButton(i18n[self.lang]['SetServoAddr32'])
        self.btn_set_servo_zero = QPushButton(i18n[self.lang]['SetServoZero'])

        btn_layout.addWidget(self.lnt_servo_addr, 1, 0)
        btn_layout.addWidget(self.lnt_servo_addr_value, 1, 1)
        btn_layout.addWidget(self.btn_get_servo_addr16, 1, 2)
        btn_layout.addWidget(self.btn_set_servo_addr16, 1, 3)
        btn_layout.addWidget(self.btn_get_servo_addr32, 1, 4)
        btn_layout.addWidget(self.btn_set_servo_addr32, 1, 5)
        btn_layout.addWidget(self.btn_set_servo_zero, 1, 6)

    def connect_slot(self):
        self.btn_connect.clicked.connect(self.connect)
        self.slider_speed.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_speed, scale=1))
        self.spinbox_speed.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_speed, scale=1))
        self.slider_acc.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_acc, scale=1))
        self.spinbox_acc.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_acc, scale=1))
        self.btn_stop.clicked.connect(self.stop)
        self.btn_clean.clicked.connect(self.clean)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_get_servo_dbmsg.clicked.connect(
            functools.partial(self.handler.get_servo_debug_msg, only_log_error_servo=False))
        self.btn_motion_enable.clicked.connect(self.motion_enable)
        self.btn_motion_disable.clicked.connect(self.motion_disable)
        self.btn_servo_attach.clicked.connect(self.set_servo_attach)
        self.btn_servo_detach.clicked.connect(self.set_servo_detach)
        self.btn_set_state.clicked.connect(self.set_state)
        self.btn_get_servo_addr16.clicked.connect(self.get_servo_addr_16)
        self.btn_set_servo_addr16.clicked.connect(self.set_servo_addr_16)
        self.btn_get_servo_addr32.clicked.connect(self.get_servo_addr_32)
        self.btn_set_servo_addr32.clicked.connect(self.set_servo_addr_32)
        self.btn_set_servo_zero.clicked.connect(self.set_servo_zero)

    @staticmethod
    def slider_spinbox_related(value, master=None, slave=None, scale=1):
        try:
            slave.setValue(value * scale)
        except Exception as e:
            print(e)

    def reset_flag(self):
        self.cartesian_ui.reset_flag()
        self.axis_ui.reset_flag()

    def update_maable_mtbrake(self, maable, mtbrake):
        try:
            self.label_maable.setText(str(maable))
            self.label_mtbrake.setText(str(mtbrake))
            self.label_maable.setStyleSheet('''color: green;font:bold;''')
            self.label_mtbrake.setStyleSheet('''color: green;font:bold;''')
        except Exception as e:
            print(e)

    def update_cmd_count(self, cmdnum):
        try:
            self.label_cmd_count.setText(str(cmdnum))
            self.label_cmd_count.setStyleSheet('''color: green;font:bold;''')
        except Exception as e:
            print(e)

    def update_state(self, state):
        try:
            if state == 1:
                state_str = 'sport'
                self.label_state.setText(state_str)
                self.label_state.setStyleSheet('''color: green;font:bold;''')
            elif state == 2:
                state_str = 'sleep'
                self.label_state.setText(state_str)
                self.label_state.setStyleSheet('''color: gray;font:bold;''')
            elif state == 3:
                state_str = 'pause'
                self.label_state.setText(state_str)
                self.label_state.setStyleSheet('''color: orange;font:bold;''')
            elif state == 4:
                state_str = 'stop'
                self.label_state.setText(state_str)
                self.label_state.setStyleSheet('''color: red;font:bold;''')
        except Exception as e:
            print(e)
        # getattr(self, 'label_state').setText(state_str)
        # getattr(self, 'label_state').setText(str(state))
        if state != 1:
            self.reset_flag()

    def update_warn_error(self, item):
        try:
            warn, error = item
            self.label_warn_code.setText(str(warn))
            self.label_error_code.setText(str(error))
            if warn != 0:
                self.label_warn_code.setStyleSheet('''color: red;font:bold;''')
            else:
                self.label_warn_code.setStyleSheet('''color: green;font:bold;''')
            if error != 0:
                self.label_error_code.setStyleSheet('''color: red;font:bold;''')
            else:
                self.label_error_code.setStyleSheet('''color: green;font:bold;''')
        except Exception as e:
            print(e)

    def update_connect_status(self, item):
        try:
            img = QImage()
            if item[0]:
                logger.info(
                    'connect to {} success, report: {}'.format(self.handler.addr, self.handler.report_type))
                if img.load(connect_icon_path):
                    self.label_connected.setPixmap(QPixmap.fromImage(img))
                    self.btn_connect.setText(i18n[self.lang]['Disconnect'])
                    self.btn_connect.setStyleSheet('''color: red;font:bold;''')
                self.set_disable(False)
            else:
                logger.info('disconnect from or failed connect {}'.format(self.handler.addr))
                self.handler.cmd_que.queue.clear()
                if img.load(disconnect_icon_path):
                    self.label_connected.setPixmap(QPixmap.fromImage(img))
                    self.btn_connect.setText(i18n[self.lang]['Connect'])
                    self.btn_connect.setStyleSheet('''color: green;font:bold;''')
                self.set_disable(True)
            if item[1]:
                if img.load(connect_icon_path):
                    self.label_reported.setPixmap(QPixmap.fromImage(img))
            else:
                if img.load(disconnect_icon_path):
                    self.label_reported.setPixmap(QPixmap.fromImage(img))
        except Exception as e:
            print(e)

    def connect(self, event):
        try:
            if str(self.btn_connect.text()) == i18n[self.lang]['Connect']:
                addr = self.lnt_addr.text().strip()
                if addr == '192.168.1.':
                    addr = 'localhost'
                    report_type = 'normal'
                else:
                    tmp = addr.split(':')
                    addr = tmp[0]
                    report_type = tmp[1] if len(tmp) > 1 else 'normal'
                self.btn_connect.setText('Connecting')
                self.btn_connect.setStyleSheet('''color: orange;font:bold;''')
                self.handler.connect(addr, report_type=report_type)
                # if self.window.connect(addr, report_type=report_type):
                #     self.btn_connect.setText(self.disconnect_label)
                #     self.btn_connect.setStyleSheet('''color: red;font:bold;''')
            elif str(self.btn_connect.text()) == i18n[self.lang]['Disconnect']:
                self.handler.disconnect()
                self.btn_connect.setText(i18n[self.lang]['Connect'])
                self.btn_connect.setStyleSheet('''color: green;font:bold;''')
        except Exception as e:
            print(e)

    def stop(self, event):
        try:
            self.handler.cmd_que.queue.clear()
            if self.handler.xarm and self.handler.xarm.warn_code != 0:
                item = {
                    'cmd': 'clean_warn',
                }
                self.handler.put_cmd_que(item)
            if self.handler.xarm and self.handler.xarm.error_code != 0:
                item = {
                    'cmd': 'clean_error',
                }
                self.handler.put_cmd_que(item)
                item = {
                    'cmd': 'motion_enable',
                    'kwargs': {
                        'servo_id': 0,
                        'enable': True
                    }
                }
                self.handler.put_cmd_que(item)
            item = {
                'cmd': 'urgent_stop',
            }
            self.handler.put_cmd_que(item)
            self.reset_flag()
        except Exception as e:
            print(e)

    def clean(self, event):
        try:
            self.handler.cmd_que.queue.clear()
            if self.handler.xarm and self.handler.xarm.warn_code != 0:
                item = {
                    'cmd': 'clean_warn',
                }
                self.handler.put_cmd_que(item)
            if self.handler.xarm and self.handler.xarm.error_code != 0:
                item = {
                    'cmd': 'clean_error',
                }
                self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def reset(self, event):
        try:
            self.handler.cmd_que.queue.clear()
            if self.handler.xarm and self.handler.xarm.warn_code != 0:
                item = {
                    'cmd': 'clean_warn',
                }
                self.handler.put_cmd_que(item)
            if self.handler.xarm and self.handler.xarm.error_code != 0:
                item = {
                    'cmd': 'clean_error',
                }
                self.handler.put_cmd_que(item)
                item = {
                    'cmd': 'motion_enable',
                    'kwargs': {
                        'servo_id': 0,
                        'enable': True
                    }
                }
                self.handler.put_cmd_que(item)
                item = {
                    'cmd': 'set_state',
                    'kwargs': {
                        'state': 0
                    }
                }
                self.handler.put_cmd_que(item)
            item = {
                'cmd': 'move_gohome',
                'kwargs': {
                    'speed': 30,
                    'mvacc': 5000,
                }
            }
            self.handler.put_cmd_que(item)
            self.reset_flag()
        except Exception as e:
            print(e)

    def get_servo_addr_16(self, event):
        try:
            addr = self.lnt_servo_addr.text().strip()
            try:
                if addr.lower().startswith('0x'):
                    addr = int(addr, base=16)
                else:
                    addr = int(addr)
            except:
                QMessageBox.warning(self.main_ui.window, '错误', '请输入正确的地址， 地址必须是u16类型')
                return
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                QMessageBox.warning(self.main_ui.window, '警告', '请选择其中一个电机，不能选择所有电机')
                return
            else:
                servo_id = int(text.split('-')[-1])
            tmp = '你确定要获取电机{}的地址{}的值吗？'.format(servo_id, addr)
            if QMessageBox.question(self.main_ui.window, '警告', tmp) == QMessageBox.Yes:
                item = {
                    'cmd': 'get_servo_addr_16',
                    'kwargs': {
                        'servo_id': servo_id,
                        'addr': addr
                    }
                }
                self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def get_servo_addr_32(self, event):
        try:
            addr = self.lnt_servo_addr.text().strip()
            try:
                if addr.lower().startswith('0x'):
                    addr = int(addr, base=16)
                else:
                    addr = int(addr)
            except:
                QMessageBox.warning(self.main_ui.window, '错误', '请输入正确的地址， 地址必须是u16类型')
                return
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                QMessageBox.warning(self.main_ui.window, '警告', '请选择其中一个电机，不能选择所有电机')
                return
            else:
                servo_id = int(text.split('-')[-1])
            tmp = '你确定要获取电机{}的地址{}的值吗？'.format(servo_id, addr)
            if QMessageBox.question(self.main_ui.window, '警告', tmp) == QMessageBox.Yes:
                item = {
                    'cmd': 'get_servo_addr_32',
                    'kwargs': {
                        'servo_id': servo_id,
                        'addr': addr
                    }
                }
                self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_servo_addr_16(self, event):
        try:
            addr = self.lnt_servo_addr.text().strip()
            try:
                if addr.lower().startswith('0x'):
                    addr = int(addr, base=16)
                else:
                    addr = int(addr)
            except:
                QMessageBox.warning(self.main_ui.window, '错误', '请输入正确的地址， 地址必须是u16类型')
                return
            value = self.lnt_servo_addr_value.text().strip()
            try:
                value = float(value)
            except:
                QMessageBox.warning(self.main_ui.window, '错误', '请输入正确的值， 值必须是float32类型')
                return
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                QMessageBox.warning(self.main_ui.window, '警告', '请选择其中一个电机，不能选择所有电机')
                return
            else:
                servo_id = int(text.split('-')[-1])
            tmp = '你确定要设置电机{}的地址{}的值为{}吗？'.format(servo_id, addr, value)
            if QMessageBox.question(self.main_ui.window, '警告', tmp) == QMessageBox.Yes:
                item = {
                    'cmd': 'set_servo_addr_16',
                    'kwargs': {
                        'servo_id': servo_id,
                        'addr': addr,
                        'value': value
                    }
                }
                self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_servo_addr_32(self, event):
        try:
            addr = self.lnt_servo_addr.text().strip()
            try:
                if addr.lower().startswith('0x'):
                    addr = int(addr, base=16)
                else:
                    addr = int(addr)
            except:
                QMessageBox.warning(self.main_ui.window, '错误', '请输入正确的地址， 地址必须是u16类型')
                return
            value = self.lnt_servo_addr_value.text().strip()
            try:
                value = float(value)
            except:
                QMessageBox.warning(self.main_ui.window, '错误', '请输入正确的值， 值必须是float32类型')
                return
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                QMessageBox.warning(self.main_ui.window, '警告', '请选择其中一个电机，不能选择所有电机')
                return
            else:
                servo_id = int(text.split('-')[-1])

            tmp = '你确定要设置电机{}的地址{}的值为{}吗？'.format(servo_id, addr, value)
            if QMessageBox.question(self.main_ui.window, '警告', tmp) == QMessageBox.Yes:
                item = {
                    'cmd': 'set_servo_addr_32',
                    'kwargs': {
                        'servo_id': servo_id,
                        'addr': addr,
                        'value': value
                    }
                }
                self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_servo_zero(self, event):
        try:
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                servo_id = 8
            else:
                servo_id = int(text.split('-')[-1])
            if servo_id == 8:
                tmp = '你确定要设置所有电机的零点吗？'
            else:
                tmp = '你确定要设置电机{}的零点吗？'.format(servo_id)
            if QMessageBox.question(self.main_ui.window, '警告', tmp) == QMessageBox.Yes:
                item = {
                    'cmd': 'set_servo_zero',
                    'kwargs': {
                        'servo_id': servo_id
                    }
                }
                self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_servo_attach(self, event):
        try:
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                servo_id = 8
            else:
                servo_id = int(text.split('-')[-1])

            item = {
                'cmd': 'set_servo_attach',
                'kwargs': {
                    'servo_id': servo_id
                }
            }
            self.handler.put_cmd_que(item)
            item = {
                'cmd': 'motion_enable',
                'kwargs': {
                    'servo_id': servo_id,
                    'enable': True
                }
            }
            self.handler.put_cmd_que(item)
            item = {
                'cmd': 'set_state',
                'kwargs': {
                    'state': 0
                }
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_servo_detach(self, event):
        try:
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                servo_id = 8
            else:
                servo_id = int(text.split('-')[-1])

            if servo_id == 8:
                tmp = '你确定要解锁所有电机吗？'
            else:
                tmp = '你确定要解锁电机{}吗？'.format(servo_id)
            if QMessageBox.question(self.main_ui.window, '警告', tmp) == QMessageBox.Yes:
                item = {
                    'cmd': 'set_servo_detach',
                    'kwargs': {
                        'servo_id': servo_id
                    }
                }
                self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def motion_enable(self, event):
        self._motion_enable(True)

    def motion_disable(self, event):
        self._motion_enable(False)

    def _motion_enable(self, enable=True):
        try:
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                servo_id = 8
            else:
                servo_id = int(text.split('-')[-1])
            item = {
                'cmd': 'motion_enable',
                'kwargs': {
                    'servo_id': servo_id,
                    'enable': enable
                }
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_state(self, event):
        try:
            text = self.combobox_state.currentText()
            if text == 'sport':
                state = 0
            elif text == 'pause':
                state = 3
            elif text == 'stop':
                state = 4
            else:
                return
            if state in [0, 3, 4]:
                item = {
                    'cmd': 'set_state',
                    'kwargs': {
                        'state': state
                    }
                }
                self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_disable(self, disable):
        try:
            self.btn_stop.setDisabled(disable)
            self.btn_clean.setDisabled(disable)
            self.btn_reset.setDisabled(disable)
            self.btn_get_servo_dbmsg.setDisabled(disable)
            self.combobox_servo.setDisabled(disable)
            self.combobox_state.setDisabled(disable)
            self.btn_motion_enable.setDisabled(disable)
            self.btn_motion_disable.setDisabled(disable)
            self.btn_servo_attach.setDisabled(disable)
            self.btn_servo_detach.setDisabled(disable)
            self.btn_set_state.setDisabled(disable)
            self.lnt_servo_addr.setDisabled(disable)
            self.lnt_servo_addr_value.setDisabled(disable)
            self.btn_get_servo_addr16.setDisabled(disable)
            self.btn_set_servo_addr16.setDisabled(disable)
            self.btn_get_servo_addr32.setDisabled(disable)
            self.btn_set_servo_addr32.setDisabled(disable)
            self.btn_set_servo_zero.setDisabled(disable)

            self.slider_speed.setDisabled(disable)
            self.spinbox_speed.setDisabled(disable)
            self.slider_acc.setDisabled(disable)
            self.spinbox_acc.setDisabled(disable)

            self.axis_ui.set_disable(disable)
            self.cartesian_ui.set_disable(disable)
        except Exception as e:
            print(e)

