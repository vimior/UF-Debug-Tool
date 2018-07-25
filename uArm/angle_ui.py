#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import threading
import functools
from PyQt5.QtCore import Qt
from PyQt5.Qt import QFrame, QGridLayout, QSlider, QDoubleSpinBox, QLabel, QMessageBox


class AngleUI(object):
    def __init__(self, ui, layout):
        self.main_ui = ui
        self.p_layout = layout
        super(AngleUI, self).__init__()
        self.joints = [
            {'name': 'servo_0', 'default': 90.0, 'range': [0, 180]},
            {'name': 'servo_1', 'default': 101.08, 'range': [0, 180]},
            {'name': 'servo_2', 'default': 7.76, 'range': [0, 90]},
            {'name': 'servo_3', 'default': 90.0, 'range': [0, 180]},
        ]
        self.flag_lock = threading.Lock()
        self.joints_flag = [False] * 7
        self.set_ui()

    def set_ui(self):
        self._set_ui()

    def _set_ui(self):
        frame = QFrame()
        layout = QGridLayout(frame)
        self.p_layout.addWidget(frame)

        for i, joint in enumerate(self.joints):
            label = QLabel('Servo-'+str(i)+':')
            setattr(self, 'slider_{}'.format(joint['name']), QSlider(Qt.Horizontal))
            setattr(self, 'spinbox_{}'.format(joint['name']), QDoubleSpinBox())
            slider = getattr(self, 'slider_{}'.format(joint['name']))
            spinbox = getattr(self, 'spinbox_{}'.format(joint['name']))
            slider.setMinimum(joint['range'][0] * 10)
            slider.setMaximum(joint['range'][1] * 10)
            slider.setValue(joint['default'] * 10)
            spinbox.setDecimals(1)
            spinbox.setSingleStep(0.1)
            spinbox.setMinimum(joint['range'][0])
            spinbox.setMaximum(joint['range'][1])
            spinbox.setValue(joint['default'])

            slider.mouseReleaseEvent = functools.partial(self.set_servo_angle, index=i, source=slider.mouseReleaseEvent)
            spinbox.focusOutEvent = functools.partial(self.set_servo_angle, index=i, source=spinbox.focusOutEvent)
            slider.mousePressEvent = functools.partial(self.set_flag, index=i, source=slider.mousePressEvent)
            spinbox.focusInEvent = functools.partial(self.set_flag, index=i, source=spinbox.focusInEvent)

            slider.valueChanged.connect(functools.partial(self.slider_spinbox_related, slave=spinbox, scale=0.1))
            spinbox.valueChanged.connect(functools.partial(self.slider_spinbox_related, slave=slider, scale=10))

            layout.addWidget(label, i, 0)
            layout.addWidget(slider, i, 1)
            layout.addWidget(spinbox, i, 2)

    def set_flag(self, event, index=0, source=None):
        try:
            # with self.flag_lock:
            #     self.joints_flag[index] = True
            source(event)
        except Exception as e:
            print(e)

    def reset_flag(self):
        try:
            with self.flag_lock:
                for i in range(len(self.joints_flag)):
                    self.joints_flag[i] = False
        except Exception as e:
            print(e)

    def update_joints(self, angles):
        for i in range(len(angles)):
            try:
                if self.joints_flag[i] is False and angles[i] is not None and getattr(self, 'spinbox_{}'.format(self.joints[i]['name'])).value() != angles[i]:
                    getattr(self, 'spinbox_{}'.format(self.joints[i]['name'])).setValue(angles[i])
            except Exception as e:
                print(e)

    def set_servo_angle(self, event, index=0, source=None):
        try:
            angle = getattr(self, 'spinbox_{}'.format(self.joints[index]['name'])).value()
            kwargs = {
                'servo_id': index,
                'angle': angle,
                'speed': self.main_ui.spinbox_speed.value(),
                'wait': False
            }
            item = {
                'cmd': 'set_servo_angle',
                'kwargs': kwargs
            }
            self.main_ui.handler.put_cmd_que(item)
            # self.joints_flag[index] = False
            source(event)
        except Exception as e:
            print(e)

    @staticmethod
    def slider_spinbox_related(value, master=None, slave=None, scale=1):
        try:
            slave.setValue(value * scale)
        except Exception as e:
            print(e)

    def set_disable(self, disable):
        try:
            [getattr(self, 'slider_{}'.format(joint['name'])).setDisabled(disable) for joint in self.joints]
            [getattr(self, 'spinbox_{}'.format(joint['name'])).setDisabled(disable) for joint in self.joints]
        except Exception as e:
            print(e)