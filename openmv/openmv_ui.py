# !/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

from PyQt5.Qt import QTextEdit, QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QImage, QPixmap, QSizePolicy
from PyQt5 import QtCore
import numpy as np
import threading
from .handler import OpenMVHandler
import sys
sys.path.append('..')
from log import logger


class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.setAcceptDrops(True)
        self._filename = None

    def dropEvent(self, event):
        tmp = event.mimeData().text().split('///')
        if tmp and len(tmp) >= 2:
            self._filename = tmp[1]
            with open(self._filename, 'r') as f:
                self.setText(f.read())

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, name):
        self._filename = name


class OpenMV_UI(object):
    def __init__(self, ui, layout):
        self.main_ui = ui
        self.layout = layout
        super(OpenMV_UI, self).__init__()
        self.set_ui()
        self.set_disable(True)
        self.openmv_handler = OpenMVHandler(self)

    def set_ui(self):
        self._set_left_ui()
        self._set_right_ui()

    def _set_left_ui(self):
        left_frame = QFrame()
        self.left_layout = QVBoxLayout(left_frame)
        self.layout.addWidget(left_frame)

        self.label_title = QLabel('untitled')
        self.textEdit = TextEdit()
        self.textEdit.dropEvent = self.dropEvent
        self.textEdit.setDisabled(False)
        self.main_ui.window.setAcceptDrops(True)
        self.left_layout.addWidget(self.label_title)
        self.left_layout.addWidget(self.textEdit)

    def dropEvent(self, event):
        tmp = event.mimeData().text().split('///')
        if tmp and len(tmp) >= 2:
            self.textEdit.filename = tmp[1]
            with open(self.textEdit.filename, 'r') as f:
                self.textEdit.setText(f.read())
            self.label_title.setText(self.textEdit.filename)

    def _set_right_ui(self):
        right_frame = QFrame()
        right_frame.setMinimumWidth(330)
        self.right_layout = QVBoxLayout(right_frame)
        self.layout.addWidget(right_frame)

        img_frame = QFrame()
        img_frame.setMaximumHeight(250)
        img_layout = QVBoxLayout(img_frame)
        self.right_layout.addWidget(img_frame)

        self.label_img = QLabel()
        self.label_img.setAlignment(QtCore.Qt.AlignRight)
        self.label_img.setAlignment(QtCore.Qt.AlignTop)
        self.label_img.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.label_img.setScaledContents(True)
        data = np.zeros(320 * 240)
        img = QImage(data, 320, 240, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.label_img.setPixmap(pixmap)
        img_layout.addWidget(self.label_img)

        ctrl_frame = QFrame()
        ctrl_layout = QGridLayout(ctrl_frame)
        self.right_layout.addWidget(ctrl_frame)

        self.btn_connect = QPushButton('Connect')
        self.btn_enable_fb = QPushButton('FB-Disable')
        self.btn_reset_openmv = QPushButton('Reset')
        self.btn_run_openmv = QPushButton('Run')
        ctrl_layout.addWidget(self.btn_connect, 0, 0)
        ctrl_layout.addWidget(self.btn_enable_fb, 1, 0)
        ctrl_layout.addWidget(self.btn_reset_openmv, 2, 0)
        ctrl_layout.addWidget(self.btn_run_openmv, 3, 0)
        self.btn_connect.clicked.connect(self.connect_openmv)
        self.btn_enable_fb.clicked.connect(self.enable_fb)
        self.btn_reset_openmv.clicked.connect(self.reset_openmv)
        self.btn_run_openmv.clicked.connect(self.run_openmv)

    def set_disable(self, state):
        self.btn_enable_fb.setDisabled(state)
        self.btn_reset_openmv.setDisabled(state)
        self.btn_run_openmv.setDisabled(state)

        if state:
            self.btn_enable_fb.setText('Fb-Disable')
            self.btn_reset_openmv.setText('Reset')
            self.btn_run_openmv.setText('Run')

    def set_pixmap(self, fb_data):
        img = QImage(fb_data[2].data, fb_data[0], fb_data[1], QImage.Format_RGB888)
        img.ndarray = fb_data[2]
        pixmap = QPixmap.fromImage(img)
        self.label_img.setPixmap(pixmap)

    def connect_openmv(self):
        if self.btn_connect.text() == 'Connect':
            self.openmv_handler.connect()
        else:
            self.openmv_handler.disconnect()

    def enable_fb(self):
        if self.btn_enable_fb.text() == 'FB-Enable':
            self.openmv_handler.enable_fb_event(True)
        else:
            self.openmv_handler.enable_fb_event(False)

    def reset_openmv(self):
        self.openmv_handler.reset_openmv_event()

    def run_openmv(self):
        if self.btn_run_openmv.text() == 'Run':
            self.openmv_handler.run_script_event()
        else:
            self.openmv_handler.stop_script_event()





