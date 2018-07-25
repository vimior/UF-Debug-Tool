#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import functools
import threading
from PyQt5.QtCore import Qt
from PyQt5.Qt import QFrame, QGridLayout, QLabel, QSlider, QDoubleSpinBox


class CartesianUI(object):
    def __init__(self, ui, layout):
        self.main_ui = ui
        self.p_layout = layout
        super(CartesianUI, self).__init__()
        self.cartesians = [
            {'name': 'x', 'default': 201.5, 'range': [-900.0, 900.0]},
            {'name': 'y', 'default': 0.0, 'range': [-900.0, 900.0]},
            {'name': 'z', 'default': 140.5, 'range': [-900.0, 900.0]},
            {'name': 'roll', 'default': -180.0, 'range': [-180.0, 180.0]},
            {'name': 'yaw', 'default': 0.0, 'range': [-180.0, 180.0]},
            {'name': 'pitch', 'default': 0.0, 'range': [-180.0, 180.0]},
            {'name': 'radius', 'default': -1.0, 'range': [-1.0, 900.0]},
        ]
        self.flag_lock = threading.Lock()
        self.cartesians_flag = [False] * 7
        self.set_ui()

    def set_ui(self):
        self._set_ui()

    def _set_ui(self):
        frame = QFrame()
        layout = QGridLayout(frame)
        self.p_layout.addWidget(frame)

        for i, cartesian in enumerate(self.cartesians):
            label = QLabel('{}:'.format(cartesian['name']))
            setattr(self, 'slider_{}'.format(cartesian['name']), QSlider(Qt.Horizontal))
            setattr(self, 'spinbox_{}'.format(cartesian['name']), QDoubleSpinBox())
            slider = getattr(self, 'slider_{}'.format(cartesian['name']))
            spinbox = getattr(self, 'spinbox_{}'.format(cartesian['name']))
            slider.setMinimum(cartesian['range'][0] * 10)
            slider.setMaximum(cartesian['range'][1] * 10)
            slider.setValue(cartesian['default'] * 10)
            spinbox.setDecimals(1)
            spinbox.setSingleStep(0.1)
            spinbox.setMinimum(cartesian['range'][0])
            spinbox.setMaximum(cartesian['range'][1])
            spinbox.setValue(cartesian['default'])

            if cartesian['name'] != 'radius':
                slider.mouseReleaseEvent = functools.partial(self.set_position, index=i, source=slider.mouseReleaseEvent)
                spinbox.focusOutEvent = functools.partial(self.set_position, index=i, source=spinbox.focusOutEvent)
                slider.mousePressEvent = functools.partial(self.set_flag, index=i, source=slider.mousePressEvent)
                spinbox.focusInEvent = functools.partial(self.set_flag, index=i, source=spinbox.focusInEvent)

            slider.valueChanged.connect(functools.partial(self.slider_spinbox_related, slave=spinbox, scale=0.1))
            spinbox.valueChanged.connect(functools.partial(self.slider_spinbox_related, slave=slider, scale=10))

            layout.addWidget(label, i, 0)
            layout.addWidget(slider, i, 1)
            layout.addWidget(spinbox, i, 2)

    def set_flag(self, event, index=0, source=None):
        try:
            with self.flag_lock:
                self.cartesians_flag[index] = True
            source(event)
        except Exception as e:
            print(e)

    def reset_flag(self):
        try:
            with self.flag_lock:
                for i in range(len(self.cartesians_flag)):
                    self.cartesians_flag[i] = False
        except Exception as e:
            print(e)

    def update_cartesians(self, cartesians):
        # print(cartesians)
        for i in range(len(cartesians)):
            try:
                if self.cartesians_flag[i] is False and getattr(self, 'spinbox_{}'.format(self.cartesians[i]['name'])).value() != cartesians[i]:
                    getattr(self, 'spinbox_{}'.format(self.cartesians[i]['name'])).setValue(cartesians[i])
            except:
                pass

    def set_position(self, event, index=0, source=None):
        try:
            kwargs = {
                'x': getattr(self, 'spinbox_{}'.format(self.cartesians[0]['name'])).value(),
                'y': getattr(self, 'spinbox_{}'.format(self.cartesians[1]['name'])).value(),
                'z': getattr(self, 'spinbox_{}'.format(self.cartesians[2]['name'])).value(),
                'roll': getattr(self, 'spinbox_{}'.format(self.cartesians[3]['name'])).value(),
                'yaw': getattr(self, 'spinbox_{}'.format(self.cartesians[4]['name'])).value(),
                'pitch': getattr(self, 'spinbox_{}'.format(self.cartesians[5]['name'])).value(),
                'radius': getattr(self, 'spinbox_{}'.format(self.cartesians[6]['name'])).value(),
                'speed': self.main_ui.spinbox_speed.value(),
                'mvacc': self.main_ui.spinbox_acc.value(),
                'is_radian': False,
                'check': True
            }
            if kwargs['radius'] < 0:
                kwargs['radius'] = None
            item = {
                'cmd': 'set_position',
                'kwargs': kwargs
            }
            self.main_ui.handler.put_cmd_que(item)
            # self.cartesians_flag[index] = False
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
            [getattr(self, 'slider_{}'.format(joint['name'])).setDisabled(disable) for joint in self.cartesians]
            [getattr(self, 'spinbox_{}'.format(joint['name'])).setDisabled(disable) for joint in self.cartesians]
        except Exception as e:
            print(e)
