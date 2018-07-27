#-*- coding: UTF-8 -*-

from PyQt5.Qt import QHBoxLayout, QGridLayout, \
    QPushButton, QLabel, QSlider, QSpinBox, QDoubleSpinBox, QImage, QPixmap, \
    QFrame, QFileDialog, QTextEdit, QRadioButton
from PyQt5 import QtCore

import os
import sys
import numpy as np
import json
import functools
from .handler import GcodeHandler

icon_path = os.path.join(os.path.split(sys.path[0])[0], 'icon')
if not os.path.exists(icon_path):
    icon_path = os.path.join(os.getcwd(), 'icon')

config_file = './config.json'
init_config = {'zeropoint_height': 0.0}

def read_config():
    error = False
    json_data = init_config
    try:
        with open(config_file, 'r') as f:
            data = f.read()
            json_data = json.loads(data)
    except Exception as e:
        print("load config error: {}".format(e))
        error = True
    if error:
        try:
            with open(config_file, 'w') as f:
                f.write(json.dumps(json_data))
        except Exception as e:
            print('write init config error: {}'.format(e))
    return json_data

def write_config(json_data):
    try:
        with open(config_file, 'w') as f:
            f.write(json.dumps(json_data))
    except Exception as e:
        print('write config error: {}: config: {}'.format(e, json_data))


class GcodeUI(object):
    def __init__(self, ui, layout):
        self.main_ui = ui
        self.layout = layout
        super(GcodeUI, self).__init__()
        self.isOutlineMode = True
        self.isLaserMode = True
        self.handler = GcodeHandler(self)
        self.set_ui()
        self.connect_slot()
        self.gcode = ''

    def set_ui(self):
        self._set_up_frame_ui()
        self._set_middle_frame_ui()
        self._set_down_frame_ui()

    def _set_up_frame_ui(self):
        self.up_frame = QFrame()
        self.up_frame.setMinimumHeight(300)
        self.up_frame.setMaximumHeight(500)
        self.up_layout = QHBoxLayout(self.up_frame)
        up_left_frame = QFrame()
        # up_left_frame.setMinimumWidth(self.main_ui.window.geometry().width() / 2)
        # up_left_frame.setMaximumWidth(self.geometry().width() / 2)
        up_right_frame = QFrame()
        # up_right_frame.setMinimumWidth(self.main_ui.window.geometry().width() / 2)
        # up_right_frame.setMaximumWidth(self.geometry().width() / 2)
        self.up_left_layout = QHBoxLayout(up_left_frame)
        self.up_right_layout = QHBoxLayout(up_right_frame)
        self.up_layout.addWidget(up_left_frame)
        # self.up_layout.addWidget(up_right_frame)
        self.layout.addWidget(self.up_frame)

        self.label_img = QLabel()
        # self.label_img.setMaximumHeight(320)
        # self.label_img.setMaximumWidth(480)
        # self.label_img.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # self.label_img.setScaledContents(True)

        img = QImage()
        if img.load(os.path.join(icon_path, 'tmp.svg')):
            self.label_img.setPixmap(QPixmap.fromImage(img))
            with open(os.path.join(icon_path, 'tmp.svg'), 'rb') as f:
                self.handler.source = f.read()

        self.up_left_layout.addWidget(self.label_img)

        self.label_img_preview = QLabel()
        # self.label_img_preview.setMaximumHeight(320)
        # self.label_img_preview.setMaximumWidth(480)
        self.label_img_preview.setDisabled(True)
        # # self.label_img_preview.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # # self.label_img_preview.setScaledContents(True)
        # data = np.zeros(320 * 240)
        # img = QImage(data, 320, 240, QImage.Format_RGB888)
        # pixmap = QPixmap.fromImage(img)
        # self.label_img_preview.setPixmap(pixmap)
        self.up_right_layout.addWidget(self.label_img_preview)
        # self.up_frame.hide()

    def _set_middle_frame_ui(self):
        middle_frame = QFrame()
        self.middle_layout = QHBoxLayout(middle_frame)
        middle_left_frame = QFrame()
        # middle_left_frame.setMinimumWidth(self.main_ui.window.geometry().width() / 2 - 20)
        middle_right_frame = QFrame()
        # middle_right_frame.setMinimumWidth(self.main_ui.window.geometry().width() / 2 - 20)
        self.middle_left_layout = QGridLayout(middle_left_frame)
        self.middle_right_layout = QGridLayout(middle_right_frame)

        self.middle_layout.addWidget(middle_left_frame)
        self.middle_layout.addWidget(middle_right_frame)
        self.layout.addWidget(middle_frame)

        row = 0
        self.checkbox_outline = QRadioButton('OutLine')
        self.checkbox_gray = QRadioButton('Gray')
        self.checkbox_gray.hide()
        self.btn_load_img = QPushButton('LoadImage')
        self.checkbox_outline.toggle()
        self.isOutlineMode = True
        self.checkbox_outline.setDisabled(True)
        self.middle_left_layout.addWidget(self.checkbox_outline, row, 0)
        self.middle_left_layout.addWidget(self.checkbox_gray, row, 1)
        self.middle_left_layout.addWidget(self.btn_load_img, row, 2)

        row += 1
        label_x_home = QLabel('x_home:')
        self.slider_x_home = QSlider(QtCore.Qt.Horizontal)
        self.slider_x_home.setMinimum(0)
        self.slider_x_home.setMaximum(2000)
        self.slider_x_home.setValue(1500)
        self.spinbox_x_home = QDoubleSpinBox()
        self.spinbox_x_home.setDecimals(1)
        self.spinbox_x_home.setSingleStep(0.1)
        self.spinbox_x_home.setMinimum(0.0)
        self.spinbox_x_home.setMaximum(200.0)
        self.spinbox_x_home.setValue(150.0)
        self.slider_x_home.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                 source=self.slider_x_home.mouseReleaseEvent)
        self.spinbox_x_home.focusOutEvent = functools.partial(self.focusOutEvent,
                                                              source=self.spinbox_x_home.focusOutEvent)
        self.middle_left_layout.addWidget(label_x_home, row, 0)
        self.middle_left_layout.addWidget(self.slider_x_home, row, 1)
        self.middle_left_layout.addWidget(self.spinbox_x_home, row, 2)

        row += 1
        label_y_home = QLabel('y_home:')
        self.slider_y_home = QSlider(QtCore.Qt.Horizontal)
        self.slider_y_home.setMinimum(-1500)
        self.slider_y_home.setMaximum(1500)
        self.slider_y_home.setValue(0)
        self.spinbox_y_home = QDoubleSpinBox()
        self.spinbox_y_home.setDecimals(1)
        self.spinbox_y_home.setSingleStep(0.1)
        self.spinbox_y_home.setMinimum(-150.0)
        self.spinbox_y_home.setMaximum(150.0)
        self.spinbox_y_home.setValue(0.0)
        self.slider_y_home.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                 source=self.slider_y_home.mouseReleaseEvent)
        self.spinbox_y_home.focusOutEvent = functools.partial(self.focusOutEvent,
                                                              source=self.spinbox_y_home.focusOutEvent)
        self.middle_left_layout.addWidget(label_y_home, row, 0)
        self.middle_left_layout.addWidget(self.slider_y_home, row, 1)
        self.middle_left_layout.addWidget(self.spinbox_y_home, row, 2)

        row += 1
        label_z_home = QLabel('z_home:')
        self.slider_z_home = QSlider(QtCore.Qt.Horizontal)
        self.slider_z_home.setMinimum(0)
        self.slider_z_home.setMaximum(1500)
        self.slider_z_home.setValue(900)
        self.spinbox_z_home = QDoubleSpinBox()
        self.spinbox_z_home.setDecimals(1)
        self.spinbox_z_home.setSingleStep(0.1)
        self.spinbox_z_home.setMinimum(0.0)
        self.spinbox_z_home.setMaximum(150.0)
        self.spinbox_z_home.setValue(90.0)
        self.slider_z_home.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                 source=self.slider_z_home.mouseReleaseEvent)
        self.spinbox_z_home.focusOutEvent = functools.partial(self.focusOutEvent,
                                                              source=self.spinbox_z_home.focusOutEvent)
        self.middle_left_layout.addWidget(label_z_home, row, 0)
        self.middle_left_layout.addWidget(self.slider_z_home, row, 1)
        self.middle_left_layout.addWidget(self.spinbox_z_home, row, 2)

        row += 1
        label_x_offset = QLabel('x_offset:')
        self.slider_x_offset = QSlider(QtCore.Qt.Horizontal)
        self.slider_x_offset.setMinimum(-5000)
        self.slider_x_offset.setMaximum(5000)
        self.slider_x_offset.setValue(0)
        self.spinbox_x_offset = QDoubleSpinBox()
        self.spinbox_x_offset.setSingleStep(0.1)
        self.spinbox_x_offset.setDecimals(1)
        self.spinbox_x_offset.setMinimum(-500.0)
        self.spinbox_x_offset.setMaximum(500.0)
        self.spinbox_x_offset.setValue(0.0)
        self.slider_x_offset.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                   source=self.slider_x_offset.mouseReleaseEvent)
        self.spinbox_x_offset.focusOutEvent = functools.partial(self.focusOutEvent,
                                                                source=self.spinbox_x_offset.focusOutEvent)
        self.middle_left_layout.addWidget(label_x_offset, row, 0)
        self.middle_left_layout.addWidget(self.slider_x_offset, row, 1)
        self.middle_left_layout.addWidget(self.spinbox_x_offset, row, 2)

        row += 1
        label_y_offset = QLabel('y_offset:')
        self.slider_y_offset = QSlider(QtCore.Qt.Horizontal)
        self.slider_y_offset.setMinimum(-5000)
        self.slider_y_offset.setMaximum(5000)
        self.slider_y_offset.setValue(0)
        self.spinbox_y_offset = QDoubleSpinBox()
        self.spinbox_y_offset.setDecimals(1)
        self.spinbox_y_offset.setSingleStep(0.1)
        self.spinbox_y_offset.setMinimum(-500.0)
        self.spinbox_y_offset.setMaximum(500.0)
        self.spinbox_y_offset.setValue(0.0)
        self.slider_y_offset.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                   source=self.slider_y_offset.mouseReleaseEvent)
        self.spinbox_y_offset.focusOutEvent = functools.partial(self.focusOutEvent,
                                                                source=self.spinbox_y_offset.focusOutEvent)
        self.middle_left_layout.addWidget(label_y_offset, row, 0)
        self.middle_left_layout.addWidget(self.slider_y_offset, row, 1)
        self.middle_left_layout.addWidget(self.spinbox_y_offset, row, 2)

        row += 1
        label_z_offset = QLabel('z_offset:')
        self.slider_z_offset = QSlider(QtCore.Qt.Horizontal)
        self.slider_z_offset.setMinimum(-1000)
        self.slider_z_offset.setMaximum(1500)
        self.slider_z_offset.setValue(900)
        self.spinbox_z_offset = QDoubleSpinBox()
        self.spinbox_z_offset.setDecimals(1)
        self.spinbox_z_offset.setSingleStep(0.1)
        self.spinbox_z_offset.setMinimum(-100.0)
        self.spinbox_z_offset.setMaximum(150.0)
        self.spinbox_z_offset.setValue(90.0)
        self.slider_z_offset.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                   source=self.slider_z_offset.mouseReleaseEvent)
        self.spinbox_z_offset.focusOutEvent = functools.partial(self.focusOutEvent,
                                                                source=self.spinbox_z_offset.focusOutEvent)
        self.middle_left_layout.addWidget(label_z_offset, row, 0)
        self.middle_left_layout.addWidget(self.slider_z_offset, row, 1)
        self.middle_left_layout.addWidget(self.spinbox_z_offset, row, 2)

        row += 1
        label_pen_up = QLabel('pen_up:')
        self.slider_pen_up = QSlider(QtCore.Qt.Horizontal)
        self.slider_pen_up.setMinimum(0)
        self.slider_pen_up.setMaximum(500)
        self.slider_pen_up.setValue(200)
        self.spinbox_pen_up = QDoubleSpinBox()
        self.spinbox_pen_up.setDecimals(1)
        self.spinbox_pen_up.setSingleStep(0.1)
        self.spinbox_pen_up.setMinimum(0.0)
        self.spinbox_pen_up.setMaximum(50.0)
        self.spinbox_pen_up.setValue(20.0)
        self.slider_pen_up.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                 source=self.slider_pen_up.mouseReleaseEvent)
        self.spinbox_pen_up.focusOutEvent = functools.partial(self.focusOutEvent,
                                                              source=self.spinbox_pen_up.focusOutEvent)
        self.slider_pen_up.setDisabled(True)
        self.spinbox_pen_up.setDisabled(True)
        self.middle_left_layout.addWidget(label_pen_up, row, 0)
        self.middle_left_layout.addWidget(self.slider_pen_up, row, 1)
        self.middle_left_layout.addWidget(self.spinbox_pen_up, row, 2)

        row = 0
        self.checkbox_laser = QRadioButton('Laser')
        self.checkbox_pen = QRadioButton('Pen')
        self.checkbox_laser.toggle()
        self.isLaserMode = True
        self.middle_right_layout.addWidget(self.checkbox_laser, row, 0)
        self.middle_right_layout.addWidget(self.checkbox_pen, row, 1)

        row += 1
        label_drawing_feedrate = QLabel('drawing_feedrate:')
        self.slider_drawing_feedrate = QSlider(QtCore.Qt.Horizontal)
        self.slider_drawing_feedrate.setMinimum(5)
        self.slider_drawing_feedrate.setMaximum(1000)
        self.slider_drawing_feedrate.setValue(100)
        self.spinbox_drawing_feedrate = QSpinBox()
        self.spinbox_drawing_feedrate.setMinimum(5)
        self.spinbox_drawing_feedrate.setMaximum(1000)
        self.spinbox_drawing_feedrate.setValue(100)
        self.slider_drawing_feedrate.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                           source=self.slider_drawing_feedrate.mouseReleaseEvent)
        self.spinbox_drawing_feedrate.focusOutEvent = functools.partial(self.focusOutEvent,
                                                                        source=self.spinbox_drawing_feedrate.focusOutEvent)
        self.middle_right_layout.addWidget(label_drawing_feedrate, row, 0)
        self.middle_right_layout.addWidget(self.slider_drawing_feedrate, row, 1)
        self.middle_right_layout.addWidget(self.spinbox_drawing_feedrate, row, 2)

        row += 1
        label_moving_feedrate = QLabel('moving_feedrate:')
        self.slider_moving_feedrate = QSlider(QtCore.Qt.Horizontal)
        self.slider_moving_feedrate.setMinimum(5)
        self.slider_moving_feedrate.setMaximum(20000)
        self.slider_moving_feedrate.setValue(100)
        self.spinbox_moving_feedrate = QSpinBox()
        self.spinbox_moving_feedrate.setMinimum(5)
        self.spinbox_moving_feedrate.setMaximum(20000)
        self.spinbox_moving_feedrate.setValue(100)
        self.slider_moving_feedrate.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                          source=self.slider_moving_feedrate.mouseReleaseEvent)
        self.spinbox_moving_feedrate.focusOutEvent = functools.partial(self.focusOutEvent,
                                                                       source=self.spinbox_moving_feedrate.focusOutEvent)
        self.middle_right_layout.addWidget(label_moving_feedrate, row, 0)
        self.middle_right_layout.addWidget(self.slider_moving_feedrate, row, 1)
        self.middle_right_layout.addWidget(self.spinbox_moving_feedrate, row, 2)

        row += 1
        label_scale = QLabel('scale:')
        self.slider_scale = QSlider(QtCore.Qt.Horizontal)
        self.slider_scale.setMinimum(1)
        self.slider_scale.setMaximum(100)
        self.slider_scale.setValue(10)
        self.spinbox_scale = QDoubleSpinBox()
        self.spinbox_scale.setDecimals(1)
        self.spinbox_scale.setSingleStep(0.1)
        self.spinbox_scale.setMinimum(0.1)
        self.spinbox_scale.setMaximum(10.0)
        self.spinbox_scale.setValue(1.0)
        # self.slider_scale.setDisabled(True)
        # self.spinbox_scale.setDisabled(True)
        self.slider_scale.mouseReleaseEvent = functools.partial(self.mouseReleaseEvent,
                                                                source=self.slider_scale.mouseReleaseEvent)
        self.spinbox_scale.focusOutEvent = functools.partial(self.focusOutEvent,
                                                             source=self.spinbox_scale.focusOutEvent)

        self.middle_right_layout.addWidget(label_scale, row, 0)
        self.middle_right_layout.addWidget(self.slider_scale, row, 1)
        self.middle_right_layout.addWidget(self.spinbox_scale, row, 2)

        row += 1
        label_resolution = QLabel('resolution:')
        self.slider_resolution = QSlider(QtCore.Qt.Horizontal)
        self.slider_resolution.setMinimum(1)
        self.slider_resolution.setMaximum(100)
        self.slider_resolution.setValue(10)
        self.spinbox_resolution = QDoubleSpinBox()
        self.spinbox_resolution.setMinimum(0.1)
        self.spinbox_resolution.setMaximum(10.0)
        self.spinbox_resolution.setSingleStep(0.1)
        self.spinbox_resolution.setDecimals(1)
        self.spinbox_resolution.setValue(1.0)
        self.slider_resolution.setDisabled(True)
        self.spinbox_resolution.setDisabled(True)
        self.middle_right_layout.addWidget(label_resolution, row, 0)
        self.middle_right_layout.addWidget(self.slider_resolution, row, 1)
        self.middle_right_layout.addWidget(self.spinbox_resolution, row, 2)

        row += 1
        self.btn_generate_gcode = QPushButton('Generate_Gcode')
        self.middle_right_layout.addWidget(self.btn_generate_gcode, row, 0)

        row += 1
        self.label_x_min = QLabel('')
        self.label_x_max = QLabel('')
        self.middle_right_layout.addWidget(self.label_x_min, row, 0)
        self.middle_right_layout.addWidget(self.label_x_max, row, 1)

        row += 1
        self.label_y_min = QLabel('')
        self.label_y_max = QLabel('')
        self.middle_right_layout.addWidget(self.label_y_min, row, 0)
        self.middle_right_layout.addWidget(self.label_y_max, row, 1)

    def _set_down_frame_ui(self):
        self.down_frame = QFrame()
        self.down_layout = QHBoxLayout(self.down_frame)
        self.layout.addWidget(self.down_frame)

        self.textEdit = QTextEdit()
        self.down_layout.addWidget(self.textEdit)
        # self.down_frame.hide()

    def select_engrave_mode(self, event):
        self.isOutlineMode = event
        # print('outline: {}, laser: {}'.format(self.isOutlineMode, self.isLaserMode))

    def select_end_type(self, event):
        self.isLaserMode = event
        self.slider_pen_up.setDisabled(self.isLaserMode)
        self.spinbox_pen_up.setDisabled(self.isLaserMode)
        self.generate_gcode()
        # print('outline: {}, laser: {}'.format(self.isOutlineMode, self.isLaserMode))

    def connect_slot(self):
        self.checkbox_outline.toggled.connect(self.select_engrave_mode)
        self.checkbox_laser.toggled.connect(self.select_end_type)
        self.btn_load_img.clicked.connect(self.load_image)

        self.slider_x_home.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_x_home, scale=.1))
        self.spinbox_x_home.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_x_home, scale=10))

        self.slider_y_home.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_y_home, scale=.1))
        self.spinbox_y_home.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_y_home, scale=10))

        self.slider_z_home.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_z_home, scale=.1))
        self.spinbox_z_home.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_z_home, scale=10))

        self.slider_x_offset.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_x_offset, scale=.1))
        self.spinbox_x_offset.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_x_offset, scale=10))

        self.slider_y_offset.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_y_offset, scale=.1))
        self.spinbox_y_offset.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_y_offset, scale=10))

        self.slider_z_offset.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_z_offset, scale=.1))
        self.spinbox_z_offset.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_z_offset, scale=10))

        self.slider_pen_up.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_pen_up, scale=.1))
        self.spinbox_pen_up.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_pen_up, scale=10))

        self.slider_scale.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_scale, scale=.1))
        self.spinbox_scale.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_scale, scale=10))

        self.slider_resolution.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_resolution, scale=.1))
        self.spinbox_resolution.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_resolution, scale=10))

        self.slider_drawing_feedrate.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_drawing_feedrate, scale=1))
        self.spinbox_drawing_feedrate.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_drawing_feedrate, scale=1))

        self.slider_moving_feedrate.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.spinbox_moving_feedrate, scale=1))
        self.spinbox_moving_feedrate.valueChanged.connect(
            functools.partial(self.slider_spinbox_related, slave=self.slider_moving_feedrate, scale=1))

        self.btn_generate_gcode.clicked.connect(functools.partial(self.generate_gcode, flag=True))

    def slider_spinbox_related(self, value, master=None, slave=None, scale=1):
        try:
            slave.setValue(value * scale)
        except Exception as e:
            print(e)

    def mouseReleaseEvent(self, event, source=None):
        try:
            self.generate_gcode()
        except Exception as e:
            print(e)
        source(event)

    def focusOutEvent(self, event, source=None):
        try:
            self.generate_gcode()
        except Exception as e:
            print(e)
        source(event)

    def generate_gcode(self, flag=False):
        if self.handler.template is None and flag:
            self.handler.svg_to_gcode()
        if self.handler.template:
            pen_up = self.spinbox_pen_up.value() if not self.isLaserMode else 0
            config = {
                'x_home': self.spinbox_x_home.value(),
                'y_home': self.spinbox_y_home.value(),
                'z_home': self.spinbox_z_home.value(),
                'z_offset': self.spinbox_z_offset.value(),
                'pen_up': pen_up,
                'z_offset_pen_up': self.spinbox_z_offset.value() + pen_up,
                'moving_feedrate': self.spinbox_moving_feedrate.value(),
                'drawing_feedrate': self.spinbox_drawing_feedrate.value(),
            }
            self.gcode = self.handler.template.format(**config)
            self.change_gcode()
            # self.textEdit.setText(self.gcode)

    def change_gcode(self):
        if self.gcode:
            x_offset = self.spinbox_x_offset.value()
            y_offset = self.spinbox_y_offset.value()
            z_offset = self.spinbox_z_offset.value()
            moving_feedrate = self.spinbox_moving_feedrate.value()
            drawing_feedrate = self.spinbox_drawing_feedrate.value()
            scale = self.spinbox_scale.value()

            lines = self.gcode.split('\n')
            for i, line in enumerate(lines):
                List = line.strip().split(' ')
                line = ''
                for l in List:
                    if l.startswith('F'):
                        if line.startswith(('G01', 'G1')):
                            l = 'F{}'.format(drawing_feedrate)
                        elif line.startswith(('G00', 'G0')):
                            l = 'F{}'.format(moving_feedrate)
                    elif l.startswith('X'):
                        x = float(l[1:]) * scale + x_offset
                        l = 'X{0:.2f}'.format(x)
                    elif l.startswith('Y'):
                        y = float(l[1:]) * scale + y_offset
                        l = 'Y{0:.2f}'.format(y)
                    # elif l.startswith('Z'):
                    #     z = float(l[1:]) + z_offset
                    #     l = 'Z{0:.2f}'.format(z)
                    line += l + ' '
                line = line.strip()
                lines[i] = line
            self.calc_gcode(lines)
            gcode = '\n'.join(lines)
            self.textEdit.setText(gcode)

    def calc_gcode(self, lines):
        x_list = []
        y_list = []
        for i, line in enumerate(lines):
            if line.startswith(tuple(['G0', 'G1', 'G00', 'G01'])):
                List = line.strip().split(' ')
                for l in List:
                    if l.startswith('X'):
                        x = float(l[1:])
                        x_list.append(x)
                    elif l.startswith('Y'):
                        y = float(l[1:])
                        y_list.append(y)
        if len(x_list) > 0:
            x_min = np.min(x_list)
            x_max = np.max(x_list)
            self.label_x_min.setText('X(min): ' + str(x_min))
            self.label_x_max.setText('X(max): ' + str(x_max))
            # print('x_min: {}, x_max: {}, x_distance: {}'.format(x_min, x_max, x_max - x_min))
        if len(y_list) > 0:
            y_min = np.min(y_list)
            y_max = np.max(y_list)
            self.label_y_min.setText('Y(min): ' + str(y_min))
            self.label_y_max.setText('Y(max): ' + str(y_max))
            # print('y_min: {}, y_max: {}, y_distance: {}'.format(y_min, y_max, y_max - y_min))

    def load_image(self):
        fname = QFileDialog.getOpenFileName(self.main_ui.window, 'Open file', '', '*.svg')
        if fname and fname[0]:
            img = QImage()
            if img.load(fname[0]):
                self.label_img.setPixmap(QPixmap.fromImage(img))
                with open(fname[0], 'rb') as f:
                    self.handler.source = f.read()
                    self.handler.template = None
                    self.gcode = None
                    self.up_frame.show()
