# !/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>


import time
from PyQt5.QtCore import QThread, pyqtSignal
from .openmv import OpenMV
import sys
sys.path.append('..')
from log import logger


class FrameThread(QThread):
    signal = pyqtSignal(tuple)

    def __init__(self, owner):
        self.owner = owner
        super(FrameThread, self).__init__()

    def run(self):
        while self.owner.openmv and self.owner.openmv.connected and self.owner.openmv.running:
            try:
                if self.owner.openmv.enable_fb:
                    fb_data = self.owner.openmv.get_fb_data()
                    if fb_data:
                        self.signal.emit(fb_data)
                time.sleep(0.05)
            except:
                pass


class OutputThread(QThread):
    signal = pyqtSignal(str)
    TERMINATOR = b'\r\n'
    ENCODING = 'utf-8'
    UNICODE_HANDLING = 'replace'

    def __init__(self, owner):
        self.owner = owner
        self.buffer = bytearray()
        super(OutputThread, self).__init__()

    def run(self):
        while self.owner.openmv and self.owner.openmv.connected and self.owner.openmv.running:
            try:
                data = self.owner.openmv.get_output_data()
                if data:
                    self.buffer.extend(data)
                    while self.TERMINATOR in self.buffer:
                        packet, self.buffer = self.buffer.split(self.TERMINATOR, 1)
                        buf = packet.decode(self.ENCODING, self.UNICODE_HANDLING)
                        self.signal.emit(buf)
                time.sleep(0.05)
            except:
                pass


class OpenMVHandler(object):
    def __init__(self, ui):
        self.ui = ui
        super(OpenMVHandler, self).__init__()
        self.connected = False
        self.openmv = None
        self.output_thread = None
        self.fb_thread = None

    def init(self):
        self.connected = False
        self.openmv = None
        self.output_thread = None
        self.fb_thread = None

    def connect(self):
        if self.openmv is None or not self.openmv.connected:
            logger.debug('try to connect')
            try:
                self.openmv = OpenMV()
                self.openmv.connect()
                if self.openmv.connected:
                    self.ui.btn_connect.setText('DisConnect')
                    self.ui.set_disable(False)
                    logger.info('Connect OpenMV success from {}'.format(self.openmv.port))
                    logger.info('Firmware Version: {}'.format(self.openmv.fw_version))
                    if self.openmv.running:
                        self.ui.btn_run_openmv.setText('Stop')
                        self.fb_thread = FrameThread(self)
                        self.fb_thread.signal.connect(self.update_fb)
                        self.fb_thread.start()
                        self.output_thread = OutputThread(self)
                        self.output_thread.signal.connect(self.log_output)
                        self.output_thread.start()
                    return True
                else:
                    self.ui.btn_connect.setText('Connect')
                    self.openmv = None
                    logger.error('connect failed')
                    return False
            except Exception as e:
                self.ui.btn_connect.setText('Connect')
                self.openmv = None
                logger.error('connect failed: {}'.format(e))
                return False
        else:
            logger.warn('openmv is connected')
            return True

    def disconnect(self):
        if self.openmv and self.openmv.connected:
            logger.error('Disconnect OpenMV from {}'.format(self.openmv.port))
            self.openmv.disconnect()
        self.init()
        self.ui.set_disable(True)
        self.ui.btn_connect.setText('Connect')
        self.ui.btn_connect.setDisabled(False)

    def update_fb(self, fb_data):
        self.ui.set_pixmap(fb_data)

    def log_output(self, data):
        logger.debug(data)
        if not self.openmv or not self.openmv.running:
            self.ui.btn_run_openmv.setText('Run')
            self.ui.btn_enable_fb.setText('FB-Disable')

    def enable_fb_event(self, enable):
        if self.openmv and self.openmv.connected:
            if self.openmv.set_enable_fb(enable):
                if enable:
                    self.ui.btn_enable_fb.setText('FB-Disable')
                else:
                    self.ui.btn_enable_fb.setText('FB-Enable')
                return True
            else:
                return False
        else:
            return False

    def reset_openmv_event(self):
        if self.openmv and self.openmv.connected:
            if self.openmv.reset():
                self.openmv = None
                self.ui.set_disable(True)
                self.ui.btn_connect.setText('Connect')
                return True
            else:
                return False
        else:
            return False

    def run_script_event(self):
        if self.openmv and self.openmv.connected:
            self.openmv.stop_script()
            buf = self.ui.textEdit.toPlainText().encode('utf-8')
            if buf and self.openmv.exec_script(buf):
                self.fb_thread = FrameThread(self)
                self.fb_thread.signal.connect(self.update_fb)
                self.fb_thread.start()
                self.output_thread = OutputThread(self)
                self.output_thread.signal.connect(self.log_output)
                self.output_thread.start()
                self.ui.btn_run_openmv.setText('Stop')
                return True
            else:
                return False
        else:
            return False

    def stop_script_event(self):
        if self.openmv and self.openmv.connected:
            if self.openmv.running:
                if self.openmv.stop_script():
                    self.ui.btn_enable_fb.setText('FB-Disable')
                    self.ui.btn_run_openmv.setText('Stop')
                    return True
                else:
                    return False
            else:
                self.ui.btn_enable_fb.setText('FB-Disable')
                self.ui.btn_run_openmv.setText('Stop')
        else:
            self.ui.btn_enable_fb.setText('FB-Disable')
            self.ui.btn_run_openmv.setText('Stop')
            return False
