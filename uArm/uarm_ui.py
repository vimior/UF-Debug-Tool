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
from PyQt5.QtCore import Qt
from PyQt5.Qt import QTabWidget, QFrame, QToolBox, QGroupBox
from PyQt5.Qt import QVBoxLayout, QGridLayout, QHBoxLayout
from PyQt5.Qt import QLabel, QLineEdit, QPushButton, QSpinBox, QSlider, QComboBox, QImage, QPixmap

from .angle_ui import AngleUI
from .coordinate_ui import CoordinateUI
from .handler import UArmHandler

sys.path.append('..')
from log import logger

icon_path = os.path.join(os.path.split(sys.path[0])[0], 'icon')
if not os.path.exists(icon_path):
    icon_path = os.path.join(os.getcwd(), 'icon')

connect_icon_path = os.path.join(icon_path, 'connect.png')
disconnect_icon_path = os.path.join(icon_path, 'disconnect.png')


i18n = {
    'cn': {
        'Connect': '连接',
        'Disconnect': '断开',
        'Connected': '连接状态',
        'Mode': '模式',
        'Type': '类型',
        'HardwareVersion': '硬件版本',
        'FirmwareVersion': '固件版本',
        'Angle': '角度',
        'Coordinate': '坐标',
        'Speed': '速度',
        'Acc': '加速度',
        'Reset': '复位',
        'PumpOn': '打开吸泵',
        'PumpOff': '关闭吸泵',
        'GripperCatch': '合上夹子',
        'GripperRelease': '松开夹子',
        'ServoAttach': '使能电机',
        'ServoDetach': '解锁电机',
        'GetPosition': '获取位置',
        'GetPolar': '获取极坐标',
        'GetServoAngle': '获取电机角度',
        'GetMode': '获取模式',
        'SetMode': '设置模式',
        'GetDeviceInfo': '获取设备信息',
    },
    'en': {
        'Connect': 'Connect',
        'Disconnect': 'Disconnect',
        'Connected': 'Connected',
        'Mode': 'Mode',
        'Type': 'Type',
        'HardwareVersion': 'HardwareVersion',
        'FirmwareVersion': 'FirmwareVersion',
        'Angle': 'Angle',
        'Coordinate': 'Coordinate',
        'Speed': 'Speed',
        'Acc': 'Acc',
        'Reset': 'Reset',
        'PumpOn': 'PumpOn',
        'PumpOff': 'PumpOff',
        'GripperCatch': 'GripperCatch',
        'GripperRelease': 'GripperRelease',
        'ServoAttach': 'ServerAttach',
        'ServoDetach': 'ServerDetach',
        'GetPosition': 'GetPosition',
        'GetPolar': 'GetPolar',
        'GetServoAngle': 'GetServoAngle',
        'GetMode': 'GetMode',
        'SetMode': 'SetMode',
        'GetDeviceInfo': 'GetDeviceInfo',
    }
}


class UArmUI(object):
    def __init__(self, ui, layout):
        self.main_ui = ui
        self.layout = layout
        super(UArmUI, self).__init__()
        self.handler = UArmHandler(self)
        self.lang = self.main_ui.lang
        self.status = 0
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
        common_top_frame.setMaximumHeight(50)
        common_top_layout = QHBoxLayout(common_top_frame)
        top_layout.addWidget(common_top_frame)
        common_top_layout.addStretch(0)

        label = QLabel(i18n[self.lang]['Type'] + ':')
        self.label_type = QLabel('')
        self.label_type.setStyleSheet('''color: gray;font:bold;''')
        common_top_layout.addWidget(label)
        common_top_layout.addWidget(self.label_type)

        label = QLabel(i18n[self.lang]['Mode'] + ':')
        self.label_mode = QLabel('')
        self.label_mode.setStyleSheet('''color: gray;font:bold;''')
        common_top_layout.addWidget(label)
        common_top_layout.addWidget(self.label_mode)

        label = QLabel(i18n[self.lang]['HardwareVersion'] + ':')
        self.label_hard_version = QLabel('')
        self.label_hard_version.setStyleSheet('''color: gray;font:bold;''')
        common_top_layout.addWidget(label)
        common_top_layout.addWidget(self.label_hard_version)

        label = QLabel(i18n[self.lang]['FirmwareVersion'] + ':')
        self.label_firm_version = QLabel('')
        self.label_firm_version.setStyleSheet('''color: gray;font:bold;''')
        common_top_layout.addWidget(label)
        common_top_layout.addWidget(self.label_firm_version)

        label_1 = QLabel(i18n[self.lang]['Connected'] + ':')
        self.label_connected = QLabel()
        img = QImage()
        self.label_connected.setMaximumHeight(20)
        self.label_connected.setMaximumWidth(20)
        self.label_connected.setScaledContents(True)
        if img.load(disconnect_icon_path):
            self.label_connected.setPixmap(QPixmap.fromImage(img))

        self.lnt_addr = QLineEdit('COM12')
        self.lnt_addr.setMaximumWidth(50)
        self.lnt_addr.setMinimumWidth(30)
        self.btn_connect = QPushButton(i18n[self.lang]['Connect'])
        # self.btn_connect.setMaximumWidth(50)

        # common_top_layout.addStretch(0)
        common_top_layout.setSpacing(10)
        common_top_layout.addWidget(label_1)
        common_top_layout.addWidget(self.label_connected)
        common_top_layout.addWidget(self.lnt_addr)
        common_top_layout.addWidget(self.btn_connect)

    def _set_common_down_ui(self):
        slider_frame = QFrame()
        slider_layout = QGridLayout(slider_frame)
        self.layout.addWidget(slider_frame)

        label = QLabel(i18n[self.lang]['Speed'] + ':')
        self.slider_speed = QSlider(Qt.Horizontal)
        self.spinbox_speed = QSpinBox()
        self.slider_speed.setMinimum(1)
        self.slider_speed.setMaximum(100000)
        self.slider_speed.setValue(10000)
        self.spinbox_speed.setSingleStep(1)
        self.spinbox_speed.setMinimum(1)
        self.spinbox_speed.setMaximum(100000)
        self.spinbox_speed.setValue(10000)
        slider_layout.addWidget(label, 0, 0)
        slider_layout.addWidget(self.slider_speed, 0, 1)
        slider_layout.addWidget(self.spinbox_speed, 0, 2)

        # label = QLabel(i18n[self.lang]['Acc'] + ':')
        # self.slider_acc = QSlider(Qt.Horizontal)
        # self.spinbox_acc = QSpinBox()
        # self.slider_acc.setMinimum(1)
        # self.slider_acc.setMaximum(100000)
        # self.slider_acc.setValue(5000)
        # self.spinbox_acc.setSingleStep(1)
        # self.spinbox_acc.setMinimum(1)
        # self.spinbox_acc.setMaximum(100000)
        # self.spinbox_acc.setValue(5000)
        # slider_layout.addWidget(label, 0, 3)
        # slider_layout.addWidget(self.slider_acc, 0, 4)
        # slider_layout.addWidget(self.spinbox_acc, 0, 5)

        btn_frame = QFrame()
        btn_layout = QGridLayout(btn_frame)
        self.layout.addWidget(btn_frame)

        self.btn_get_device_info = QPushButton(i18n[self.lang]['GetDeviceInfo'])
        self.btn_get_position = QPushButton(i18n[self.lang]['GetPosition'])
        self.btn_get_polar = QPushButton(i18n[self.lang]['GetPolar'])
        self.btn_get_servo_angle = QPushButton(i18n[self.lang]['GetServoAngle'])
        self.btn_get_mode = QPushButton(i18n[self.lang]['GetMode'])

        btn_layout.addWidget(self.btn_get_device_info, 0, 0)
        btn_layout.addWidget(self.btn_get_position, 0, 1)
        btn_layout.addWidget(self.btn_get_polar, 0, 2)
        btn_layout.addWidget(self.btn_get_servo_angle, 0, 3)
        btn_layout.addWidget(self.btn_get_mode, 0, 4)

        self.combobox_servo = QComboBox()
        self.combobox_servo.setStyleSheet('''color: blue;''')
        for item in ['axis-1', 'axis-2', 'axis-3', 'axis-all']:
            self.combobox_servo.addItem(item)
        self.combobox_servo.setCurrentIndex(0)
        btn_layout.addWidget(self.combobox_servo, 0, 0)

        self.btn_servo_attach = QPushButton(i18n[self.lang]['ServoAttach'])
        self.btn_servo_detach = QPushButton(i18n[self.lang]['ServoDetach'])
        self.combobox_mode = QComboBox()
        self.combobox_mode.setStyleSheet('''color: blue;''')
        for item in ['normal', 'laser', '3D', 'pen']:
            self.combobox_mode.addItem(item)
            self.combobox_mode.setCurrentIndex(0)
        self.btn_set_mode = QPushButton(i18n[self.lang]['SetMode'])

        btn_layout.addWidget(self.combobox_servo, 1, 0)
        btn_layout.addWidget(self.btn_servo_attach, 1, 1)
        btn_layout.addWidget(self.btn_servo_detach, 1, 2)
        btn_layout.addWidget(self.combobox_mode, 1, 3)
        btn_layout.addWidget(self.btn_set_mode, 1, 4)

        self.btn_reset = QPushButton(i18n[self.lang]['Reset'])
        self.btn_pump_on = QPushButton(i18n[self.lang]['PumpOn'])
        self.btn_pump_off = QPushButton(i18n[self.lang]['PumpOff'])
        self.btn_gripper_catch = QPushButton(i18n[self.lang]['GripperCatch'])
        self.btn_gripper_release = QPushButton(i18n[self.lang]['GripperRelease'])
        btn_layout.addWidget(self.btn_reset, 2, 0)
        btn_layout.addWidget(self.btn_pump_on, 2, 1)
        btn_layout.addWidget(self.btn_pump_off, 2, 2)
        btn_layout.addWidget(self.btn_gripper_catch, 2, 3)
        btn_layout.addWidget(self.btn_gripper_release, 2, 4)

    @staticmethod
    def slider_spinbox_related(value, master=None, slave=None, scale=1):
        try:
            slave.setValue(value * scale)
        except Exception as e:
            print(e)

    def connect_slot(self):
        self.btn_connect.clicked.connect(self.connect)
        self.slider_speed.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_speed, scale=1))
        self.spinbox_speed.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_speed, scale=1))
        # self.slider_acc.valueChanged.connect(
        #     functools.partial(self.slider_spinbox_related, slave=self.spinbox_acc, scale=1))
        # self.spinbox_acc.valueChanged.connect(
        #     functools.partial(self.slider_spinbox_related, slave=self.slider_acc, scale=1))
        self.btn_get_device_info.clicked.connect(self.get_device_info)
        self.btn_get_position.clicked.connect(self.get_position)
        self.btn_get_polar.clicked.connect(self.get_polar)
        self.btn_get_servo_angle.clicked.connect(self.get_servo_angle)
        self.btn_get_mode.clicked.connect(self.get_mode)

        self.btn_servo_attach.clicked.connect(self.set_servo_attach)
        self.btn_servo_detach.clicked.connect(self.set_servo_detach)
        self.btn_set_mode.clicked.connect(self.set_mode)

        self.btn_reset.clicked.connect(self.reset)
        self.btn_pump_on.clicked.connect(self.pump_on)
        self.btn_pump_off.clicked.connect(self.pump_off)
        self.btn_gripper_catch.clicked.connect(self.gripper_catch)
        self.btn_gripper_release.clicked.connect(self.gripper_release)

    def reset_flag(self):
        self.cartesian_ui.reset_flag()
        self.axis_ui.reset_flag()

    def update_connect_status(self, item):
        try:
            img = QImage()
            if item and self.status != 1:
                self.status = 1
                logger.info('connect to {} success'.format(self.handler.port))
                if img.load(connect_icon_path):
                    self.label_connected.setPixmap(QPixmap.fromImage(img))
                    self.btn_connect.setText(i18n[self.lang]['Disconnect'])
                    self.btn_connect.setStyleSheet('''color: red;font:bold;''')
                self.set_disable(False)
            elif not item and self.status != 0:
                self.status = 0
                logger.info('disconnect from {0} or failed connect {0}'.format(self.handler.port))
                self.handler.cmd_que.queue.clear()
                if img.load(disconnect_icon_path):
                    self.label_connected.setPixmap(QPixmap.fromImage(img))
                    self.btn_connect.setText(i18n[self.lang]['Connect'])
                    self.btn_connect.setStyleSheet('''color: green;font:bold;''')
                self.set_disable(True)
        except Exception as e:
            print(e)

    def connect(self):
        try:
            if str(self.btn_connect.text()) == i18n[self.lang]['Connect']:
                addr = self.lnt_addr.text().strip()
                if addr == 'auto':
                    addr = None
                self.btn_connect.setText('Connecting')
                self.status = 2
                self.btn_connect.setStyleSheet('''color: orange;font:bold;''')
                self.handler.connect(addr)
                # if self.window.connect(addr, report_type=report_type):
                #     self.btn_connect.setText(self.disconnect_label)
                #     self.btn_connect.setStyleSheet('''color: red;font:bold;''')
            elif str(self.btn_connect.text()) == i18n[self.lang]['Disconnect']:
                self.handler.disconnect()
                self.btn_connect.setText(i18n[self.lang]['Connect'])
                self.btn_connect.setStyleSheet('''color: green;font:bold;''')
        except Exception as e:
            print(e)

    def get_device_info(self, event):
        try:
            item = {
                'cmd': 'get_device_info',
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def get_mode(self, event):
        try:
            item = {
                'cmd': 'get_mode',
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def get_position(self, event):
        try:
            item = {
                'cmd': 'get_position',
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def get_polar(self, event):
        try:
            item = {
                'cmd': 'get_polar',
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def get_servo_angle(self, event):
        try:
            item = {
                'cmd': 'get_servo_angle',
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_servo_attach(self, event):
        try:
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                servo_id = None
            else:
                servo_id = int(self.combobox_servo.currentIndex())
            item = {
                'cmd': 'set_servo_attach',
                'kwargs': {
                    'servo_id': servo_id
                }
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_servo_detach(self, event):
        try:
            text = self.combobox_servo.currentText()
            if text == 'axis-all':
                servo_id = None
            else:
                servo_id = int(self.combobox_servo.currentIndex())
            item = {
                'cmd': 'set_servo_detach',
                'kwargs': {
                    'servo_id': servo_id
                }
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def pump_on(self, event):
        try:
            item = {
                'cmd': 'set_pump',
                'kwargs': {
                    'on': True
                }
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def pump_off(self, event):
        try:
            item = {
                'cmd': 'set_pump',
                'kwargs': {
                    'on': False
                }
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def gripper_catch(self, event):
        try:
            item = {
                'cmd': 'set_gripper',
                'kwargs': {
                    'catch': True
                }
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def gripper_release(self, event):
        try:
            item = {
                'cmd': 'set_gripper',
                'kwargs': {
                    'catch': False
                }
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_mode(self, event):
        try:
            mode = self.combobox_mode.currentIndex()
            item = {
                'cmd': 'set_mode',
                'kwargs': {
                    'mode': int(mode)
                }
            }
            self.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def reset(self, event):
        try:
            self.handler.cmd_que.queue.clear()
            item = {
                'cmd': 'reset',
                'kwargs': {
                    'speed': self.spinbox_speed.value(),
                    'wait': False,
                }
            }
            self.handler.put_cmd_que(item)
            self.reset_flag()
        except Exception as e:
            print(e)

    @staticmethod
    def slider_spinbox_related(value, master=None, slave=None, scale=1):
        try:
            slave.setValue(value * scale)
        except Exception as e:
            print(e)

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

        tab_widget.addTab(toolBox1, i18n[self.lang]['Angle'])
        tab_widget.addTab(toolBox2, i18n[self.lang]['Coordinate'])

        joint_layout = QVBoxLayout(groupBox1)
        cartesian_layout = QVBoxLayout(groupBox2)

        self.cartesian_ui = CoordinateUI(self, cartesian_layout)
        self.axis_ui = AngleUI(self, joint_layout)

    def update_device_info(self, device_info):
        if device_info is not None:
            self.label_type.setText(str(device_info.get('device_type', None)))
            self.label_hard_version.setText(str(device_info.get('hardware_version', None)))
            self.label_firm_version.setText(str(device_info.get('firmware_version', None)))

    def update_mode(self, mode):
        if mode is not None:
            if mode == 0:
                mode_str = 'Normal'
            elif mode == 1:
                mode_str = 'Laser'
            elif mode == 2:
                mode_str = '3D'
            elif mode == 3:
                mode_str = 'Pen'
            else:
                mode_str = self.label_mode.text()
            self.label_mode.setText(mode_str)

    def set_disable(self, disable):
        try:
            self.btn_get_device_info.setDisabled(disable)
            self.btn_get_position.setDisabled(disable)
            self.btn_get_polar.setDisabled(disable)
            self.btn_get_servo_angle.setDisabled(disable)
            self.btn_get_mode.setDisabled(disable)
            self.combobox_servo.setDisabled(disable)
            self.combobox_mode.setDisabled(disable)
            self.btn_servo_attach.setDisabled(disable)
            self.btn_servo_detach.setDisabled(disable)
            self.btn_reset.setDisabled(disable)
            self.btn_pump_on.setDisabled(disable)
            self.btn_pump_off.setDisabled(disable)
            self.btn_gripper_catch.setDisabled(disable)
            self.btn_gripper_release.setDisabled(disable)

            self.slider_speed.setDisabled(disable)
            self.spinbox_speed.setDisabled(disable)
            # self.slider_acc.setDisabled(disable)
            # self.spinbox_acc.setDisabled(disable)

            self.axis_ui.set_disable(disable)
            self.cartesian_ui.set_disable(disable)
        except Exception as e:
            print(e)
