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
from PyQt5.Qt import QFrame, QGridLayout, QSlider, QDoubleSpinBox, QCheckBox, QMessageBox


class JointUI(object):
    def __init__(self, ui, layout):
        self.main_ui = ui
        self.p_layout = layout
        super(JointUI, self).__init__()
        self.joints = [
            {'name': 'axis_1', 'default': 0.0, 'range': [-179.9, 179.9]},
            {'name': 'axis_2', 'default': 0.0, 'range': [-179.9, 179.9]},
            {'name': 'axis_3', 'default': 0.0, 'range': [-179.9, 179.9]},
            {'name': 'axis_4', 'default': 0.0, 'range': [-179.9, 179.9]},
            {'name': 'axis_5', 'default': 0.0, 'range': [-179.9, 179.9]},
            {'name': 'axis_6', 'default': 0.0, 'range': [-179.9, 179.9]},
            {'name': 'axis_7', 'default': 0.0, 'range': [-179.9, 179.9]},
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
            setattr(self, 'checkbox_{}'.format(joint['name']), QCheckBox('Axis-{}'.format(i+1)))
            setattr(self, 'slider_{}'.format(joint['name']), QSlider(Qt.Horizontal))
            setattr(self, 'spinbox_{}'.format(joint['name']), QDoubleSpinBox())
            checkbox = getattr(self, 'checkbox_{}'.format(joint['name']))
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

            checkbox.mouseReleaseEvent = functools.partial(self.set_servo_state, servo_id=i+1, source=checkbox.mouseReleaseEvent)

            # checkbox.stateChanged.connect(functools.partial(self.checkbox_state_changed, servo_id=i+1))
            slider.valueChanged.connect(functools.partial(self.slider_spinbox_related, slave=spinbox, scale=0.1))
            spinbox.valueChanged.connect(functools.partial(self.slider_spinbox_related, slave=slider, scale=10))

            layout.addWidget(checkbox, i, 0)
            layout.addWidget(slider, i, 1)
            layout.addWidget(spinbox, i, 2)

    def set_flag(self, event, index=0, source=None):
        try:
            with self.flag_lock:
                self.joints_flag[index] = True
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
                if self.joints_flag[i] is False and getattr(self, 'spinbox_{}'.format(self.joints[i]['name'])).value() != angles[i]:
                    getattr(self, 'spinbox_{}'.format(self.joints[i]['name'])).setValue(angles[i])
            except Exception as e:
                print(e)

    def brake_changed_callback(self, brakes):
        try:
            [getattr(self, 'checkbox_{}'.format(joint['name'])).setChecked(brakes[i]) for i, joint in enumerate(self.joints)]
        except Exception as e:
            print(e)

    def set_servo_state(self, event, servo_id=1, source=None):
        try:
            checkbox = getattr(self, 'checkbox_{}'.format(self.joints[servo_id - 1]['name']))
            if not checkbox.isChecked():
                # source(event)
                item = {
                    'cmd': 'set_servo_attach',
                    'kwargs': {
                        'servo_id': servo_id
                    }
                }
                self.main_ui.handler.put_cmd_que(item)
                item = {
                    'cmd': 'motion_enable',
                    'kwargs': {
                        'servo_id': servo_id,
                        'enable': True
                    }
                }
                self.main_ui.handler.put_cmd_que(item)
                item = {
                    'cmd': 'set_state',
                    'kwargs': {
                        'state': 0
                    }
                }
                self.main_ui.handler.put_cmd_que(item)
            else:
                tmp = '你确定要解锁电机{}吗？'.format(servo_id)
                if QMessageBox.question(self.main_ui.main_ui.window, '警告', tmp) == QMessageBox.Yes:
                    # source(event)
                    item = {
                        'cmd': 'set_servo_detach',
                        'kwargs': {
                            'servo_id': servo_id
                        }
                    }
                    self.main_ui.handler.put_cmd_que(item)
        except Exception as e:
            print(e)

    def set_servo_angle(self, event, index=0, source=None):
        try:
            angle = [getattr(self, 'spinbox_{}'.format(joint['name'])).value() for joint in self.joints]
            kwargs = {
                'angle': angle,
                'speed': self.main_ui.spinbox_speed.value(),
                'mvacc': self.main_ui.spinbox_acc.value(),
                'is_radian': False,
                'check': True
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
            [getattr(self, 'checkbox_{}'.format(joint['name'])).setDisabled(disable) for i, joint in
             enumerate(self.joints)]
            [getattr(self, 'slider_{}'.format(joint['name'])).setDisabled(disable) for joint in self.joints]
            [getattr(self, 'spinbox_{}'.format(joint['name'])).setDisabled(disable) for joint in self.joints]
        except Exception as e:
            print(e)